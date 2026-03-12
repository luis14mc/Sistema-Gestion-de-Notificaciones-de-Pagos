#!/usr/bin/env python3
"""
Sistema de Pagos CNI - Backend Flask
Consejo Nacional de Inversiones - Honduras

Desarrollado por: Ing. Luis Martínez
Software Developer | luismartinez.94mc@gmail.com
Versión 2.2.0 - 12 de Marzo 2026
Estado: Producción
"""
import os, sqlite3, smtplib, json, calendar
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
    # ── Tabla ISR tramos progresivos (rangos ANUALES) ──
    c.execute('''CREATE TABLE IF NOT EXISTS isr_tramos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tasa REAL NOT NULL,
        desde_anual REAL NOT NULL,
        hasta_anual REAL NOT NULL,
        descripcion TEXT DEFAULT ''
    )''')
    # Migrar desde_mensual/hasta_mensual si existen (compatibilidad)
    cols_isr = {r[1] for r in c.execute("PRAGMA table_info(isr_tramos)").fetchall()}
    if "desde_mensual" in cols_isr and "desde_anual" not in cols_isr:
        c.execute("ALTER TABLE isr_tramos ADD COLUMN desde_anual REAL")
        c.execute("ALTER TABLE isr_tramos ADD COLUMN hasta_anual REAL")
        c.execute("UPDATE isr_tramos SET desde_anual = desde_mensual * 12, hasta_anual = hasta_mensual * 12")
    # Tabla config deducciones ISR (gastos medicos + deducible IVM)
    c.execute('''CREATE TABLE IF NOT EXISTS isr_config (
        id INTEGER PRIMARY KEY CHECK (id=1),
        gastos_medicos_anual REAL DEFAULT 40000.00,
        deducible_ivm_mensual REAL DEFAULT 297.58
    )''')
    cols_isr_cfg = {r[1] for r in c.execute("PRAGMA table_info(isr_config)").fetchall()}
    if "gastos_medicos_anual" not in cols_isr_cfg:
        c.execute("DROP TABLE IF EXISTS isr_config")
        c.execute('''CREATE TABLE isr_config (
            id INTEGER PRIMARY KEY CHECK (id=1),
            gastos_medicos_anual REAL DEFAULT 40000.00,
            deducible_ivm_mensual REAL DEFAULT 297.58
        )''')
        c.execute("INSERT INTO isr_config (id, gastos_medicos_anual, deducible_ivm_mensual) VALUES (1, 40000.00, 297.58)")
    else:
        c.execute("INSERT OR IGNORE INTO isr_config (id, gastos_medicos_anual, deducible_ivm_mensual) VALUES (1, 40000.00, 297.58)")
    # Tabla progresiva oficial 2026 (Renta Neta Gravable anual) - Referencia SH
    tramos_oficial_2026 = [
        (0.0,   0.01,      228324.32, "Exentos"),
        (15.0,  228324.33, 348154.10, "15%"),
        (20.0,  348154.11, 809660.75, "20%"),
        (25.0,  809660.76, 999999999.99, "25%"),
    ]
    if c.execute("SELECT COUNT(*) FROM isr_tramos").fetchone()[0] == 0:
        c.executemany("INSERT INTO isr_tramos (tasa, desde_anual, hasta_anual, descripcion) VALUES (?,?,?,?)", tramos_oficial_2026)

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
    if "fecha_ingreso" not in cols:
        try: c.execute("ALTER TABLE empleados ADD COLUMN fecha_ingreso TEXT DEFAULT NULL")
        except: pass
    
    # ── Tabla IHSS Configuracion (EM + IVM) ──
    c.execute('''CREATE TABLE IF NOT EXISTS ihss_config (
        id INTEGER PRIMARY KEY CHECK (id=1),
        tasa_em REAL DEFAULT 2.5,
        tasa_ivm REAL DEFAULT 2.5,
        techo_mensual REAL DEFAULT 12000.00
    )''')
    cols_ihss = {r[1] for r in c.execute("PRAGMA table_info(ihss_config)").fetchall()}
    if "tasa_ivm" not in cols_ihss:
        c.execute("ALTER TABLE ihss_config ADD COLUMN tasa_ivm REAL DEFAULT 2.5")
        c.execute("UPDATE ihss_config SET tasa_ivm = 2.5 WHERE tasa_ivm IS NULL")
    c.execute("INSERT OR IGNORE INTO ihss_config (id, tasa_em, tasa_ivm, techo_mensual) VALUES (1, 2.5, 2.5, 12000.00)")
    
    conn.commit(); conn.close()

def fmt(a): return f"L. {a:,.2f}"

def row_to_dict(r):
    return dict(r) if r else None

