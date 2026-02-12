#!/usr/bin/env python3
"""
Sistema de Pagos CNI - Backend Flask
Consejo Nacional de Inversiones - Honduras

Desarrollado por: Ing. Luis Martínez
Software Developer | luismartinez.94mc@gmail.com
Versión 2.0.0 - 11 de Febrero 2026
Estado: Producción
"""
import os, sqlite3, smtplib, json
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_file
from fpdf import FPDF
from fpdf.enums import XPos, YPos
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "rrhh_cni.db")
REPORTES_DIR = os.path.join(BASE_DIR, "reportes_pagos_RRHH")
MESES = ["Enero","Febrero","Marzo","Abril","Mayo","Junio",
         "Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"]

app = Flask(__name__)

# ── DB helpers ──────────────────────────────────────────────────
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS empleados (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cod_empleado TEXT UNIQUE NOT NULL,
        nombre_empleado TEXT NOT NULL, cargo TEXT NOT NULL,
        salario_mensual REAL NOT NULL, ihss REAL DEFAULT 0,
        isr REAL DEFAULT 0, otro REAL DEFAULT 0,
        observacion_otro TEXT DEFAULT '', correo_institucional TEXT DEFAULT ''
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS smtp_config (
        id INTEGER PRIMARY KEY CHECK (id=1),
        servidor TEXT DEFAULT 'smtp.office365.com', puerto INTEGER DEFAULT 587,
        usuario TEXT DEFAULT '', contrasena TEXT DEFAULT '',
        emisor TEXT DEFAULT 'Servicios Online', remitente_display TEXT DEFAULT ''
    )''')
    c.execute("INSERT OR IGNORE INTO smtp_config (id) VALUES (1)")
    c.execute('''CREATE TABLE IF NOT EXISTS historico_pagos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        empleado_id INTEGER, cod_empleado TEXT, nombre_empleado TEXT,
        cargo TEXT, fecha_inicio TEXT, fecha_fin TEXT,
        periodo_key TEXT UNIQUE, salario REAL, ihss REAL, isr REAL,
        otro REAL, observacion_otro TEXT DEFAULT '',
        total_deducciones REAL, salario_neto REAL,
        tipo TEXT DEFAULT 'PDF', fecha_generacion TEXT, ruta_pdf TEXT DEFAULT ''
    )''')
    # ── Tabla ISR tramos progresivos ──
    c.execute('''CREATE TABLE IF NOT EXISTS isr_tramos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tasa REAL NOT NULL,
        desde_mensual REAL NOT NULL,
        hasta_mensual REAL NOT NULL,
        descripcion TEXT DEFAULT ''
    )''')
    # Insertar tramos por defecto 2026 si la tabla esta vacia
    if c.execute("SELECT COUNT(*) FROM isr_tramos").fetchone()[0] == 0:
        tramos_2026 = [
            (0.0,   0.01,     22360.36, "Exentos"),
            (15.0,  22360.37, 32346.18, "15%"),
            (20.0,  32346.19, 70805.06, "20%"),
            (25.0,  70805.07, 99999999.99, "25%"),
        ]
        c.executemany("INSERT INTO isr_tramos (tasa, desde_mensual, hasta_mensual, descripcion) VALUES (?,?,?,?)", tramos_2026)

    # Migraciones
    cols = {r[1] for r in c.execute("PRAGMA table_info(empleados)").fetchall()}
    if "ivm1" in cols and "ihss" not in cols:
        c.execute("ALTER TABLE empleados ADD COLUMN ihss REAL DEFAULT 0")
        c.execute("UPDATE empleados SET ihss = ivm1 + em")
    for col in ["ihss","otro","observacion_otro"]:
        if col not in cols:
            default = "0" if col != "observacion_otro" else "''"
            try: c.execute(f"ALTER TABLE empleados ADD COLUMN {col} REAL DEFAULT {default}" if col != "observacion_otro" else f"ALTER TABLE empleados ADD COLUMN {col} TEXT DEFAULT {default}")
            except: pass
    for col, dflt in [("emisor","'Servicios Online'"),("remitente_display","''")]:
        try: c.execute(f"ALTER TABLE smtp_config ADD COLUMN {col} TEXT DEFAULT {dflt}")
        except: pass
    
    # ── Tabla IHSS Configuracion ──
    c.execute('''CREATE TABLE IF NOT EXISTS ihss_config (
        id INTEGER PRIMARY KEY CHECK (id=1),
        tasa_em REAL DEFAULT 2.5,
        tasa_ivm REAL DEFAULT 2.5,
        techo_mensual REAL DEFAULT 12000.00
    )''')
    c.execute("INSERT OR IGNORE INTO ihss_config (id, tasa_em, tasa_ivm, techo_mensual) VALUES (1, 2.5, 2.5, 12000.00)")
    
    conn.commit(); conn.close()

def fmt(a): return f"L. {a:,.2f}"

def row_to_dict(r):
    return dict(r) if r else None

# ── Calculo ISR Progresivo ──────────────────────────────────────
def _calcular_isr(salario, db=None):
    """Calcula ISR mensual con tabla progresiva de tramos."""
    close_db = False
    if db is None:
        db = get_db()
        close_db = True
    tramos = [dict(r) for r in db.execute("SELECT * FROM isr_tramos ORDER BY desde_mensual ASC").fetchall()]
    if close_db:
        db.close()
    if not tramos:
        return 0.0
    isr_total = 0.0
    for t in tramos:
        tasa = t["tasa"] / 100.0
        desde = t["desde_mensual"]
        hasta = t["hasta_mensual"]
        if salario < desde:
            break
        gravable = min(salario, hasta) - desde + 0.01
        if gravable > 0:
            isr_total += gravable * tasa
    return round(isr_total, 2)

# ── Calculo IHSS ────────────────────────────────────────────────
def _calcular_ihss(salario, db=None):
    """
    Calcula IHSS mensual del empleado con base en configuracion.
    IHSS = Salario Base × (Tasa EM + Tasa IVM) / 100
    donde Salario Base = min(Salario Real, Techo de Cotización)
    """
    close_db = False
    if db is None:
        db = get_db()
        close_db = True
    
    config = db.execute("SELECT * FROM ihss_config WHERE id=1").fetchone()
    if close_db:
        db.close()
    
    if not config:
        # Valores por defecto 2026
        tasa_em = 2.5
        tasa_ivm = 2.5
        techo = 12000.00
    else:
        tasa_em = config["tasa_em"]
        tasa_ivm = config["tasa_ivm"]
        techo = config["techo_mensual"]
    
    # Calcular IHSS
    salario_base = min(salario, techo)
    ihss_total = salario_base * (tasa_em + tasa_ivm) / 100.0
    return round(ihss_total, 2)

def _recalcular_isr_todos(db):
    """Recalcula ISR de todos los empleados con la tabla actual."""
    emps = db.execute("SELECT id, salario_mensual FROM empleados").fetchall()
    for e in emps:
        nuevo_isr = _calcular_isr(e["salario_mensual"], db)
        db.execute("UPDATE empleados SET isr=? WHERE id=?", (nuevo_isr, e["id"]))

def _recalcular_ihss_todos(db):
    """Recalcula IHSS de todos los empleados con la configuración actual."""
    emps = db.execute("SELECT id, salario_mensual FROM empleados").fetchall()
    for e in emps:
        nuevo_ihss = _calcular_ihss(e["salario_mensual"], db)
        db.execute("UPDATE empleados SET ihss=? WHERE id=?", (nuevo_ihss, e["id"]))
    db.commit()

# ── ROUTES: Pages ───────────────────────────────────────────────
@app.route("/")
def index():
    return render_template("index.html")

# ── API: Empleados ──────────────────────────────────────────────
@app.route("/api/empleados")
def api_empleados():
    db = get_db()
    q = request.args.get("q","").strip()
    if q:
        t = f"%{q}%"
        rows = db.execute("SELECT * FROM empleados WHERE nombre_empleado LIKE ? OR cod_empleado LIKE ? OR cargo LIKE ? ORDER BY nombre_empleado",(t,t,t)).fetchall()
    else:
        rows = db.execute("SELECT * FROM empleados ORDER BY nombre_empleado").fetchall()
    db.close()
    return jsonify([dict(r) for r in rows])

@app.route("/api/empleados/<int:eid>")
def api_empleado(eid):
    db = get_db()
    r = db.execute("SELECT * FROM empleados WHERE id=?",(eid,)).fetchone()
    db.close()
    return jsonify(dict(r)) if r else ("",404)

@app.route("/api/empleados", methods=["POST"])
def api_add_empleado():
    d = request.json
    try:
        db = get_db()
        sal = float(d["salario_mensual"])
        isr_auto = _calcular_isr(sal, db)
        ihss_auto = _calcular_ihss(sal, db)
        db.execute("INSERT INTO empleados (cod_empleado,nombre_empleado,cargo,salario_mensual,ihss,isr,otro,observacion_otro,correo_institucional) VALUES (?,?,?,?,?,?,?,?,?)",
            (d["cod_empleado"],d["nombre_empleado"],d["cargo"],sal,
             ihss_auto,isr_auto,float(d.get("otro",0)),
             d.get("observacion_otro",""),d.get("correo_institucional","")))
        db.commit(); db.close()
        return jsonify({"ok":True,"isr_calculado":isr_auto,"ihss_calculado":ihss_auto})
    except sqlite3.IntegrityError:
        return jsonify({"ok":False,"error":f"Codigo '{d['cod_empleado']}' ya existe."}),400
    except Exception as e:
        return jsonify({"ok":False,"error":str(e)}),400

@app.route("/api/empleados/<int:eid>", methods=["PUT"])
def api_update_empleado(eid):
    d = request.json
    try:
        db = get_db()
        sal = float(d["salario_mensual"])
        isr_auto = _calcular_isr(sal, db)
        ihss_auto = _calcular_ihss(sal, db)
        db.execute("UPDATE empleados SET cod_empleado=?,nombre_empleado=?,cargo=?,salario_mensual=?,ihss=?,isr=?,otro=?,observacion_otro=?,correo_institucional=? WHERE id=?",
            (d["cod_empleado"],d["nombre_empleado"],d["cargo"],sal,
             ihss_auto,isr_auto,float(d.get("otro",0)),
             d.get("observacion_otro",""),d.get("correo_institucional",""),eid))
        db.commit(); db.close()
        return jsonify({"ok":True,"isr_calculado":isr_auto,"ihss_calculado":ihss_auto})
    except Exception as e:
        return jsonify({"ok":False,"error":str(e)}),400

@app.route("/api/empleados/<int:eid>", methods=["DELETE"])
def api_delete_empleado(eid):
    db = get_db()
    db.execute("DELETE FROM empleados WHERE id=?",(eid,))
    db.commit(); db.close()
    return jsonify({"ok":True})

@app.route("/api/stats")
def api_stats():
    db = get_db()
    r = db.execute("SELECT COUNT(*) as total, COALESCE(SUM(salario_mensual),0) as planilla, COALESCE(AVG(salario_mensual),0) as promedio FROM empleados").fetchone()
    db.close()
    return jsonify(dict(r))

@app.route("/api/next_cod")
def api_next_cod():
    db = get_db()
    # Buscamos el número más alto en los códigos que sigan el patrón CNIxxx
    row = db.execute("SELECT cod_empleado FROM empleados WHERE cod_empleado LIKE 'CNI%' ORDER BY cod_empleado DESC LIMIT 1").fetchone()
    db.close()
    
    next_num = 1
    if row:
        cod = row['cod_empleado']
        try:
            # Extraemos la parte numérica (asumiendo formato CNI001)
            num_str = ''.join(filter(str.isdigit, cod))
            if num_str:
                next_num = int(num_str) + 1
        except:
            pass
            
    return jsonify({"next_cod": f"CNI{next_num:03d}"})

# ── API: Boleta / PDF / Email ───────────────────────────────────
@app.route("/api/boleta/pdf", methods=["POST"])
def api_boleta_pdf():
    d = request.json
    db = get_db()
    emp = db.execute("SELECT * FROM empleados WHERE id=?",(d["id"],)).fetchone()
    if not emp: return jsonify({"ok":False,"error":"Empleado no encontrado"}),404
    emp = dict(emp)
    try:
        ruta = _generar_pdf(emp, d["fi"], d["ff"])
        _registrar_pago(db, emp, d["fi"], d["ff"], "PDF", ruta)
        db.close()
        return jsonify({"ok":True,"ruta":ruta})
    except Exception as e:
        db.close()
        return jsonify({"ok":False,"error":str(e)}),500

@app.route("/api/boleta/email", methods=["POST"])
def api_boleta_email():
    d = request.json
    db = get_db()
    emp = dict(db.execute("SELECT * FROM empleados WHERE id=?",(d["id"],)).fetchone())
    smtp = dict(db.execute("SELECT * FROM smtp_config WHERE id=1").fetchone())
    try:
        ruta = _generar_pdf(emp, d["fi"], d["ff"])
        _enviar_email(smtp, emp, d["fi"], d["ff"], ruta)
        _registrar_pago(db, emp, d["fi"], d["ff"], "Email", ruta)
        db.close()
        return jsonify({"ok":True,"correo":emp["correo_institucional"]})
    except Exception as e:
        db.close()
        return jsonify({"ok":False,"error":str(e)}),500

@app.route("/api/boleta/both", methods=["POST"])
def api_boleta_both():
    d = request.json
    db = get_db()
    emp = dict(db.execute("SELECT * FROM empleados WHERE id=?",(d["id"],)).fetchone())
    smtp = dict(db.execute("SELECT * FROM smtp_config WHERE id=1").fetchone())
    try:
        ruta = _generar_pdf(emp, d["fi"], d["ff"])
        _enviar_email(smtp, emp, d["fi"], d["ff"], ruta)
        _registrar_pago(db, emp, d["fi"], d["ff"], "PDF+Email", ruta)
        db.close()
        return jsonify({"ok":True,"ruta":ruta,"correo":emp["correo_institucional"]})
    except Exception as e:
        db.close()
        return jsonify({"ok":False,"error":str(e)}),500

# ── API: Boleta BATCH (todos) ────────────────────────────────────
@app.route("/api/boleta/batch", methods=["POST"])
def api_boleta_batch():
    d = request.json
    fi, ff = d["fi"], d["ff"]
    modo = d.get("modo", "pdf")  # pdf | email | both
    db = get_db()
    emps = [dict(r) for r in db.execute("SELECT * FROM empleados ORDER BY nombre_empleado").fetchall()]
    smtp = dict(db.execute("SELECT * FROM smtp_config WHERE id=1").fetchone()) if modo in ("email","both") else None
    resultados = []
    for emp in emps:
        try:
            ruta = _generar_pdf(emp, fi, ff)
            if modo in ("email", "both"):
                _enviar_email(smtp, emp, fi, ff, ruta)
            tipo = {"pdf":"PDF","email":"Email","both":"PDF+Email"}[modo]
            _registrar_pago(db, emp, fi, ff, tipo, ruta)
            resultados.append({"cod": emp["cod_empleado"], "nombre": emp["nombre_empleado"], "ok": True})
        except Exception as e:
            resultados.append({"cod": emp["cod_empleado"], "nombre": emp["nombre_empleado"], "ok": False, "error": str(e)})
    db.close()
    ok_count = sum(1 for r in resultados if r["ok"])
    fail_count = sum(1 for r in resultados if not r["ok"])
    return jsonify({"ok": True, "total": len(emps), "exitosos": ok_count, "fallidos": fail_count, "detalle": resultados})

# ── API: Historico ──────────────────────────────────────────────
@app.route("/api/historico")
def api_historico():
    db = get_db()
    q = "SELECT * FROM historico_pagos WHERE 1=1"
    params = []
    emp = request.args.get("emp","").strip()
    fi = request.args.get("fi","").strip()
    ff = request.args.get("ff","").strip()
    if emp:
        q += " AND (cod_empleado LIKE ? OR nombre_empleado LIKE ?)"
        params += [f"%{emp}%", f"%{emp}%"]
    if fi: q += " AND fecha_fin >= ?"; params.append(fi)
    if ff: q += " AND fecha_fin <= ?"; params.append(ff)
    q += " ORDER BY id DESC"
    rows = db.execute(q, params).fetchall()
    db.close()
    data = [dict(r) for r in rows]
    total_neto = sum(r["salario_neto"] for r in data)
    total_ded = sum(r["total_deducciones"] for r in data)
    return jsonify({"rows":data,"stats":{"total":len(data),"neto":total_neto,"deducciones":total_ded}})

@app.route("/api/historico/exportar", methods=["POST"])
def api_historico_exportar():
    d = request.json
    db = get_db()
    rows = db.execute("SELECT * FROM historico_pagos ORDER BY id DESC").fetchall()
    db.close()
    data = [dict(r) for r in rows]
    try:
        ruta = _generar_auditoria(data, d.get("filtro",""))
        return jsonify({"ok":True,"ruta":ruta})
    except Exception as e:
        return jsonify({"ok":False,"error":str(e)}),500

# ── API: ISR Tramos ─────────────────────────────────────────────
@app.route("/api/isr/tramos")
def api_isr_tramos():
    db = get_db()
    rows = [dict(r) for r in db.execute("SELECT * FROM isr_tramos ORDER BY desde_mensual ASC").fetchall()]
    db.close()
    return jsonify(rows)

@app.route("/api/isr/tramos", methods=["POST"])
def api_isr_tramos_save():
    """Reemplaza todos los tramos con los nuevos."""
    tramos = request.json.get("tramos", [])
    if not tramos:
        return jsonify({"ok": False, "error": "Debe haber al menos un tramo."}), 400
    db = get_db()
    db.execute("DELETE FROM isr_tramos")
    for t in tramos:
        db.execute("INSERT INTO isr_tramos (tasa, desde_mensual, hasta_mensual, descripcion) VALUES (?,?,?,?)",
            (float(t["tasa"]), float(t["desde_mensual"]), float(t["hasta_mensual"]), t.get("descripcion", "")))
    # Recalcular ISR de todos los empleados
    _recalcular_isr_todos(db)
    db.close()
    return jsonify({"ok": True})

@app.route("/api/isr/calcular")
def api_isr_calcular():
    """Calcula ISR para un salario dado (preview)."""
    sal = float(request.args.get("salario", 0))
    isr = _calcular_isr(sal)
    return jsonify({"salario": sal, "isr": isr})

@app.route("/api/isr/recalcular", methods=["POST"])
def api_isr_recalcular():
    """Recalcula ISR de todos los empleados con la tabla actual."""
    db = get_db()
    _recalcular_isr_todos(db)
    db.commit()
    db.close()
    return jsonify({"ok": True})

@app.route("/api/ihss/recalcular", methods=["POST"])
def api_ihss_recalcular():
    """Recalcula IHSS de todos los empleados con la configuración actual."""
    db = get_db()
    _recalcular_ihss_todos(db)
    db.commit()
    db.close()
    return jsonify({"ok": True})

# ── API: SMTP Config ────────────────────────────────────────────
@app.route("/api/smtp")
def api_smtp():
    db = get_db()
    r = dict(db.execute("SELECT * FROM smtp_config WHERE id=1").fetchone())
    db.close()
    r.pop("contrasena", None)  # no enviar password al frontend
    return jsonify(r)

@app.route("/api/smtp", methods=["POST"])
def api_smtp_save():
    d = request.json
    db = get_db()
    db.execute("UPDATE smtp_config SET servidor=?,puerto=?,usuario=?,contrasena=?,emisor=?,remitente_display=? WHERE id=1",
        (d["servidor"],int(d.get("puerto",587)),d["usuario"],d["contrasena"],
         d.get("emisor","Servicios Online"),d.get("remitente_display","")))
    db.commit(); db.close()
    return jsonify({"ok":True})

# ── API: IHSS Config ─────────────────────────────────────────────
@app.route("/api/ihss")
def api_ihss_get():
    db = get_db()
    row = db.execute("SELECT * FROM ihss_config WHERE id=1").fetchone()
    db.close()
    if row:
        return jsonify(dict(row))
    else:
        return jsonify({"tasa_em": 2.5, "tasa_ivm": 2.5, "techo_mensual": 12000.00})

@app.route("/api/ihss", methods=["POST"])
def api_ihss_save():
    d = request.json
    db = get_db()
    db.execute("UPDATE ihss_config SET tasa_em=?, tasa_ivm=?, techo_mensual=? WHERE id=1",
               (d["tasa_em"], d["tasa_ivm"], d["techo_mensual"]))
    db.commit(); db.close()
    return jsonify({"ok": True})

# ── API: ISR Config ─────────────────────────────────────────────
@app.route("/api/calcular_isr")
def api_calcular_isr():
    """Calcula ISR mensual usando la tabla de tramos configurada."""
    salario = float(request.args.get("salario", 0))
    if salario <= 0: return jsonify({"isr_mensual": 0})
    
    db = get_db()
    isr_mensual = _calcular_isr(salario, db)
    db.close()
    
    return jsonify({"isr_mensual": isr_mensual})

# ── Logica: PDF ─────────────────────────────────────────────────
class BoletaPDF(FPDF):
    def header(self):
        self.set_fill_color(37,99,235); self.rect(0,0,210,36,"F")
        self.set_font("Helvetica","B",18); self.set_text_color(255,255,255)
        self.set_y(8); self.cell(0,10,"BOLETA DE PAGO",align="C",new_x=XPos.LMARGIN,new_y=YPos.NEXT)
        self.set_font("Helvetica","",9); self.set_text_color(219,234,254)
        self.cell(0,6,"Sistema de Recursos Humanos",align="C",new_x=XPos.LMARGIN,new_y=YPos.NEXT)
        self.ln(10)
    def footer(self):
        self.set_y(-15); self.set_font("Helvetica","I",7); self.set_text_color(148,163,184)
        self.cell(0,8,f"Generado: {datetime.now().strftime('%d/%m/%Y %H:%M')}  |  Pagina {self.page_no()}",align="C")
    def section(self, text, r, g, b):
        self.set_font("Helvetica","B",10); self.set_fill_color(r,g,b); self.set_text_color(30,41,59)
        self.cell(0,8,f"   {text}",fill=True,new_x=XPos.LMARGIN,new_y=YPos.NEXT); self.ln(3)
    def row(self, label, value, bold=False, color=None):
        f="B" if bold else ""
        self.set_font("Helvetica",f,9); self.set_text_color(71,85,105)
        self.cell(125,7,f"   {label}")
        if color: self.set_text_color(*color)
        self.set_font("Helvetica","B" if bold else "",9)
        self.cell(0,7,value,align="R",new_x=XPos.LMARGIN,new_y=YPos.NEXT)
        self.set_text_color(71,85,105)

def _generar_pdf(emp, fi, ff):
    n,cod,cargo = emp["nombre_empleado"],emp["cod_empleado"],emp["cargo"]
    sal = emp["salario_mensual"]
    ihss,isr,otro = float(emp.get("ihss",0) or 0),float(emp.get("isr",0) or 0),float(emp.get("otro",0) or 0)
    obs = emp.get("observacion_otro","") or ""
    td=ihss+isr+otro; neto=sal-td
    fecha_fin = datetime.strptime(ff,"%d/%m/%Y")
    mes=MESES[fecha_fin.month-1]; anio=fecha_fin.year
    carpeta=os.path.join(REPORTES_DIR,f"{cod}_{n.replace(' ','_')}")
    os.makedirs(carpeta,exist_ok=True)
    ruta=os.path.join(carpeta,f"Boleta_{mes}_{anio}.pdf")
    pdf=BoletaPDF(); pdf.add_page()
    pdf.section("DATOS DEL EMPLEADO",241,245,249)
    for l,v in [("Codigo:",cod),("Nombre:",n),("Cargo:",cargo),("Periodo:",f"{fi} al {ff}")]:
        pdf.set_font("Helvetica","B",9); pdf.cell(45,7,f"   {l}")
        pdf.set_font("Helvetica","",9); pdf.cell(0,7,v,new_x=XPos.LMARGIN,new_y=YPos.NEXT)
    pdf.ln(4)
    pdf.section("INGRESOS",209,250,229)
    pdf.row("Salario Mensual",fmt(sal),color=(5,150,105))
    pdf.set_draw_color(226,232,240); pdf.line(15,pdf.get_y()+1,195,pdf.get_y()+1); pdf.ln(2)
    pdf.row("Total Ingresos",fmt(sal),bold=True,color=(5,150,105)); pdf.ln(4)
    pdf.section("DEDUCCIONES",254,226,226)
    pdf.row("IHSS (Seguro Social)",fmt(ihss),color=(220,38,38))
    pdf.row("ISR (Impuesto Sobre la Renta)",fmt(isr),color=(220,38,38))
    if otro>0:
        pdf.row(f"Otro ({obs})" if obs else "Otra Deduccion",fmt(otro),color=(220,38,38))
    pdf.set_draw_color(226,232,240); pdf.line(15,pdf.get_y()+2,195,pdf.get_y()+2); pdf.ln(3)
    pdf.row("Total Deducciones",fmt(td),bold=True,color=(220,38,38)); pdf.ln(8)
    pdf.set_font("Helvetica","B",13); pdf.set_fill_color(37,99,235); pdf.set_text_color(255,255,255)
    pdf.cell(125,13,"   SALARIO NETO",fill=True)
    pdf.cell(0,13,f"{fmt(neto)}   ",fill=True,align="R",new_x=XPos.LMARGIN,new_y=YPos.NEXT)
    pdf.output(ruta)
    return ruta

def _generar_auditoria(rows, filtro=""):
    carpeta=os.path.join(REPORTES_DIR,"_auditorias"); os.makedirs(carpeta,exist_ok=True)
    ruta=os.path.join(carpeta,f"Auditoria_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")
    pdf=FPDF(); pdf.add_page("L"); pdf.set_auto_page_break(True,20)
    pdf.set_fill_color(37,99,235); pdf.rect(0,0,297,24,"F")
    pdf.set_font("Helvetica","B",14); pdf.set_text_color(255,255,255); pdf.set_y(5)
    pdf.cell(0,10,"REPORTE DE AUDITORIA — HISTORICO DE PAGOS",align="C",new_x=XPos.LMARGIN,new_y=YPos.NEXT)
    pdf.ln(6)
    cols=[("Fecha",26),("Cod",20),("Empleado",50),("Cargo",38),("Periodo",40),
          ("Salario",26),("IHSS",20),("ISR",20),("Otro",20),("Deducc.",26),("Neto",26),("Tipo",15)]
    pdf.set_font("Helvetica","B",7); pdf.set_fill_color(37,99,235); pdf.set_text_color(255,255,255)
    for t,w in cols: pdf.cell(w,7,t,fill=True,align="C")
    pdf.ln()
    pdf.set_font("Helvetica","",7)
    for i,r in enumerate(rows):
        bg=(248,250,252) if i%2==0 else (255,255,255); pdf.set_fill_color(*bg); pdf.set_text_color(30,41,59)
        data=[r.get("fecha_generacion",""),r["cod_empleado"],r["nombre_empleado"][:24],
              r["cargo"][:18],f"{r['fecha_inicio']}-{r['fecha_fin']}",
              fmt(r["salario"]),fmt(r["ihss"]),fmt(r["isr"]),fmt(r["otro"]),
              fmt(r["total_deducciones"]),fmt(r["salario_neto"]),r["tipo"]]
        for j,(t,w) in enumerate(cols):
            a="C" if j in(0,1,4,11) else "L" if j in(2,3) else "R"
            pdf.cell(w,6,data[j],fill=True,align=a)
        pdf.ln()
    pdf.output(ruta); return ruta

# ── Logica: Email ───────────────────────────────────────────────
def _enviar_email(smtp_cfg, emp, fi, ff, ruta_pdf):
    srv,port = smtp_cfg["servidor"],smtp_cfg["puerto"]
    usr,pwd = smtp_cfg["usuario"],smtp_cfg["contrasena"]
    if not srv or not usr or not pwd: raise ValueError("Configure SMTP primero.")
    dest = emp["correo_institucional"]
    if not dest: raise ValueError(f"{emp['nombre_empleado']} no tiene correo.")
    sal=emp["salario_mensual"]; ihss=float(emp.get("ihss",0) or 0)
    isr=float(emp.get("isr",0) or 0); otro=float(emp.get("otro",0) or 0)
    obs=emp.get("observacion_otro","") or ""; td=ihss+isr+otro; neto=sal-td
    otro_row=""
    if otro>0:
        lbl=f"Otro ({obs})" if obs else "Otra Deduccion"
        otro_row=f'<tr style="background:#f8fafb"><td style="padding:10px 16px;border-bottom:1px solid #e2e8f0;color:#475569">{lbl}</td><td style="padding:10px 16px;text-align:right;color:#dc2626;font-weight:600;border-bottom:1px solid #e2e8f0">-{fmt(otro)}</td></tr>'
    
    # HTML moderno con colores institucionales CNI
    html=f'''<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"></head>