def _parse_fecha_ingreso(fecha_ingreso):
    """Parsea fecha_ingreso a (anio, mes, dia). Retorna None si invalida."""
    if not fecha_ingreso or not str(fecha_ingreso).strip():
        return None
    s = str(fecha_ingreso).strip()
    try:
        if "-" in s and len(s) >= 10:  # YYYY-MM-DD
            partes = s.split("-")
            if len(partes) >= 3:
                return (int(partes[0]), int(partes[1]), int(partes[2]))
        if "/" in s:
            partes = s.split("/")
            if len(partes) >= 3:
                return (int(partes[2]), int(partes[1]), int(partes[0]))
    except (ValueError, IndexError):
        pass
    return None

def _dias_trabajados_en_mes(dia_ingreso, anio, mes):
    """Dias trabajados desde dia_ingreso hasta fin de mes."""
    _, ultimo = calendar.monthrange(anio, mes)
    return max(0, ultimo - dia_ingreso + 1)

def _es_primer_mes_empleado(fecha_ingreso, anio_periodo, mes_periodo):
    """True si el periodo (anio, mes) es el mes de ingreso del empleado."""
    p = _parse_fecha_ingreso(fecha_ingreso)
    if not p:
        return False
    anio_ing, mes_ing, _ = p
    return anio_ing == anio_periodo and mes_ing == mes_periodo

def _salario_prorrateado_primer_mes(salario_base, fecha_ingreso, anio_periodo, mes_periodo):
    """
    Salario del primer mes prorrateado por dias trabajados.
    sueldo_dias = salario_base/30; Sueldo_mes_primero = sueldo_dias * cantidad_dias
    Si no es primer mes, retorna salario_base completo.
    """
    if not _es_primer_mes_empleado(fecha_ingreso, anio_periodo, mes_periodo):
        return salario_base
    p = _parse_fecha_ingreso(fecha_ingreso)
    if not p:
        return salario_base
    _, _, dia_ing = p
    dias = _dias_trabajados_en_mes(dia_ing, anio_periodo, mes_periodo)
    sueldo_dias = salario_base / 30.0
    return round(sueldo_dias * dias, 2)

def _meses_trabajados_en_anio(fecha_ingreso, anio):
    """
    Calcula cuantos meses trabajara el empleado en el anio dado segun su fecha de ingreso.
    Si ingreso en febrero, trabaja feb-dic = 11 meses.
    Retorna 12 si no hay fecha_ingreso o si ingreso antes de ese anio.
    """
    if not fecha_ingreso or not str(fecha_ingreso).strip():
        return 12
    s = str(fecha_ingreso).strip()
    try:
        if "-" in s and len(s) >= 7:
            partes = s.split("-")
            if len(partes) >= 2:
                anio_ing = int(partes[0])
                mes_ing = int(partes[1])
                if anio_ing > anio:
                    return 0
                if anio_ing < anio:
                    return 12
                return 12 - mes_ing + 1
        if "/" in s:
            partes = s.split("/")
            if len(partes) >= 3:
                dia, mes_ing, anio_ing = int(partes[0]), int(partes[1]), int(partes[2])
                if anio_ing > anio:
                    return 0
                if anio_ing < anio:
                    return 12
                return 12 - mes_ing + 1
    except (ValueError, IndexError):
        pass
    return 12

# ── Calculo ISR Progresivo (Anual con deducciones) ───────────────
def _calcular_isr(salario, db=None, meses_trabajados=12, salario_periodo_actual=None):
    """
    Calcula ISR mensual segun formula Honduras.
    Si salario_periodo_actual se pasa (prorrateado primer mes), se usa para Ingreso_Anual.
    Deducciones: gastos_medicos prorrateado por meses + deducible_ivm * meses_trabajados.
    """
    close_db = False
    if db is None:
        db = get_db()
        close_db = True

    # Config deducciones
    cfg = db.execute("SELECT * FROM isr_config WHERE id=1").fetchone()
    if cfg:
        gastos_medicos = float(cfg["gastos_medicos_anual"] or 40000)
        deducible_ivm = float(cfg["deducible_ivm_mensual"] or 297.58)
    else:
        gastos_medicos = 40000.0
        deducible_ivm = 297.58

    # Ingreso anual: si hay salario_periodo_actual (prorrateado), es primer mes
    if salario_periodo_actual is not None and meses_trabajados > 0:
        ingreso_anual = salario_periodo_actual + salario * (meses_trabajados - 1)
    else:
        ingreso_anual = salario * meses_trabajados

    # Deducciones: gastos_medicos fijo anual prorrateado por meses + deducible_ivm * meses
    deducciones_anual = (gastos_medicos * meses_trabajados / 12.0) + (deducible_ivm * meses_trabajados)
    renta_neta_gravable = max(0.0, ingreso_anual - deducciones_anual)

    # Tabla progresiva anual
    cols = {r[1] for r in db.execute("PRAGMA table_info(isr_tramos)").fetchall()}
    order_col = "desde_anual" if "desde_anual" in cols else "desde_mensual"
    tramos = [dict(r) for r in db.execute(f"SELECT * FROM isr_tramos ORDER BY {order_col} ASC").fetchall()]
    if close_db:
        db.close()

    if not tramos:
        return 0.0

    # Usar desde_anual/hasta_anual o convertir desde mensual
    def get_desde(t):
        if "desde_anual" in t and t["desde_anual"] is not None:
            return float(t["desde_anual"])
        return float(t.get("desde_mensual", 0)) * 12

    def get_hasta(t):
        if "hasta_anual" in t and t["hasta_anual"] is not None:
            return float(t["hasta_anual"])
        return float(t.get("hasta_mensual", 0)) * 12

    isr_anual = 0.0
    for t in tramos:
        tasa = float(t["tasa"]) / 100.0
        desde = get_desde(t)
        hasta = get_hasta(t)
        if renta_neta_gravable < desde:
            break
        gravable = min(renta_neta_gravable, hasta) - desde + 0.01
        if gravable > 0:
            isr_anual += gravable * tasa

    isr_mensual = isr_anual / meses_trabajados if meses_trabajados > 0 else 0
    return round(isr_mensual, 2)

# ── Calculo IHSS ────────────────────────────────────────────────
def _calcular_ihss(salario, db=None, salario_periodo_actual=None):
    """
    Calcula IHSS mensual del empleado (EM + IVM).
    IHSS = Salario Base × (Tasa EM + Tasa IVM) / 100
    Si salario_periodo_actual se pasa (prorrateado primer mes), se usa en lugar de salario.
    """
    close_db = False
    if db is None:
        db = get_db()
        close_db = True
    
    config = db.execute("SELECT * FROM ihss_config WHERE id=1").fetchone()
    if close_db:
        db.close()
    
    if not config:
        tasa_em = 2.5
        tasa_ivm = 2.5
        techo = 12000.00
    else:
        cfg = dict(config)
        tasa_em = cfg.get("tasa_em") or 2.5
        tasa_ivm = cfg.get("tasa_ivm") or 2.5
        techo = cfg.get("techo_mensual") or 12000.00
    
    sal_efectivo = salario_periodo_actual if salario_periodo_actual is not None else salario
    salario_base = min(sal_efectivo, techo)
    tasa_total = tasa_em + tasa_ivm
    ihss_total = salario_base * tasa_total / 100.0
    return round(ihss_total, 2)

def _recalcular_isr_todos(db, anio=None, mes=None):
    """Recalcula ISR de todos los empleados (aplica reglas por fecha_ingreso)."""
    anio = anio or datetime.now().year
    mes = mes or datetime.now().month
    emps = db.execute("SELECT id, salario_mensual, fecha_ingreso FROM empleados").fetchall()
    for e in emps:
        sal = e["salario_mensual"]
        fecha_ing = e.get("fecha_ingreso") or ""
        meses = _meses_trabajados_en_anio(fecha_ing, anio)
        sal_periodo = _salario_prorrateado_primer_mes(sal, fecha_ing, anio, mes)
        es_primer = _es_primer_mes_empleado(fecha_ing, anio, mes)
        sal_isr = sal_periodo if es_primer else None
        nuevo_isr = _calcular_isr(sal, db, meses_trabajados=meses, salario_periodo_actual=sal_isr)
        db.execute("UPDATE empleados SET isr=? WHERE id=?", (nuevo_isr, e["id"]))