<body style="margin:0;padding:20px;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,'Helvetica Neue',Arial,sans-serif;background:#f1f5f9">
<div style="max-width:600px;margin:0 auto;background:#ffffff;border-radius:16px;overflow:hidden;box-shadow:0 4px 6px rgba(0,0,0,0.07)">
  <!-- Header CNI -->
  <div style="background:linear-gradient(135deg,#233981 0%,#1a2a63 100%);padding:32px 24px;text-align:center;position:relative">
    <div style="display:inline-block;background:#ffffff;width:56px;height:56px;border-radius:12px;margin-bottom:12px;display:flex;align-items:center;justify-content:center">
      <div style="width:48px;height:48px;background:#233981;border-radius:10px"></div>
    </div>
    <h1 style="margin:0;color:#ffffff;font-size:28px;font-weight:700;letter-spacing:-0.5px">Boleta de Pago</h1>
    <p style="margin:8px 0 0;color:#2AAAD6;font-size:13px;font-weight:600;letter-spacing:0.5px">CONSEJO NACIONAL DE INVERSIONES</p>
  </div>
  
  <!-- Body -->
  <div style="padding:32px 24px">
    <div style="background:#f8fafc;border-left:4px solid #2AAAD6;padding:16px 20px;border-radius:8px;margin-bottom:24px">
      <p style="margin:0;font-size:15px;color:#475569">Estimado/a <strong style="color:#233981">{emp["nombre_empleado"]}</strong>,</p>
      <p style="margin:8px 0 0;font-size:13px;color:#64748b">Boleta correspondiente al periodo del <strong>{fi}</strong> al <strong>{ff}</strong></p>
    </div>
    
    <!-- Tabla de conceptos -->
    <table style="width:100%;border-collapse:separate;border-spacing:0;font-size:14px;border-radius:12px;overflow:hidden;border:1px solid #e2e8f0">
      <thead>
        <tr style="background:linear-gradient(135deg,#233981 0%,#1a2a63 100%);color:#ffffff">
          <th style="padding:14px 16px;text-align:left;font-weight:600;font-size:12px;letter-spacing:0.5px;text-transform:uppercase">Concepto</th>
          <th style="padding:14px 16px;text-align:right;font-weight:600;font-size:12px;letter-spacing:0.5px;text-transform:uppercase">Monto</th>
        </tr>
      </thead>
      <tbody>
        <!-- Salario -->
        <tr style="background:linear-gradient(to right,#f0fdf9,#f0fdf4)">
          <td style="padding:14px 16px;border-bottom:1px solid #e2e8f0">
            <strong style="color:#1BAE64;font-size:15px">💰 Salario Mensual</strong>
          </td>
          <td style="padding:14px 16px;text-align:right;border-bottom:1px solid #e2e8f0">
            <strong style="color:#1BAE64;font-size:16px">{fmt(sal)}</strong>
          </td>
        </tr>
        
        <!-- Deducciones -->
        <tr style="background:#ffffff">
          <td colspan="2" style="padding:12px 16px;background:#f8fafb;border-bottom:1px solid #e2e8f0">
            <strong style="color:#64748b;font-size:11px;text-transform:uppercase;letter-spacing:0.5px">⚡ Deducciones</strong>
          </td>
        </tr>
        <tr style="background:#ffffff">
          <td style="padding:10px 16px;padding-left:32px;border-bottom:1px solid #e2e8f0;color:#475569">IHSS</td>
          <td style="padding:10px 16px;text-align:right;color:#dc2626;font-weight:600;border-bottom:1px solid #e2e8f0">-{fmt(ihss)}</td>
        </tr>
        <tr style="background:#f8fafb">
          <td style="padding:10px 16px;padding-left:32px;border-bottom:1px solid #e2e8f0;color:#475569">ISR</td>
          <td style="padding:10px 16px;text-align:right;color:#dc2626;font-weight:600;border-bottom:1px solid #e2e8f0">-{fmt(isr)}</td>
        </tr>
        {otro_row}
        
        <!-- Total Deducciones -->
        <tr style="background:#fef2f2">
          <td style="padding:12px 16px;border-bottom:2px solid #e2e8f0">
            <strong style="color:#dc2626">Total Deducciones</strong>
          </td>
          <td style="padding:12px 16px;text-align:right;border-bottom:2px solid #e2e8f0">
            <strong style="color:#dc2626;font-size:15px">-{fmt(td)}</strong>
          </td>
        </tr>
        
        <!-- Salario Neto -->
        <tr style="background:linear-gradient(135deg,#2AAAD6 0%,#0891b2 100%)">
          <td style="padding:18px 16px">
            <strong style="color:#ffffff;font-size:16px;letter-spacing:0.5px">💵 SALARIO NETO</strong>
          </td>
          <td style="padding:18px 16px;text-align:right">
            <strong style="color:#ffffff;font-size:20px;letter-spacing:-0.5px">{fmt(neto)}</strong>
          </td>
        </tr>
      </tbody>
    </table>
    
    <!-- Footer note -->
    <div style="margin-top:24px;padding:16px;background:#f8fafc;border-radius:8px;border:1px dashed #cbd5e1">
      <p style="margin:0;font-size:12px;color:#64748b;text-align:center">
        📎 Esta boleta ha sido generada automáticamente por el <strong>Sistema de Pagos CNI</strong>
      </p>
    </div>
  </div>
  
  <!-- Footer -->
  <div style="background:#f8fafc;padding:20px 24px;text-align:center;border-top:1px solid #e2e8f0">
    <p style="margin:0;font-size:11px;color:#94a3b8">© 2026 CNI Honduras • Sistema de Recursos Humanos</p>
    <p style="margin:4px 0 0;font-size:10px;color:#cbd5e1">Consejo Nacional de Inversiones</p>
  </div>