def _recalcular_ihss_todos(db, anio=None, mes=None):
    """Recalcula IHSS de todos los empleados (aplica reglas por fecha_ingreso)."""
    anio = anio or datetime.now().year
    mes = mes or datetime.now().month
    emps = db.execute("SELECT id, salario_mensual, fecha_ingreso FROM empleados").fetchall()
    for e in emps:
        sal = e["salario_mensual"]
        fecha_ing = e.get("fecha_ingreso") or ""
        sal_periodo = _salario_prorrateado_primer_mes(sal, fecha_ing, anio, mes)
        nuevo_ihss = _calcular_ihss(sal, db, salario_periodo_actual=sal_periodo)
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
        fecha_ing = d.get("fecha_ingreso") or ""
        anio_actual = datetime.now().year
        mes_actual = datetime.now().month
        meses = _meses_trabajados_en_anio(fecha_ing, anio_actual)
        sal_periodo = _salario_prorrateado_primer_mes(sal, fecha_ing, anio_actual, mes_actual)
        es_primer = _es_primer_mes_empleado(fecha_ing, anio_actual, mes_actual)
        sal_isr = sal_periodo if es_primer else None
        isr_auto = _calcular_isr(sal, db, meses_trabajados=meses, salario_periodo_actual=sal_isr)
        ihss_auto = _calcular_ihss(sal, db, salario_periodo_actual=sal_periodo)
        db.execute("INSERT INTO empleados (cod_empleado,nombre_empleado,cargo,salario_mensual,ihss,isr,otro,observacion_otro,correo_institucional,fecha_ingreso) VALUES (?,?,?,?,?,?,?,?,?,?)",
            (d["cod_empleado"],d["nombre_empleado"],d["cargo"],sal,
             ihss_auto,isr_auto,float(d.get("otro",0)),
             d.get("observacion_otro",""),d.get("correo_institucional",""), fecha_ing or None))
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
        fecha_ing = d.get("fecha_ingreso") or ""
        anio_actual = datetime.now().year
        mes_actual = datetime.now().month
        meses = _meses_trabajados_en_anio(fecha_ing, anio_actual)
        sal_periodo = _salario_prorrateado_primer_mes(sal, fecha_ing, anio_actual, mes_actual)
        es_primer = _es_primer_mes_empleado(fecha_ing, anio_actual, mes_actual)
        sal_isr = sal_periodo if es_primer else None
        isr_auto = _calcular_isr(sal, db, meses_trabajados=meses, salario_periodo_actual=sal_isr)
        ihss_auto = _calcular_ihss(sal, db, salario_periodo_actual=sal_periodo)
        db.execute("UPDATE empleados SET cod_empleado=?,nombre_empleado=?,cargo=?,salario_mensual=?,ihss=?,isr=?,otro=?,observacion_otro=?,correo_institucional=?,fecha_ingreso=? WHERE id=?",
            (d["cod_empleado"],d["nombre_empleado"],d["cargo"],sal,
             ihss_auto,isr_auto,float(d.get("otro",0)),
             d.get("observacion_otro",""),d.get("correo_institucional",""), fecha_ing or None, eid))
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
    cols = {r[1] for r in db.execute("PRAGMA table_info(isr_tramos)").fetchall()}
    order_col = "desde_anual" if "desde_anual" in cols else "desde_mensual"
    rows = [dict(r) for r in db.execute(f"SELECT * FROM isr_tramos ORDER BY {order_col} ASC").fetchall()]
    db.close()
    return jsonify(rows)

@app.route("/api/isr/config")
def api_isr_config():
    db = get_db()
    r = db.execute("SELECT * FROM isr_config WHERE id=1").fetchone()
    db.close()
    if r:
        return jsonify(dict(r))
    return jsonify({"gastos_medicos_anual": 40000, "deducible_ivm_mensual": 297.58})

@app.route("/api/isr/config", methods=["POST"])
def api_isr_config_save():
    d = request.json
    db = get_db()
    db.execute("INSERT OR REPLACE INTO isr_config (id, gastos_medicos_anual, deducible_ivm_mensual) VALUES (1,?,?)",
        (float(d.get("gastos_medicos_anual", 40000)), float(d.get("deducible_ivm_mensual", 297.58))))
    db.commit()
    db.close()
    return jsonify({"ok": True})

@app.route("/api/isr/tramos", methods=["POST"])
def api_isr_tramos_save():
    """Reemplaza todos los tramos con los nuevos (rangos ANUALES)."""
    tramos = request.json.get("tramos", [])
    if not tramos:
        return jsonify({"ok": False, "error": "Debe haber al menos un tramo."}), 400
    db = get_db()
    cols = {r[1] for r in db.execute("PRAGMA table_info(isr_tramos)").fetchall()}
    use_anual = "desde_anual" in cols
    db.execute("DELETE FROM isr_tramos")
    for t in tramos:
        if use_anual:
            d = float(t.get("desde_anual", t.get("desde_mensual", 0) * 12))
            h = float(t.get("hasta_anual", t.get("hasta_mensual", 0) * 12))
            db.execute("INSERT INTO isr_tramos (tasa, desde_anual, hasta_anual, descripcion) VALUES (?,?,?,?)",
                (float(t["tasa"]), d, h, t.get("descripcion", "")))
        else:
            db.execute("INSERT INTO isr_tramos (tasa, desde_mensual, hasta_mensual, descripcion) VALUES (?,?,?,?)",
                (float(t["tasa"]), float(t["desde_mensual"]), float(t["hasta_mensual"]), t.get("descripcion", "")))
    _recalcular_isr_todos(db)
    db.commit()
    db.close()
    return jsonify({"ok": True})

@app.route("/api/isr/calcular")
def api_isr_calcular():
    """Calcula ISR para un salario dado (preview)."""
    sal = float(request.args.get("salario", 0))
    isr = _calcular_isr(sal)
    return jsonify({"salario": sal, "isr": isr})

@app.route("/api/isr/tramos/reset", methods=["POST"])
def api_isr_tramos_reset():
    """Restablece la tabla ISR a los valores oficiales 2026 (referencia SH)."""
    tramos_oficial_2026 = [
        (0.0,   0.01,      228324.32, "Exentos"),
        (15.0,  228324.33, 348154.10, "15%"),
        (20.0,  348154.11, 809660.75, "20%"),
        (25.0,  809660.76, 999999999.99, "25%"),
    ]
    db = get_db()
    cols = {r[1] for r in db.execute("PRAGMA table_info(isr_tramos)").fetchall()}
    use_anual = "desde_anual" in cols
    db.execute("DELETE FROM isr_tramos")
    for t in tramos_oficial_2026:
        if use_anual:
            db.execute("INSERT INTO isr_tramos (tasa, desde_anual, hasta_anual, descripcion) VALUES (?,?,?,?)", t)
        else:
            db.execute("INSERT INTO isr_tramos (tasa, desde_mensual, hasta_mensual, descripcion) VALUES (?,?,?,?)",
                (t[0], t[1]/12, t[2]/12, t[3]))
    _recalcular_isr_todos(db)
    db.commit()
    db.close()
    return jsonify({"ok": True})

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
        d = dict(row)
        d.setdefault("tasa_em", 2.5)
        d.setdefault("tasa_ivm", 2.5)
        d.setdefault("techo_mensual", 12000.00)
        return jsonify(d)
    return jsonify({"tasa_em": 2.5, "tasa_ivm": 2.5, "techo_mensual": 12000.00})

@app.route("/api/ihss", methods=["POST"])
def api_ihss_save():
    d = request.json
    db = get_db()
    db.execute("UPDATE ihss_config SET tasa_em=?, tasa_ivm=?, techo_mensual=? WHERE id=1",
               (d["tasa_em"], d.get("tasa_ivm", 2.5), d["techo_mensual"]))
    db.commit(); db.close()
    return jsonify({"ok": True})

# ── API: ISR Config ─────────────────────────────────────────────
@app.route("/api/calcular_isr")
def api_calcular_isr():
    """Calcula ISR mensual usando la tabla de tramos. Soporta meses_trabajados segun fecha_ingreso."""
    salario = float(request.args.get("salario", 0))
    if salario <= 0: return jsonify({"isr_mensual": 0})
    fecha_ingreso = request.args.get("fecha_ingreso", "").strip()
    anio = int(request.args.get("anio", datetime.now().year))
    meses = _meses_trabajados_en_anio(fecha_ingreso, anio) if fecha_ingreso else 12
    
    db = get_db()
    isr_mensual = _calcular_isr(salario, db, meses_trabajados=meses)
    db.close()
    
    return jsonify({"isr_mensual": isr_mensual})

@app.route("/api/calcular_deducciones")
def api_calcular_deducciones():
    """Calcula ISR e IHSS para un empleado en un periodo (para preview de boleta)."""
    salario = float(request.args.get("salario", 0))
    if salario <= 0: return jsonify({"isr": 0, "ihss": 0, "salario_periodo": 0})
    fecha_ingreso = request.args.get("fecha_ingreso", "").strip()
    anio = int(request.args.get("anio", datetime.now().year))
    mes = int(request.args.get("mes", datetime.now().month))
    sal_periodo = _salario_prorrateado_primer_mes(salario, fecha_ingreso, anio, mes)
    meses = _meses_trabajados_en_anio(fecha_ingreso, anio) if fecha_ingreso else 12
    es_primer = _es_primer_mes_empleado(fecha_ingreso, anio, mes)
    db = get_db()
    sal_isr = sal_periodo if es_primer else None
    isr = _calcular_isr(salario, db, meses_trabajados=meses, salario_periodo_actual=sal_isr)
    ihss = _calcular_ihss(salario, db, salario_periodo_actual=sal_periodo)
    db.close()
    return jsonify({"isr": isr, "ihss": ihss, "salario_periodo": sal_periodo, "es_primer_mes": es_primer})

# ── Logica: PDF ─────────────────────────────────────────────────
CNI_BLUE = (35, 57, 129)
CNI_CYAN = (42, 170, 214)
CNI_GREEN = (27, 174, 100)
LOGO_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img", "logo_cni.png")