</div>
</body>
</html>'''
    remitente = smtp_cfg.get("remitente_display","") or usr
    msg=MIMEMultipart(); msg["From"]=remitente; msg["To"]=dest
    msg["Subject"]=f"Boleta de Pago - {fi} al {ff}"; msg.attach(MIMEText(html,"html"))
    if ruta_pdf and os.path.exists(ruta_pdf):
        with open(ruta_pdf,"rb") as f:
            adj=MIMEBase("application","pdf"); adj.set_payload(f.read())
            encoders.encode_base64(adj)
            adj.add_header("Content-Disposition",f"attachment; filename={os.path.basename(ruta_pdf)}")
            msg.attach(adj)
    ehlo_domain = usr.split("@")[-1] if "@" in usr else "localhost"
    if port==465:
        server=smtplib.SMTP_SSL(srv,port,timeout=30); server.ehlo(ehlo_domain)
    else:
        server=smtplib.SMTP(srv,port,timeout=30); server.ehlo(ehlo_domain)
        server.starttls(); server.ehlo(ehlo_domain)
    server.login(usr,pwd); server.sendmail(usr,dest,msg.as_string()); server.quit()

def _registrar_pago(db, emp, fi, ff, tipo, ruta):
    sal=emp["salario_mensual"]; ihss=float(emp.get("ihss",0) or 0)
    isr=float(emp.get("isr",0) or 0); otro=float(emp.get("otro",0) or 0)
    obs=emp.get("observacion_otro","") or ""; td=ihss+isr+otro; neto=sal-td
    dt=datetime.strptime(ff,"%d/%m/%Y"); pk=f"{emp['cod_empleado']}_{dt.month:02d}_{dt.year}"
    ahora=datetime.now().strftime("%d/%m/%Y %H:%M")
    existe=db.execute("SELECT id FROM historico_pagos WHERE periodo_key=?",(pk,)).fetchone()
    if existe:
        db.execute("UPDATE historico_pagos SET nombre_empleado=?,cargo=?,fecha_inicio=?,fecha_fin=?,salario=?,ihss=?,isr=?,otro=?,observacion_otro=?,total_deducciones=?,salario_neto=?,tipo=?,fecha_generacion=?,ruta_pdf=? WHERE periodo_key=?",
            (emp["nombre_empleado"],emp["cargo"],fi,ff,sal,ihss,isr,otro,obs,td,neto,tipo,ahora,ruta,pk))
    else:
        db.execute("INSERT INTO historico_pagos (empleado_id,cod_empleado,nombre_empleado,cargo,fecha_inicio,fecha_fin,periodo_key,salario,ihss,isr,otro,observacion_otro,total_deducciones,salario_neto,tipo,fecha_generacion,ruta_pdf) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (emp["id"],emp["cod_empleado"],emp["nombre_empleado"],emp["cargo"],fi,ff,pk,sal,ihss,isr,otro,obs,td,neto,tipo,ahora,ruta))
    db.commit()

init_db()

if __name__ == "__main__":
    app.run(debug=True, port=5000)