class BoletaPDF(FPDF):
    def header(self):
        # Barra azul CNI
        self.set_fill_color(*CNI_BLUE)
        self.rect(0, 0, 210, 44, "F")
        # Linea cyan decorativa
        self.set_fill_color(*CNI_CYAN)
        self.rect(0, 44, 210, 2, "F")
        # Logo
        if os.path.exists(LOGO_PATH):
            self.image(LOGO_PATH, 14, 6, 32)
        # Texto header
        self.set_y(10)
        self.set_font("Helvetica", "B", 18)
        self.set_text_color(255, 255, 255)
        self.cell(0, 8, "BOLETA DE PAGO", align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_font("Helvetica", "", 9)
        self.set_text_color(255, 255, 255)
        self.cell(0, 5, "Consejo Nacional de Inversiones", align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_font("Helvetica", "", 7)
        self.set_text_color(200, 210, 230)
        self.cell(0, 5, "Honduras, C.A.", align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(8)

    def footer(self):
        self.set_y(-18)
        self.set_draw_color(*CNI_BLUE)
        self.line(15, self.get_y(), 195, self.get_y())
        self.ln(2)
        self.set_font("Helvetica", "", 7)
        self.set_text_color(120, 120, 120)
        self.cell(0, 4, f"Generado: {datetime.now().strftime('%d/%m/%Y %H:%M')}  |  Pagina {self.page_no()}", align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_font("Helvetica", "", 6)
        self.set_text_color(160, 160, 160)
        self.cell(0, 4, "Sistema de Pagos CNI v2.2.0 - Consejo Nacional de Inversiones", align="C")

    def section(self, text, is_income=False, is_deduction=False):
        if is_income:
            self.set_fill_color(*CNI_GREEN)
        elif is_deduction:
            self.set_fill_color(180, 40, 40)
        else:
            self.set_fill_color(*CNI_BLUE)
        self.set_font("Helvetica", "B", 9)
        self.set_text_color(255, 255, 255)
        self.cell(0, 8, f"   {text}", fill=True, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(2)

    def row(self, label, value, bold=False, is_deduction=False):
        f = "B" if bold else ""
        self.set_font("Helvetica", f, 9)
        self.set_text_color(50, 50, 50)
        self.cell(125, 7, f"   {label}")
        if is_deduction:
            self.set_text_color(180, 40, 40)
        else:
            self.set_text_color(50, 50, 50)
        self.set_font("Helvetica", "B" if bold else "", 9)
        self.cell(0, 7, value, align="R", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        # Linea separadora sutil
        if not bold:
            self.set_draw_color(220, 220, 220)
            self.line(15, self.get_y(), 195, self.get_y())

def _generar_pdf(emp, fi, ff):
    n, cod, cargo = emp["nombre_empleado"], emp["cod_empleado"], emp["cargo"]
    sal = emp["salario_mensual"]
    fecha_fin = datetime.strptime(ff, "%d/%m/%Y")
    anio_periodo = fecha_fin.year
    mes_periodo = fecha_fin.month
    meses = _meses_trabajados_en_anio(emp.get("fecha_ingreso") or "", anio_periodo)
    sal_periodo = _salario_prorrateado_primer_mes(sal, emp.get("fecha_ingreso") or "", anio_periodo, mes_periodo)
    es_primer_mes = _es_primer_mes_empleado(emp.get("fecha_ingreso") or "", anio_periodo, mes_periodo)
    db = get_db()
    sal_isr = sal_periodo if es_primer_mes else None
    isr = _calcular_isr(sal, db, meses_trabajados=meses, salario_periodo_actual=sal_isr)
    ihss = _calcular_ihss(sal, db, salario_periodo_actual=sal_periodo)
    db.close()
    emp["salario_periodo"] = sal_periodo
    emp["isr"] = isr
    emp["ihss"] = ihss
    otro = float(emp.get("otro", 0) or 0)
    obs = emp.get("observacion_otro", "") or ""
    td = ihss + isr + otro
    neto = sal_periodo - td
    fecha_fin = datetime.strptime(ff, "%d/%m/%Y")
    mes = MESES[fecha_fin.month - 1]
    anio = fecha_fin.year
    carpeta = os.path.join(REPORTES_DIR, f"{cod}_{n.replace(' ', '_')}")
    os.makedirs(carpeta, exist_ok=True)
    ruta = os.path.join(carpeta, f"Boleta_{mes}_{anio}.pdf")

    pdf = BoletaPDF()
    pdf.add_page()

    # Datos del empleado
    pdf.section("DATOS DEL EMPLEADO")
    for l, v in [("Codigo:", cod), ("Nombre:", n), ("Cargo:", cargo),
                 ("Correo:", emp.get("correo_institucional", "") or "N/A"),
                 ("Periodo:", f"{fi} al {ff}")]:
        pdf.set_font("Helvetica", "B", 9)
        pdf.set_text_color(*CNI_BLUE)
        pdf.cell(45, 7, f"   {l}")
        pdf.set_font("Helvetica", "", 9)
        pdf.set_text_color(50, 50, 50)
        pdf.cell(0, 7, v, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(4)

    # Ingresos
    pdf.section("INGRESOS", is_income=True)
    if es_primer_mes and sal_periodo != sal:
        pdf.row("Salario (prorrateado por dias trabajados)", fmt(sal_periodo))
    else:
        pdf.row("Salario Mensual", fmt(sal))
    pdf.ln(1)
    pdf.set_draw_color(*CNI_GREEN)
    pdf.line(15, pdf.get_y(), 195, pdf.get_y())
    pdf.ln(1)
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(*CNI_GREEN)
    pdf.cell(125, 8, "   Total Ingresos")
    pdf.cell(0, 8, fmt(sal_periodo), align="R", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(4)

    # Deducciones
    pdf.section("DEDUCCIONES", is_deduction=True)
    pdf.row("IHSS (Seguro Social)", fmt(ihss), is_deduction=True)
    pdf.row("ISR (Impuesto Sobre la Renta)", fmt(isr), is_deduction=True)
    if otro > 0:
        pdf.row(f"Otro ({obs})" if obs else "Otra Deduccion", fmt(otro), is_deduction=True)
    pdf.ln(1)
    pdf.set_draw_color(180, 40, 40)
    pdf.line(15, pdf.get_y(), 195, pdf.get_y())
    pdf.ln(1)
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(180, 40, 40)
    pdf.cell(125, 8, "   Total Deducciones")
    pdf.cell(0, 8, f"-{fmt(td)}", align="R", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(6)

    # Salario Neto
    pdf.set_fill_color(*CNI_BLUE)
    pdf.set_font("Helvetica", "B", 14)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(125, 14, "   SALARIO NETO", fill=True)
    pdf.cell(0, 14, f"{fmt(neto)}   ", fill=True, align="R", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.output(ruta)
    return ruta

def _generar_auditoria(rows, filtro=""):
    carpeta = os.path.join(REPORTES_DIR, "_auditorias")
    os.makedirs(carpeta, exist_ok=True)
    ruta = os.path.join(carpeta, f"Auditoria_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")
    pdf = FPDF()
    pdf.add_page("L")
    pdf.set_auto_page_break(True, 25)

    # Header con logo y colores CNI
    pdf.set_fill_color(*CNI_BLUE)
    pdf.rect(0, 0, 297, 28, "F")
    pdf.set_fill_color(*CNI_CYAN)
    pdf.rect(0, 28, 297, 1.5, "F")
    if os.path.exists(LOGO_PATH):
        pdf.image(LOGO_PATH, 8, 3, 22)
    pdf.set_font("Helvetica", "B", 14)
    pdf.set_text_color(255, 255, 255)
    pdf.set_y(6)
    pdf.cell(0, 8, "REPORTE DE AUDITORIA", align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_font("Helvetica", "", 8)
    pdf.cell(0, 5, "Consejo Nacional de Inversiones - Historico de Pagos", align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(6)

    # Encabezados de tabla
    cols = [("Fecha", 26), ("Cod", 20), ("Empleado", 50), ("Cargo", 38), ("Periodo", 40),
            ("Salario", 26), ("IHSS", 20), ("ISR", 20), ("Otro", 20), ("Deducc.", 26), ("Neto", 26), ("Tipo", 15)]
    pdf.set_font("Helvetica", "B", 7)
    pdf.set_fill_color(*CNI_BLUE)
    pdf.set_text_color(255, 255, 255)
    for t, w in cols:
        pdf.cell(w, 7, t, fill=True, align="C")
    pdf.ln()

    # Filas de datos
    pdf.set_font("Helvetica", "", 7)
    for i, r in enumerate(rows):
        bg = (245, 247, 250) if i % 2 == 0 else (255, 255, 255)
        pdf.set_fill_color(*bg)
        pdf.set_text_color(50, 50, 50)
        data = [r.get("fecha_generacion", ""), r["cod_empleado"], r["nombre_empleado"][:24],
                r["cargo"][:18], f"{r['fecha_inicio']}-{r['fecha_fin']}",
                fmt(r["salario"]), fmt(r["ihss"]), fmt(r["isr"]), fmt(r["otro"]),
                fmt(r["total_deducciones"]), fmt(r["salario_neto"]), r["tipo"]]
        for j, (t, w) in enumerate(cols):
            a = "C" if j in (0, 1, 4, 11) else "L" if j in (2, 3) else "R"
            pdf.cell(w, 6, data[j], fill=True, align=a)
        pdf.ln()

    # Footer de auditoria
    pdf.ln(4)
    pdf.set_font("Helvetica", "", 7)
    pdf.set_text_color(120, 120, 120)
    pdf.cell(0, 5, f"Total registros: {len(rows)}  |  Generado: {datetime.now().strftime('%d/%m/%Y %H:%M')}  |  Sistema de Pagos CNI v2.2.0", align="C")

    pdf.output(ruta)
    return ruta

# ── Logica: Email ───────────────────────────────────────────────
def _enviar_email(smtp_cfg, emp, fi, ff, ruta_pdf):
    srv,port = smtp_cfg["servidor"],smtp_cfg["puerto"]
    usr,pwd = smtp_cfg["usuario"],smtp_cfg["contrasena"]
    if not srv or not usr or not pwd: raise ValueError("Configure SMTP primero.")
    dest = emp["correo_institucional"]
    if not dest: raise ValueError(f"{emp['nombre_empleado']} no tiene correo.")
    sal=emp.get("salario_periodo") or emp["salario_mensual"]
    ihss=float(emp.get("ihss",0) or 0)
    isr=float(emp.get("isr",0) or 0); otro=float(emp.get("otro",0) or 0)
    obs=emp.get("observacion_otro","") or ""; td=ihss+isr+otro; neto=sal-td
    otro_row=""
    if otro>0:
        lbl=f"Otro ({obs})" if obs else "Otra Deduccion"
        otro_row=f'<tr><td style="padding:10px 16px;background-color:#fafafa;border-bottom:1px solid #eeeeee;color:#666666;padding-left:24px">{lbl}</td><td style="padding:10px 16px;background-color:#fafafa;border-bottom:1px solid #eeeeee;color:#cc0000;font-weight:600;text-align:right">-{fmt(otro)}</td></tr>'
    
    # HTML limpio - compatible modo claro y oscuro
    html=f'''<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<meta name="color-scheme" content="light only">
<meta name="supported-color-schemes" content="light only">
</head>
<body style="margin:0;padding:0;background-color:#ffffff;font-family:Arial,Helvetica,sans-serif">
<table width="100%" cellpadding="0" cellspacing="0" style="background-color:#ffffff;padding:32px 0">
<tr><td align="center">
<table width="580" cellpadding="0" cellspacing="0" style="background-color:#ffffff;border-radius:8px;overflow:hidden">

  <!-- Header -->
  <tr><td style="background-color:#233981;padding:28px 32px;text-align:center">
    <h1 style="margin:0;color:#ffffff;font-size:24px;font-weight:700">Boleta de Pago</h1>
    <p style="margin:6px 0 0;color:#ffffff;font-size:12px;font-weight:400;opacity:0.8;letter-spacing:1px">CONSEJO NACIONAL DE INVERSIONES</p>
  </td></tr>

  <!-- Contenido -->
  <tr><td style="padding:28px 32px;background-color:#ffffff">

    <!-- Saludo -->
    <p style="margin:0 0 4px;font-size:14px;color:#333333">Estimado/a <strong>{emp["nombre_empleado"]}</strong>,</p>
    <p style="margin:0 0 24px;font-size:13px;color:#666666">Adjunto su boleta de pago del periodo <strong style="color:#333333">{fi}</strong> al <strong style="color:#333333">{ff}</strong>.</p>

    <!-- Tabla -->
    <table width="100%" cellpadding="0" cellspacing="0" style="font-size:14px;border:1px solid #dddddd;border-radius:4px;overflow:hidden">
      <tr style="background-color:#233981">
        <td style="padding:12px 16px;color:#ffffff;font-weight:600;font-size:12px;text-transform:uppercase;letter-spacing:0.5px">Concepto</td>
        <td style="padding:12px 16px;color:#ffffff;font-weight:600;font-size:12px;text-transform:uppercase;letter-spacing:0.5px;text-align:right">Monto (L.)</td>
      </tr>
      <tr>
        <td style="padding:12px 16px;background-color:#ffffff;border-bottom:1px solid #eeeeee;color:#333333;font-weight:600">{'Salario (prorrateado por dias)' if sal != emp.get('salario_mensual', sal) else 'Salario Mensual'}</td>
        <td style="padding:12px 16px;background-color:#ffffff;border-bottom:1px solid #eeeeee;color:#333333;font-weight:700;text-align:right;font-size:15px">{fmt(sal)}</td>
      </tr>
      <tr>
        <td style="padding:10px 16px;background-color:#fafafa;border-bottom:1px solid #eeeeee;color:#666666;padding-left:24px">IHSS</td>
        <td style="padding:10px 16px;background-color:#fafafa;border-bottom:1px solid #eeeeee;color:#cc0000;font-weight:600;text-align:right">-{fmt(ihss)}</td>
      </tr>
      <tr>
        <td style="padding:10px 16px;background-color:#ffffff;border-bottom:1px solid #eeeeee;color:#666666;padding-left:24px">ISR</td>
        <td style="padding:10px 16px;background-color:#ffffff;border-bottom:1px solid #eeeeee;color:#cc0000;font-weight:600;text-align:right">-{fmt(isr)}</td>
      </tr>
      {otro_row}
      <tr>
        <td style="padding:12px 16px;background-color:#fafafa;border-bottom:2px solid #dddddd;color:#333333;font-weight:600">Total Deducciones</td>
        <td style="padding:12px 16px;background-color:#fafafa;border-bottom:2px solid #dddddd;color:#cc0000;font-weight:700;text-align:right">-{fmt(td)}</td>
      </tr>
      <tr>
        <td style="padding:16px;background-color:#233981;color:#ffffff;font-weight:700;font-size:15px">SALARIO NETO</td>
        <td style="padding:16px;background-color:#233981;color:#ffffff;font-weight:700;font-size:18px;text-align:right">{fmt(neto)}</td>
      </tr>
    </table>

    <!-- Nota -->
    <p style="margin:24px 0 0;font-size:11px;color:#999999;text-align:center">Boleta generada por el Sistema de Pagos CNI. Si tiene consultas, contacte a Recursos Humanos.</p>

  </td></tr>

  <!-- Footer -->
  <tr><td style="padding:16px 32px;background-color:#f5f5f5;text-align:center;border-top:1px solid #eeeeee">
    <p style="margin:0;font-size:11px;color:#999999">(c) 2026 Consejo Nacional de Inversiones - Honduras</p>
  </td></tr>

</table>
</td></tr>
</table>
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
    sal=emp.get("salario_periodo") or emp["salario_mensual"]
    ihss=float(emp.get("ihss",0) or 0)
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
