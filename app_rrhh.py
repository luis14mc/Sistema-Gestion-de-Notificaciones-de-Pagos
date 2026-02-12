#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Recursos Humanos
Gestion de Personal · Boletas de Pago · Historico · Reportes
"""

import customtkinter as ctk
import sqlite3
import os
from datetime import datetime
from fpdf import FPDF
from tkinter import ttk, StringVar
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from fpdf.enums import XPos, YPos

# ─── Rutas ──────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "rrhh_cni.db")
REPORTES_DIR = os.path.join(BASE_DIR, "reportes_pagos_RRHH")
MESES = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
         "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]

# ─── Tema: solo claro ──────────────────────────────────────────
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")


# ─── Paleta — inspirada en Power BI / dashboards corporativos ──
class C:
    SIDE        = "#1b2a4a"
    SIDE_HOVER  = "#243758"
    SIDE_ACTIVE = "#0f1f38"
    SIDE_TEXT   = "#d1d9e6"
    SIDE_MUTED  = "#7b8fa6"
    SIDE_ACCENT = "#3b82f6"

    BG          = "#eef1f5"
    CARD        = "#ffffff"
    CARD_BORDER = "#e2e8f0"

    TEXT        = "#1e293b"
    TEXT_SEC    = "#475569"
    TEXT_MUTED  = "#94a3b8"

    PRIMARY     = "#2563eb"
    PRI_HOVER   = "#1d4ed8"
    PRI_LIGHT   = "#dbeafe"
    PRI_TEXT    = "#1e40af"

    OK          = "#059669"
    OK_LIGHT    = "#d1fae5"
    DANGER      = "#dc2626"
    DANGER_LT   = "#fee2e2"
    WARN        = "#d97706"
    WARN_LT     = "#fef3c7"

    INP_BG      = "#ffffff"
    INP_BORDER  = "#cbd5e1"

    TV_BG       = "#ffffff"
    TV_HEAD     = "#f1f5f9"
    TV_HEAD_FG  = "#475569"
    TV_SEL      = "#dbeafe"
    TV_SEL_FG   = "#1e40af"

    R = 10
    RS = 8
    FONT = ""


def fmt(amount):
    return f"L. {amount:,.2f}"


# ═════════════════════════════════════════════════════════════════
#  SWEET ALERT — Overlay inline dentro de la ventana principal
# ═════════════════════════════════════════════════════════════════
_SWAL_ICONS = {
    "success": ("\u2713", "#059669", "#d1fae5"),
    "error":   ("\u2717", "#dc2626", "#fee2e2"),
    "warning": ("\u0021", "#d97706", "#fef3c7"),
    "info":    ("i",      "#2563eb", "#dbeafe"),
    "confirm": ("?",      "#7c3aed", "#ede9fe"),
}


def _get_root(widget):
    w = widget
    while w is not None:
        if isinstance(w, ctk.CTk):
            return w
        w = w.master
    return widget.winfo_toplevel()


def _swal_show(parent, kind, title, message, on_yes=None):
    root = _get_root(parent)
    result = {"value": False}
    icon_char, icon_color, icon_bg = _SWAL_ICONS.get(kind, _SWAL_ICONS["info"])

    overlay = ctk.CTkFrame(root, fg_color="#1e293b", corner_radius=0)
    overlay.place(relx=0, rely=0, relwidth=1, relheight=1)
    overlay.lift()

    card_w = ctk.CTkFrame(overlay, fg_color="#ffffff", corner_radius=16,
                          border_color="#e2e8f0", border_width=1, width=400)
    card_w.place(relx=0.5, rely=0.5, anchor="center")

    inner = ctk.CTkFrame(card_w, fg_color="transparent")
    inner.pack(padx=40, pady=(32, 28))

    icon_frame = ctk.CTkFrame(inner, width=64, height=64, fg_color=icon_bg,
                              corner_radius=32)
    icon_frame.pack(pady=(0, 16))
    icon_frame.pack_propagate(False)
    ctk.CTkLabel(icon_frame, text=icon_char, font=(C.FONT, 28, "bold"),
                 text_color=icon_color).pack(expand=True)

    ctk.CTkLabel(inner, text=title, font=(C.FONT, 18, "bold"),
                 text_color=C.TEXT).pack(pady=(0, 8))
    ctk.CTkLabel(inner, text=message, font=(C.FONT, 13),
                 text_color=C.TEXT_SEC, wraplength=320,
                 justify="center").pack(pady=(0, 24))

    btn_row = ctk.CTkFrame(inner, fg_color="transparent")
    btn_row.pack()

    def _close():
        overlay.destroy()

    def _yes():
        result["value"] = True
        overlay.destroy()
        if on_yes:
            root.after(10, on_yes)

    def _no():
        result["value"] = False
        overlay.destroy()

    if kind == "confirm":
        ctk.CTkButton(btn_row, text="Cancelar", width=120, height=40,
                      corner_radius=C.RS, fg_color="#f1f5f9",
                      border_color="#cbd5e1", border_width=1,
                      text_color=C.TEXT_SEC, hover_color="#e2e8f0",
                      font=(C.FONT, 13, "bold"),
                      command=_no).pack(side="left", padx=(0, 10))
        ctk.CTkButton(btn_row, text="Confirmar", width=120, height=40,
                      corner_radius=C.RS, fg_color=icon_color,
                      hover_color="#5b21b6", text_color="#ffffff",
                      font=(C.FONT, 13, "bold"),
                      command=_yes).pack(side="left")
    else:
        ctk.CTkButton(btn_row, text="Aceptar", width=160, height=42,
                      corner_radius=C.RS, fg_color=icon_color,
                      hover_color=icon_color, text_color="#ffffff",
                      font=(C.FONT, 14, "bold"),
                      command=_close).pack()

    overlay.bind("<Button-1>", lambda e: None)
    root.wait_window(overlay)
    return result["value"]


def swal_ok(parent, title, msg):
    _swal_show(parent, "success", title, msg)

def swal_err(parent, title, msg):
    _swal_show(parent, "error", title, msg)

def swal_warn(parent, title, msg):
    _swal_show(parent, "warning", title, msg)

def swal_info(parent, title, msg):
    _swal_show(parent, "info", title, msg)

def swal_confirm(parent, title, msg, on_yes=None):
    return _swal_show(parent, "confirm", title, msg, on_yes=on_yes)


# ═════════════════════════════════════════════════════════════════
#  BASE DE DATOS
# ═════════════════════════════════════════════════════════════════
class DB:
    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH)
        self.conn.row_factory = sqlite3.Row
        c = self.conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS empleados (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cod_empleado TEXT UNIQUE NOT NULL,
            nombre_empleado TEXT NOT NULL,
            cargo TEXT NOT NULL,
            salario_mensual REAL NOT NULL,
            ihss REAL NOT NULL DEFAULT 0,
            isr REAL NOT NULL DEFAULT 0,
            otro REAL NOT NULL DEFAULT 0,
            observacion_otro TEXT DEFAULT '',
            correo_institucional TEXT DEFAULT ''
        )''')
        c.execute('''CREATE TABLE IF NOT EXISTS smtp_config (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            servidor TEXT DEFAULT 'smtp.office365.com', puerto INTEGER DEFAULT 587,
            usuario TEXT DEFAULT '', contrasena TEXT DEFAULT '',
            emisor TEXT DEFAULT 'Servicios Online',
            remitente_display TEXT DEFAULT ''
        )''')
        c.execute("INSERT OR IGNORE INTO smtp_config (id) VALUES (1)")
        c.execute('''CREATE TABLE IF NOT EXISTS historico_pagos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            empleado_id INTEGER,
            cod_empleado TEXT,
            nombre_empleado TEXT,
            cargo TEXT,
            fecha_inicio TEXT,
            fecha_fin TEXT,
            periodo_key TEXT UNIQUE,
            salario REAL,
            ihss REAL,
            isr REAL,
            otro REAL,
            observacion_otro TEXT DEFAULT '',
            total_deducciones REAL,
            salario_neto REAL,
            tipo TEXT DEFAULT 'PDF',
            fecha_generacion TEXT,
            ruta_pdf TEXT DEFAULT ''
        )''')
        # Migrar historico: agregar periodo_key si no existe
        hist_cols = {r[1] for r in c.execute("PRAGMA table_info(historico_pagos)").fetchall()}
        if "periodo_key" not in hist_cols:
            try:
                c.execute("ALTER TABLE historico_pagos ADD COLUMN periodo_key TEXT UNIQUE")
                self.conn.commit()
            except sqlite3.OperationalError:
                pass
        # ── Migraciones ──
        cols_emp = {r[1] for r in c.execute("PRAGMA table_info(empleados)").fetchall()}
        # Migrar ivm1+em -> ihss
        if "ivm1" in cols_emp and "ihss" not in cols_emp:
            c.execute("ALTER TABLE empleados ADD COLUMN ihss REAL NOT NULL DEFAULT 0")
            c.execute("UPDATE empleados SET ihss = ivm1 + em")
            self.conn.commit()
        elif "ihss" not in cols_emp:
            try:
                c.execute("ALTER TABLE empleados ADD COLUMN ihss REAL NOT NULL DEFAULT 0")
                self.conn.commit()
            except sqlite3.OperationalError:
                pass
        if "otro" not in cols_emp:
            try:
                c.execute("ALTER TABLE empleados ADD COLUMN otro REAL NOT NULL DEFAULT 0")
                self.conn.commit()
            except sqlite3.OperationalError:
                pass
        if "observacion_otro" not in cols_emp:
            try:
                c.execute("ALTER TABLE empleados ADD COLUMN observacion_otro TEXT DEFAULT ''")
                self.conn.commit()
            except sqlite3.OperationalError:
                pass
        # SMTP migrations
        for col, default in [("emisor", "'Servicios Online'"), ("remitente_display", "''")]:
            try:
                c.execute(f"ALTER TABLE smtp_config ADD COLUMN {col} TEXT DEFAULT {default}")
                self.conn.commit()
            except sqlite3.OperationalError:
                pass
        self.conn.commit()

    # ── Empleados ──
    def all(self):
        return self.conn.execute("SELECT * FROM empleados ORDER BY nombre_empleado").fetchall()

    def get(self, eid):
        return self.conn.execute("SELECT * FROM empleados WHERE id=?", (eid,)).fetchone()

    def search(self, t):
        t = f"%{t}%"
        return self.conn.execute(
            "SELECT * FROM empleados WHERE nombre_empleado LIKE ? OR cod_empleado LIKE ? "
            "OR cargo LIKE ? ORDER BY nombre_empleado", (t, t, t)).fetchall()

    def add(self, d):
        self.conn.execute("INSERT INTO empleados (cod_empleado, nombre_empleado, cargo,"
                          "salario_mensual, ihss, isr, otro, observacion_otro, correo_institucional) "
                          "VALUES (?,?,?,?,?,?,?,?,?)", d)
        self.conn.commit()

    def update(self, eid, d):
        self.conn.execute("UPDATE empleados SET cod_empleado=?, nombre_empleado=?, cargo=?,"
                          "salario_mensual=?, ihss=?, isr=?, otro=?, observacion_otro=?,"
                          "correo_institucional=? WHERE id=?", (*d, eid))
        self.conn.commit()

    def delete(self, eid):
        self.conn.execute("DELETE FROM empleados WHERE id=?", (eid,))
        self.conn.commit()

    def stats(self):
        return dict(self.conn.execute(
            "SELECT COUNT(*) as total, COALESCE(SUM(salario_mensual),0) as planilla,"
            "COALESCE(AVG(salario_mensual),0) as promedio FROM empleados").fetchone())

    # ── SMTP ──
    def smtp(self):
        return self.conn.execute("SELECT * FROM smtp_config WHERE id=1").fetchone()

    def save_smtp(self, s, p, u, c, emisor="Servicios Online", remitente_display=""):
        self.conn.execute(
            "UPDATE smtp_config SET servidor=?,puerto=?,usuario=?,contrasena=?,"
            "emisor=?,remitente_display=? WHERE id=1",
            (s, p, u, c, emisor, remitente_display))
        self.conn.commit()

    # ── Historico de pagos ──
    def _periodo_key(self, cod, ff):
        """Genera clave unica: COD_MM_YYYY basado en fecha fin."""
        try:
            dt = datetime.strptime(ff, "%d/%m/%Y")
            return f"{cod}_{dt.month:02d}_{dt.year}"
        except ValueError:
            return f"{cod}_{ff}"

    def registrar_pago(self, emp, fi, ff, tipo, ruta_pdf=""):
        sal = emp["salario_mensual"]
        ihss = self._safe(emp, "ihss")
        isr = self._safe(emp, "isr")
        otro = self._safe(emp, "otro")
        obs = self._safe_str(emp, "observacion_otro")
        td = ihss + isr + otro
        neto = sal - td
        pk = self._periodo_key(emp["cod_empleado"], ff)
        ahora = datetime.now().strftime("%d/%m/%Y %H:%M")

        # Si ya existe para este empleado+mes, actualizar
        existe = self.conn.execute(
            "SELECT id FROM historico_pagos WHERE periodo_key=?", (pk,)).fetchone()
        if existe:
            self.conn.execute(
                "UPDATE historico_pagos SET nombre_empleado=?, cargo=?, "
                "fecha_inicio=?, fecha_fin=?, salario=?, ihss=?, isr=?, otro=?, "
                "observacion_otro=?, total_deducciones=?, salario_neto=?, tipo=?, "
                "fecha_generacion=?, ruta_pdf=? WHERE periodo_key=?",
                (emp["nombre_empleado"], emp["cargo"], fi, ff, sal, ihss, isr,
                 otro, obs, td, neto, tipo, ahora, ruta_pdf, pk))
        else:
            self.conn.execute(
                "INSERT INTO historico_pagos (empleado_id, cod_empleado, nombre_empleado,"
                "cargo, fecha_inicio, fecha_fin, periodo_key, salario, ihss, isr, otro, "
                "observacion_otro, total_deducciones, salario_neto, tipo, fecha_generacion, "
                "ruta_pdf) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (emp["id"], emp["cod_empleado"], emp["nombre_empleado"], emp["cargo"],
                 fi, ff, pk, sal, ihss, isr, otro, obs, td, neto, tipo, ahora, ruta_pdf))
        self.conn.commit()

    def historico_all(self):
        return self.conn.execute(
            "SELECT * FROM historico_pagos ORDER BY id DESC").fetchall()

    def historico_filtrar(self, cod=None, fi=None, ff=None):
        q = "SELECT * FROM historico_pagos WHERE 1=1"
        params = []
        if cod:
            q += " AND (cod_empleado LIKE ? OR nombre_empleado LIKE ?)"
            params += [f"%{cod}%", f"%{cod}%"]
        if fi:
            q += " AND fecha_fin >= ?"
            params.append(fi)
        if ff:
            q += " AND fecha_fin <= ?"
            params.append(ff)
        q += " ORDER BY id DESC"
        return self.conn.execute(q, params).fetchall()

    def historico_stats(self, rows=None):
        if rows is None:
            rows = self.historico_all()
        total = len(rows)
        monto = sum(r["salario_neto"] for r in rows)
        ded = sum(r["total_deducciones"] for r in rows)
        return {"total": total, "monto_neto": monto, "deducciones": ded}

    def _safe(self, emp, key):
        try:
            return float(emp[key] or 0)
        except (KeyError, IndexError, TypeError):
            return 0.0

    def _safe_str(self, emp, key):
        try:
            return str(emp[key] or "")
        except (KeyError, IndexError):
            return ""

    def close(self):
        self.conn.close()


# ═════════════════════════════════════════════════════════════════
#  PDF
# ═════════════════════════════════════════════════════════════════
class BoletaPDF(FPDF):
    def header(self):
        self.set_fill_color(37, 99, 235)
        self.rect(0, 0, 210, 36, "F")
        self.set_font("Helvetica", "B", 18)
        self.set_text_color(255, 255, 255)
        self.set_y(8)
        self.cell(0, 10, "BOLETA DE PAGO", align="C",
                  new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_font("Helvetica", "", 9)
        self.set_text_color(219, 234, 254)
        self.cell(0, 6, "Sistema de Recursos Humanos", align="C",
                  new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 7)
        self.set_text_color(148, 163, 184)
        self.cell(0, 8, f"Generado: {datetime.now().strftime('%d/%m/%Y %H:%M')}  |  "
                  f"Pagina {self.page_no()}", align="C")

    def section(self, text, r, g, b):
        self.set_font("Helvetica", "B", 10)
        self.set_fill_color(r, g, b)
        self.set_text_color(30, 41, 59)
        self.cell(0, 8, f"   {text}", fill=True,
                  new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(3)

    def row(self, label, value, bold=False, color=None):
        f = "B" if bold else ""
        self.set_font("Helvetica", f, 9)
        self.set_text_color(71, 85, 105)
        self.cell(125, 7, f"   {label}")
        if color:
            self.set_text_color(*color)
        self.set_font("Helvetica", "B" if bold else "", 9)
        self.cell(0, 7, value, align="R", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_text_color(71, 85, 105)


def _emp_deductions(emp):
    """Extrae deducciones del empleado de forma segura."""
    try:
        ihss = float(emp["ihss"] or 0)
    except (KeyError, IndexError):
        ihss = float(emp.get("ivm1", 0) or 0) + float(emp.get("em", 0) or 0)
    isr = float(emp["isr"] or 0)
    try:
        otro = float(emp["otro"] or 0)
    except (KeyError, IndexError):
        otro = 0.0
    try:
        obs = str(emp["observacion_otro"] or "")
    except (KeyError, IndexError):
        obs = ""
    return ihss, isr, otro, obs


def generar_pdf(emp, fi, ff):
    n, cod, cargo = emp["nombre_empleado"], emp["cod_empleado"], emp["cargo"]
    sal = emp["salario_mensual"]
    ihss, isr, otro, obs = _emp_deductions(emp)
    td = ihss + isr + otro
    neto = sal - td

    try:
        fecha_fin = datetime.strptime(ff, "%d/%m/%Y")
    except ValueError:
        raise ValueError("Formato invalido. Use DD/MM/AAAA")

    mes = MESES[fecha_fin.month - 1]
    anio = fecha_fin.year
    carpeta = os.path.join(REPORTES_DIR, f"{cod}_{n.replace(' ', '_')}")
    os.makedirs(carpeta, exist_ok=True)
    ruta = os.path.join(carpeta, f"Boleta_{mes}_{anio}.pdf")

    if os.path.exists(ruta):
        from tkinter import messagebox as _mb
        if not _mb.askyesno("Existente",
                            f"Ya existe boleta de {mes} {anio} para {n}.\nReemplazar?"):
            return None

    pdf = BoletaPDF()
    pdf.add_page()
    pdf.section("DATOS DEL EMPLEADO", 241, 245, 249)
    for l, v in [("Codigo:", cod), ("Nombre:", n), ("Cargo:", cargo),
                 ("Periodo:", f"{fi}  al  {ff}")]:
        pdf.set_font("Helvetica", "B", 9)
        pdf.cell(45, 7, f"   {l}")
        pdf.set_font("Helvetica", "", 9)
        pdf.cell(0, 7, v, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(4)

    pdf.section("INGRESOS", 209, 250, 229)
    pdf.row("Salario Mensual", fmt(sal), color=(5, 150, 105))
    pdf.set_draw_color(226, 232, 240)
    pdf.line(15, pdf.get_y() + 1, 195, pdf.get_y() + 1)
    pdf.ln(2)
    pdf.row("Total Ingresos", fmt(sal), bold=True, color=(5, 150, 105))
    pdf.ln(4)

    pdf.section("DEDUCCIONES", 254, 226, 226)
    pdf.row("IHSS (Seguro Social)", fmt(ihss), color=(220, 38, 38))
    pdf.row("ISR (Impuesto Sobre la Renta)", fmt(isr), color=(220, 38, 38))
    if otro > 0:
        lbl_otro = f"Otro ({obs})" if obs else "Otra Deduccion"
        pdf.row(lbl_otro, fmt(otro), color=(220, 38, 38))
    pdf.set_draw_color(226, 232, 240)
    pdf.line(15, pdf.get_y() + 2, 195, pdf.get_y() + 2)
    pdf.ln(3)
    pdf.row("Total Deducciones", fmt(td), bold=True, color=(220, 38, 38))
    pdf.ln(8)

    pdf.set_font("Helvetica", "B", 13)
    pdf.set_fill_color(37, 99, 235)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(125, 13, "   SALARIO NETO", fill=True)
    pdf.cell(0, 13, f"{fmt(neto)}   ", fill=True, align="R",
             new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.output(ruta)
    return ruta


# ═════════════════════════════════════════════════════════════════
#  REPORTE AUDITORIA PDF
# ═════════════════════════════════════════════════════════════════
def generar_reporte_auditoria(rows, filtro_texto=""):
    """Genera PDF de reporte de auditoria con el historico de pagos."""
    carpeta = os.path.join(REPORTES_DIR, "_auditorias")
    os.makedirs(carpeta, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    ruta = os.path.join(carpeta, f"Auditoria_{ts}.pdf")

    pdf = FPDF()
    pdf.add_page("L")  # Landscape
    pdf.set_auto_page_break(auto=True, margin=20)

    # Header
    pdf.set_fill_color(37, 99, 235)
    pdf.rect(0, 0, 297, 28, "F")
    pdf.set_font("Helvetica", "B", 16)
    pdf.set_text_color(255, 255, 255)
    pdf.set_y(6)
    pdf.cell(0, 10, "REPORTE DE AUDITORIA - HISTORICO DE PAGOS", align="C",
             new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_font("Helvetica", "", 8)
    pdf.set_text_color(219, 234, 254)
    info_line = f"Generado: {datetime.now().strftime('%d/%m/%Y %H:%M')}"
    if filtro_texto:
        info_line += f"  |  Filtro: {filtro_texto}"
    info_line += f"  |  Registros: {len(rows)}"
    pdf.cell(0, 5, info_line, align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(8)

    # Resumen
    total_bruto = sum(r["salario"] for r in rows)
    total_ded = sum(r["total_deducciones"] for r in rows)
    total_neto = sum(r["salario_neto"] for r in rows)

    pdf.set_font("Helvetica", "B", 9)
    pdf.set_text_color(30, 41, 59)
    pdf.set_fill_color(241, 245, 249)
    for lbl, val, clr in [("Total Bruto:", fmt(total_bruto), (5, 150, 105)),
                           ("Total Deducciones:", fmt(total_ded), (220, 38, 38)),
                           ("Total Neto:", fmt(total_neto), (37, 99, 235))]:
        pdf.set_text_color(71, 85, 105)
        pdf.cell(40, 7, lbl)
        pdf.set_text_color(*clr)
        pdf.cell(50, 7, val)
    pdf.ln(10)

    # Tabla
    cols = [("Fecha Gen.", 28), ("Codigo", 22), ("Empleado", 55), ("Cargo", 40),
            ("Periodo", 42), ("Salario", 28), ("IHSS", 22), ("ISR", 22),
            ("Otro", 22), ("Deducciones", 28), ("Neto", 28), ("Tipo", 16)]

    pdf.set_font("Helvetica", "B", 7)
    pdf.set_fill_color(37, 99, 235)
    pdf.set_text_color(255, 255, 255)
    for txt, w in cols:
        pdf.cell(w, 7, txt, border=0, fill=True, align="C")
    pdf.ln()

    pdf.set_font("Helvetica", "", 7)
    for i, r in enumerate(rows):
        bg = (248, 250, 252) if i % 2 == 0 else (255, 255, 255)
        pdf.set_fill_color(*bg)
        pdf.set_text_color(30, 41, 59)
        data = [
            r["fecha_generacion"] or "", r["cod_empleado"],
            r["nombre_empleado"][:25], r["cargo"][:20],
            f"{r['fecha_inicio']} - {r['fecha_fin']}",
            fmt(r["salario"]), fmt(r["ihss"]), fmt(r["isr"]),
            fmt(r["otro"]), fmt(r["total_deducciones"]),
            fmt(r["salario_neto"]), r["tipo"]
        ]
        for j, (txt, w) in enumerate(cols):
            a = "C" if j in (0, 1, 4, 11) else "L" if j in (2, 3) else "R"
            pdf.cell(w, 6, data[j], border=0, fill=True, align=a)
        pdf.ln()

    # Footer
    pdf.set_y(-15)
    pdf.set_font("Helvetica", "I", 7)
    pdf.set_text_color(148, 163, 184)
    pdf.cell(0, 8, f"Reporte de Auditoria  |  {datetime.now().strftime('%d/%m/%Y %H:%M')}", align="C")

    pdf.output(ruta)
    return ruta


# ═════════════════════════════════════════════════════════════════
#  EMAIL
# ═════════════════════════════════════════════════════════════════
def enviar_email(smtp_cfg, emp, fi, ff, ruta_pdf):
    srv, port = smtp_cfg["servidor"], smtp_cfg["puerto"]
    usr, pwd = smtp_cfg["usuario"], smtp_cfg["contrasena"]
    if not srv or not usr or not pwd:
        raise ValueError("Configure SMTP primero (seccion Configuracion).")
    dest = emp["correo_institucional"]
    if not dest:
        raise ValueError(f"{emp['nombre_empleado']} no tiene correo registrado.")

    sal = emp["salario_mensual"]
    ihss, isr, otro, obs = _emp_deductions(emp)
    td = ihss + isr + otro
    neto = sal - td

    otro_row = ""
    if otro > 0:
        lbl = f"Otro ({obs})" if obs else "Otra Deduccion"
        otro_row = (f'<tr style="background:#fafafa;">'
                    f'<td style="padding:8px 14px;border-bottom:1px solid #f1f5f9;">{lbl}</td>'
                    f'<td style="padding:8px 14px;text-align:right;color:#dc2626;'
                    f'border-bottom:1px solid #f1f5f9;">-{fmt(otro)}</td></tr>')

    html = f"""<html><body style="font-family:'Segoe UI',Arial,sans-serif;color:#334155;
    max-width:580px;margin:0 auto;background:#f8fafc;">
    <div style="background:#2563eb;color:#fff;padding:24px;text-align:center;
    border-radius:8px 8px 0 0;">
    <h2 style="margin:0;">Boleta de Pago</h2>
    <p style="margin:4px 0 0;opacity:.8;font-size:13px;">Sistema de Recursos Humanos</p></div>
    <div style="padding:24px;border:1px solid #e2e8f0;border-top:none;background:#fff;
    border-radius:0 0 8px 8px;">
    <p>Estimado/a <strong>{emp['nombre_empleado']}</strong>,</p>
    <p style="color:#64748b;">Boleta del periodo <strong style="color:#1e293b;">{fi}</strong>
    al <strong style="color:#1e293b;">{ff}</strong>.</p>
    <table style="border-collapse:collapse;width:100%;margin:16px 0;font-size:13px;">
    <tr style="background:#2563eb;color:#fff;">
    <th style="padding:10px 14px;text-align:left;">Concepto</th>
    <th style="padding:10px 14px;text-align:right;">Monto</th></tr>
    <tr style="background:#f0fdf4;">
    <td style="padding:10px 14px;border-bottom:1px solid #e2e8f0;"><strong>Salario</strong></td>
    <td style="padding:10px 14px;text-align:right;color:#059669;border-bottom:1px solid #e2e8f0;">
    <strong>{fmt(sal)}</strong></td></tr>
    <tr><td style="padding:8px 14px;border-bottom:1px solid #f1f5f9;">IHSS</td>
    <td style="padding:8px 14px;text-align:right;color:#dc2626;border-bottom:1px solid #f1f5f9;">
    -{fmt(ihss)}</td></tr>
    <tr style="background:#fafafa;"><td style="padding:8px 14px;border-bottom:1px solid #f1f5f9;">ISR</td>
    <td style="padding:8px 14px;text-align:right;color:#dc2626;border-bottom:1px solid #f1f5f9;">
    -{fmt(isr)}</td></tr>
    {otro_row}
    <tr style="background:#fef2f2;">
    <td style="padding:10px 14px;border-bottom:1px solid #e2e8f0;"><strong>Deducciones</strong></td>
    <td style="padding:10px 14px;text-align:right;color:#dc2626;border-bottom:1px solid #e2e8f0;">
    <strong>-{fmt(td)}</strong></td></tr>
    <tr style="background:#2563eb;color:#fff;">
    <td style="padding:12px 14px;font-size:14px;"><strong>SALARIO NETO</strong></td>
    <td style="padding:12px 14px;text-align:right;font-size:15px;">
    <strong>{fmt(neto)}</strong></td></tr></table>
    <p style="color:#94a3b8;font-size:11px;margin-top:20px;border-top:1px solid #e2e8f0;
    padding-top:10px;">Correo generado automaticamente.</p></div></body></html>"""

    try:
        remitente_display = smtp_cfg["remitente_display"] or usr
    except (KeyError, IndexError):
        remitente_display = usr

    msg = MIMEMultipart()
    msg["From"] = remitente_display
    msg["To"] = dest
    msg["Subject"] = f"Boleta de Pago - {fi} al {ff}"
    msg.attach(MIMEText(html, "html"))
    if ruta_pdf and os.path.exists(ruta_pdf):
        with open(ruta_pdf, "rb") as f:
            adj = MIMEBase("application", "pdf")
            adj.set_payload(f.read())
            encoders.encode_base64(adj)
            adj.add_header("Content-Disposition",
                           f"attachment; filename={os.path.basename(ruta_pdf)}")
            msg.attach(adj)

    # Extraer dominio del usuario para EHLO (necesario en WSL/Office365)
    ehlo_domain = usr.split("@")[-1] if "@" in usr else "localhost"

    try:
        if port == 465:
            server = smtplib.SMTP_SSL(srv, port, timeout=30)
            server.ehlo(ehlo_domain)
        else:
            server = smtplib.SMTP(srv, port, timeout=30)
            server.ehlo(ehlo_domain)
            server.starttls()
            server.ehlo(ehlo_domain)
        server.login(usr, pwd)
        server.sendmail(usr, dest, msg.as_string())
        server.quit()
    except smtplib.SMTPAuthenticationError:
        raise ValueError("Credenciales incorrectas. Verifique usuario y contrasena.")
    except smtplib.SMTPRecipientsRefused:
        raise ValueError(f"Correo rechazado: {dest} no es valido.")
    except smtplib.SMTPException as e:
        raise ValueError(f"Error SMTP: {e}")
    except TimeoutError:
        raise ValueError(f"Timeout: No se pudo conectar a {srv}:{port}.")
    except Exception as e:
        raise ValueError(f"Error de conexion: {e}")


# ═════════════════════════════════════════════════════════════════
#  COMPONENTES UI
# ═════════════════════════════════════════════════════════════════
def card(parent, **kw):
    return ctk.CTkFrame(parent, fg_color=C.CARD, corner_radius=C.R,
                        border_color=C.CARD_BORDER, border_width=1, **kw)


def field(parent, label, placeholder="", show=None, value="", width=None):
    fr = ctk.CTkFrame(parent, fg_color="transparent")
    ctk.CTkLabel(fr, text=label, font=(C.FONT, 12), text_color=C.TEXT_SEC,
                 anchor="w").pack(fill="x")
    kw = dict(placeholder_text=placeholder, height=38, corner_radius=C.RS,
              border_color=C.INP_BORDER, fg_color=C.INP_BG, border_width=1,
              font=(C.FONT, 13), text_color=C.TEXT, show=show)
    if width:
        kw["width"] = width
    e = ctk.CTkEntry(fr, **kw)
    e.pack(fill="x", pady=(4, 0))
    if value:
        e.insert(0, str(value))
    return fr, e


def btn(parent, text, cmd, color=None, hover=None, text_color="#ffffff",
        width=140, height=38, outline=False):
    kw = dict(text=text, command=cmd, width=width, height=height,
              corner_radius=C.RS, font=(C.FONT, 13, "bold"))
    if outline:
        kw.update(fg_color="transparent", border_color=color or C.PRIMARY,
                  border_width=2, text_color=color or C.PRIMARY,
                  hover_color=C.PRI_LIGHT)
    else:
        kw.update(fg_color=color or C.PRIMARY, hover_color=hover or C.PRI_HOVER,
                  text_color=text_color)
    return ctk.CTkButton(parent, **kw)


def stat_card(parent, title, value, accent, last=False):
    c = card(parent)
    px = (0, 0) if last else (0, 10)
    c.pack(side="left", fill="both", expand=True, padx=px)
    ctk.CTkFrame(c, fg_color=accent, height=3, corner_radius=1
                 ).pack(fill="x", padx=16, pady=(14, 0))
    ctk.CTkLabel(c, text=title, font=(C.FONT, 11), text_color=C.TEXT_MUTED
                 ).pack(anchor="w", padx=16, pady=(6, 0))
    lbl = ctk.CTkLabel(c, text=value, font=(C.FONT, 20, "bold"), text_color=accent)
    lbl.pack(anchor="w", padx=16, pady=(2, 14))
    return lbl


def _setup_tree_style(name="PBI.Treeview"):
    style = ttk.Style()
    style.theme_use("clam")
    style.configure(name, background="#ffffff", foreground="#1e293b",
                    fieldbackground="#ffffff", borderwidth=0, rowheight=38,
                    font=(C.FONT, 11))
    style.configure(f"{name}.Heading", background="#f1f5f9",
                    foreground="#475569", borderwidth=0,
                    font=(C.FONT, 10, "bold"), relief="flat", padding=(10, 8))
    style.map(name, background=[("selected", "#dbeafe")],
              foreground=[("selected", "#1e40af")])
    style.map(f"{name}.Heading", background=[("active", "#e2e8f0")])
    style.layout(name, [(f"{name}.treearea", {"sticky": "nswe"})])


# ═════════════════════════════════════════════════════════════════
#  PANEL: GESTION DE PERSONAL
# ═════════════════════════════════════════════════════════════════
class PersonalPanel(ctk.CTkFrame):
    def __init__(self, parent, db):
        super().__init__(parent, fg_color="transparent")
        self.db = db
        self.editing_id = None

        # ── Vista Lista ──
        self.list_view = ctk.CTkFrame(self, fg_color="transparent")

        hdr = ctk.CTkFrame(self.list_view, fg_color="transparent")
        hdr.pack(fill="x", pady=(0, 14))
        ctk.CTkLabel(hdr, text="Gestion de Personal",
                     font=(C.FONT, 22, "bold"), text_color=C.TEXT).pack(side="left")
        btn(hdr, "+  Nuevo Empleado", self._show_form_new,
            width=180, height=40).pack(side="right")

        st_row = ctk.CTkFrame(self.list_view, fg_color="transparent")
        st_row.pack(fill="x", pady=(0, 14))
        self.s_total = stat_card(st_row, "Total Empleados", "0", C.PRIMARY)
        self.s_plan = stat_card(st_row, "Planilla Mensual", "L. 0.00", C.OK)
        self.s_prom = stat_card(st_row, "Salario Promedio", "L. 0.00", C.WARN, last=True)

        self.search_var = StringVar()
        self.search_var.trace_add("write", lambda *_: self._load())
        ctk.CTkEntry(self.list_view, textvariable=self.search_var, height=40,
                     placeholder_text="Buscar por nombre, codigo o cargo...",
                     corner_radius=C.RS, border_color=C.INP_BORDER,
                     fg_color=C.CARD, border_width=1, font=(C.FONT, 13),
                     text_color=C.TEXT).pack(fill="x", pady=(0, 10))

        tc = card(self.list_view)
        tc.pack(fill="both", expand=True, pady=(0, 8))
        inner = ctk.CTkFrame(tc, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=1, pady=1)

        _setup_tree_style()

        cols = ("cod", "nombre", "cargo", "salario", "ihss", "isr", "otro", "correo")
        self.tree = ttk.Treeview(inner, columns=cols, show="headings",
                                 style="PBI.Treeview", selectmode="browse")
        for col, txt, w, stretch in [
                ("cod", "Codigo", 80, False), ("nombre", "Nombre", 180, True),
                ("cargo", "Cargo", 140, True), ("salario", "Salario", 100, False),
                ("ihss", "IHSS", 80, False), ("isr", "ISR", 80, False),
                ("otro", "Otro", 80, False), ("correo", "Correo", 180, True)]:
            self.tree.heading(col, text=txt)
            a = "e" if col in ("salario", "ihss", "isr", "otro") else "w"
            self.tree.column(col, width=w, anchor=a, minwidth=50, stretch=stretch)

        sb = ctk.CTkScrollbar(inner, command=self.tree.yview,
                              button_color="#cbd5e1", button_hover_color="#94a3b8")
        self.tree.configure(yscrollcommand=sb.set)
        self.tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y", padx=(0, 3), pady=3)
        self.tree.bind("<Double-1>", lambda _: self._show_form_edit())

        br = ctk.CTkFrame(self.list_view, fg_color="transparent")
        br.pack(fill="x")
        btn(br, "Editar", self._show_form_edit, outline=True,
            width=130).pack(side="left", padx=(0, 8))
        btn(br, "Eliminar", self._delete, color=C.DANGER,
            hover="#b91c1c", width=130).pack(side="left")

        # ── Vista Formulario ──
        self.form_view = ctk.CTkFrame(self, fg_color="transparent")

        form_hdr = ctk.CTkFrame(self.form_view, fg_color="transparent")
        form_hdr.pack(fill="x", pady=(0, 14))
        self.form_title = ctk.CTkLabel(form_hdr, text="Nuevo Empleado",
                                       font=(C.FONT, 22, "bold"), text_color=C.TEXT)
        self.form_title.pack(side="left")
        btn(form_hdr, "Volver a lista", self._show_list, outline=True,
            width=150).pack(side="right")

        form_card = card(self.form_view)
        form_card.pack(fill="both", expand=True)
        form_inner = ctk.CTkFrame(form_card, fg_color="transparent")
        form_inner.pack(fill="both", expand=True, padx=28, pady=24)

        row1 = ctk.CTkFrame(form_inner, fg_color="transparent")
        row1.pack(fill="x", pady=(0, 6))
        f1, self.f_cod = field(row1, "Codigo de Empleado *", "CNI001")
        f1.pack(side="left", fill="x", expand=True, padx=(0, 12))
        f2, self.f_nombre = field(row1, "Nombre Completo *", "Nombre del empleado")
        f2.pack(side="left", fill="x", expand=True)

        row2 = ctk.CTkFrame(form_inner, fg_color="transparent")
        row2.pack(fill="x", pady=(0, 6))
        f3, self.f_cargo = field(row2, "Cargo *", "Puesto o cargo")
        f3.pack(side="left", fill="x", expand=True, padx=(0, 12))
        f4, self.f_salario = field(row2, "Salario Mensual (L.) *", "0.00")
        f4.pack(side="left", fill="x", expand=True)

        row3 = ctk.CTkFrame(form_inner, fg_color="transparent")
        row3.pack(fill="x", pady=(0, 6))
        f5, self.f_ihss = field(row3, "IHSS (L.)", "0.00")
        f5.pack(side="left", fill="x", expand=True, padx=(0, 12))
        f6, self.f_isr = field(row3, "ISR (L.)", "0.00")
        f6.pack(side="left", fill="x", expand=True, padx=(0, 12))
        f7, self.f_otro = field(row3, "Otro Descuento (L.)", "0.00")
        f7.pack(side="left", fill="x", expand=True)

        row3b = ctk.CTkFrame(form_inner, fg_color="transparent")
        row3b.pack(fill="x", pady=(0, 6))
        f7b, self.f_obs = field(row3b, "Observacion (detalle del otro descuento)", "Ej: Prestamo, Embargo, etc.")
        f7b.pack(fill="x")

        row4 = ctk.CTkFrame(form_inner, fg_color="transparent")
        row4.pack(fill="x", pady=(0, 16))
        f8, self.f_correo = field(row4, "Correo Institucional", "correo@cni.hn")
        f8.pack(fill="x")

        self._form_entries = [self.f_cod, self.f_nombre, self.f_cargo, self.f_salario,
                              self.f_ihss, self.f_isr, self.f_otro, self.f_obs, self.f_correo]

        btn_row = ctk.CTkFrame(form_inner, fg_color="transparent")
        btn_row.pack(fill="x")
        btn(btn_row, "Cancelar", self._show_list, outline=True,
            width=140).pack(side="left", padx=(0, 10))
        btn(btn_row, "Guardar Empleado", self._save,
            width=180, height=42).pack(side="left")

        self._show_list()

    def _show_list(self):
        self.form_view.pack_forget()
        self.list_view.pack(fill="both", expand=True)
        self._load()

    def _show_form_new(self):
        self.editing_id = None
        self.form_title.configure(text="Nuevo Empleado")
        for e in self._form_entries:
            e.delete(0, "end")
        self.list_view.pack_forget()
        self.form_view.pack(fill="both", expand=True)

    def _show_form_edit(self):
        sel = self.tree.selection()
        if not sel:
            swal_info(self, "Seleccionar", "Seleccione un empleado de la tabla.")
            return
        emp = self.db.get(int(sel[0]))
        if not emp:
            return
        self.editing_id = emp["id"]
        self.form_title.configure(text="Editar Empleado")
        keys = ["cod_empleado", "nombre_empleado", "cargo", "salario_mensual",
                "ihss", "isr", "otro", "observacion_otro", "correo_institucional"]
        for e, k in zip(self._form_entries, keys):
            e.delete(0, "end")
            e.insert(0, str(emp[k]) if emp[k] is not None else "")
        self.list_view.pack_forget()
        self.form_view.pack(fill="both", expand=True)

    def _save(self):
        try:
            vals = [e.get().strip() for e in self._form_entries]
            cod, nombre, cargo = vals[0], vals[1], vals[2]
            sal = float(vals[3] or 0)
            ihss, isr, otro = float(vals[4] or 0), float(vals[5] or 0), float(vals[6] or 0)
            obs = vals[7]
            correo = vals[8]
            if not cod or not nombre or not cargo:
                swal_warn(self, "Campos Requeridos", "Codigo, Nombre y Cargo son obligatorios.")
                return
            if sal <= 0:
                swal_warn(self, "Salario Invalido", "El salario debe ser mayor a cero.")
                return
            data = (cod, nombre, cargo, sal, ihss, isr, otro, obs, correo)
            if self.editing_id:
                self.db.update(self.editing_id, data)
            else:
                self.db.add(data)
            self._show_list()
        except ValueError:
            swal_err(self, "Error de Datos", "Los montos deben ser numericos.")
        except sqlite3.IntegrityError:
            swal_err(self, "Codigo Duplicado", f"El codigo '{self._form_entries[0].get().strip()}' ya existe.")

    def _delete(self):
        sel = self.tree.selection()
        if not sel:
            swal_info(self, "Seleccionar", "Seleccione un empleado de la tabla.")
            return
        emp = self.db.get(int(sel[0]))
        if emp:
            def do_del():
                self.db.delete(emp["id"])
                self._load()
            swal_confirm(self, "Eliminar Empleado",
                         f"Desea eliminar a {emp['nombre_empleado']}?\nEsta accion no se puede deshacer.",
                         on_yes=do_del)

    def _load(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        t = self.search_var.get().strip()
        emps = self.db.search(t) if t else self.db.all()
        for e in emps:
            ihss = self._safe_val(e, "ihss")
            isr = float(e["isr"] or 0)
            otro = self._safe_val(e, "otro")
            self.tree.insert("", "end", iid=str(e["id"]), values=(
                e["cod_empleado"], e["nombre_empleado"], e["cargo"],
                fmt(e["salario_mensual"]), fmt(ihss),
                fmt(isr), fmt(otro), e["correo_institucional"]))
        s = self.db.stats()
        self.s_total.configure(text=str(s["total"]))
        self.s_plan.configure(text=fmt(s["planilla"]))
        self.s_prom.configure(text=fmt(s["promedio"]))

    def _safe_val(self, emp, key):
        try:
            return float(emp[key] or 0)
        except (KeyError, IndexError):
            return 0.0


# ═════════════════════════════════════════════════════════════════
#  PANEL: BOLETA DE PAGO
# ═════════════════════════════════════════════════════════════════
class BoletaPanel(ctk.CTkFrame):
    def __init__(self, parent, db):
        super().__init__(parent, fg_color="transparent")
        self.db = db
        self.emp_actual = None

        ctk.CTkLabel(self, text="Boleta de Pago",
                     font=(C.FONT, 22, "bold"), text_color=C.TEXT
                     ).pack(anchor="w", pady=(0, 14))

        ctrl = card(self)
        ctrl.pack(fill="x", pady=(0, 12))

        r1 = ctk.CTkFrame(ctrl, fg_color="transparent")
        r1.pack(fill="x", padx=20, pady=(16, 8))

        ctk.CTkLabel(r1, text="Empleado", font=(C.FONT, 12, "bold"),
                     text_color=C.TEXT_SEC).pack(side="left", padx=(0, 10))
        self.combo = ctk.CTkComboBox(
            r1, height=38, corner_radius=C.RS,
            border_color=C.INP_BORDER, fg_color=C.INP_BG, border_width=1,
            button_color="#cbd5e1", button_hover_color="#94a3b8",
            dropdown_fg_color="#ffffff", dropdown_hover_color="#f1f5f9",
            dropdown_text_color=C.TEXT, text_color=C.TEXT,
            font=(C.FONT, 13), command=self._on_sel, state="readonly")
        self.combo.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.combo.set("Seleccione empleado")

        btn(r1, "Actualizar", self.refresh, outline=True,
            width=110, height=36).pack(side="right")

        r2 = ctk.CTkFrame(ctrl, fg_color="transparent")
        r2.pack(fill="x", padx=20, pady=(0, 16))

        ctk.CTkLabel(r2, text="Desde", font=(C.FONT, 12, "bold"),
                     text_color=C.TEXT_SEC).pack(side="left", padx=(0, 8))
        self.fi = ctk.CTkEntry(r2, placeholder_text="DD/MM/AAAA", width=130,
                               height=38, corner_radius=C.RS,
                               border_color=C.INP_BORDER, fg_color=C.INP_BG,
                               border_width=1, font=(C.FONT, 13), text_color=C.TEXT)
        self.fi.pack(side="left", padx=(0, 16))

        ctk.CTkLabel(r2, text="Hasta", font=(C.FONT, 12, "bold"),
                     text_color=C.TEXT_SEC).pack(side="left", padx=(0, 8))
        self.ff = ctk.CTkEntry(r2, placeholder_text="DD/MM/AAAA", width=130,
                               height=38, corner_radius=C.RS,
                               border_color=C.INP_BORDER, fg_color=C.INP_BG,
                               border_width=1, font=(C.FONT, 13), text_color=C.TEXT)
        self.ff.pack(side="left", padx=(0, 16))

        btn(r2, "Generar Vista Previa", self._preview, width=180, height=38).pack(side="left")

        now = datetime.now()
        pm = 12 if now.month == 1 else now.month - 1
        py = now.year - 1 if now.month == 1 else now.year
        self.fi.insert(0, f"20/{pm:02d}/{py}")
        self.ff.insert(0, f"20/{now.month:02d}/{now.year}")

        self.preview = card(self)
        self.preview.pack(fill="both", expand=True, pady=(0, 10))
        self._empty_preview()

        ar = ctk.CTkFrame(self, fg_color="transparent")
        ar.pack(fill="x")
        self.b_pdf = btn(ar, "Exportar PDF", self._pdf, color=C.OK,
                         hover="#047857", width=10, height=42)
        self.b_pdf.pack(side="left", fill="x", expand=True, padx=(0, 6))
        self.b_pdf.configure(state="disabled")

        self.b_mail = btn(ar, "Enviar Correo", self._email,
                          width=10, height=42)
        self.b_mail.pack(side="left", fill="x", expand=True, padx=(0, 6))
        self.b_mail.configure(state="disabled")

        self.b_both = btn(ar, "PDF + Correo", self._both, color="#7c3aed",
                          hover="#6d28d9", width=10, height=42)
        self.b_both.pack(side="left", fill="x", expand=True)
        self.b_both.configure(state="disabled")

        self.refresh()

    def _empty_preview(self):
        for w in self.preview.winfo_children():
            w.destroy()
        ctk.CTkLabel(self.preview, text="Seleccione un empleado y genere la vista previa",
                     font=(C.FONT, 14), text_color=C.TEXT_MUTED).pack(expand=True)

    def refresh(self):
        emps = self.db.all()
        self.emap = {}
        vals = []
        for e in emps:
            d = f"{e['cod_empleado']}  —  {e['nombre_empleado']}"
            vals.append(d)
            self.emap[d] = e["id"]
        self.combo.configure(values=vals)
        if not vals:
            self.combo.set("No hay empleados")

    def _on_sel(self, ch):
        if ch in self.emap:
            self.emp_actual = self.db.get(self.emap[ch])

    def _check(self):
        if not self.emp_actual:
            swal_info(self, "Sin Seleccion", "Seleccione un empleado del listado.")
            return False
        fi, ff = self.fi.get().strip(), self.ff.get().strip()
        if not fi or not ff:
            swal_warn(self, "Fechas Requeridas", "Ingrese ambas fechas de corte.")
            return False
        try:
            datetime.strptime(fi, "%d/%m/%Y")
            datetime.strptime(ff, "%d/%m/%Y")
        except ValueError:
            swal_err(self, "Formato Invalido", "El formato correcto es DD/MM/AAAA.")
            return False
        return True

    def _row(self, parent, label, value, color=None, bold=False):
        r = ctk.CTkFrame(parent, fg_color="transparent", height=30)
        r.pack(fill="x", padx=20, pady=2)
        r.pack_propagate(False)
        lf = (C.FONT, 12, "bold") if bold else (C.FONT, 12)
        vf = (C.FONT, 13, "bold") if bold else (C.FONT, 12)
        ctk.CTkLabel(r, text=label, font=lf, text_color=C.TEXT if bold else C.TEXT_SEC,
                     anchor="w").pack(side="left")
        ctk.CTkLabel(r, text=value, font=vf, text_color=color or C.TEXT,
                     anchor="e").pack(side="right")

    def _preview(self):
        if not self._check():
            return
        e = self.emp_actual
        fi, ff = self.fi.get().strip(), self.ff.get().strip()
        sal = e["salario_mensual"]
        ihss, isr, otro, obs = _emp_deductions(e)
        td = ihss + isr + otro
        neto = sal - td

        for w in self.preview.winfo_children():
            w.destroy()

        sc = ctk.CTkScrollableFrame(self.preview, fg_color="transparent",
                                    scrollbar_button_color="#cbd5e1")
        sc.pack(fill="both", expand=True, padx=4, pady=4)

        info = ctk.CTkFrame(sc, fg_color="#f8fafc", corner_radius=C.RS,
                            border_color=C.CARD_BORDER, border_width=1)
        info.pack(fill="x", padx=10, pady=(8, 6))
        ctk.CTkLabel(info, text="DATOS DEL EMPLEADO", font=(C.FONT, 10, "bold"),
                     text_color=C.TEXT_MUTED).pack(anchor="w", padx=20, pady=(14, 6))
        for l, v in [("Codigo", e["cod_empleado"]), ("Nombre", e["nombre_empleado"]),
                     ("Cargo", e["cargo"]), ("Periodo", f"{fi}  al  {ff}"),
                     ("Correo", e["correo_institucional"] or "No registrado")]:
            r = ctk.CTkFrame(info, fg_color="transparent")
            r.pack(fill="x", padx=20, pady=1)
            ctk.CTkLabel(r, text=l, font=(C.FONT, 11), text_color=C.TEXT_MUTED,
                         width=70, anchor="w").pack(side="left")
            ctk.CTkLabel(r, text=v, font=(C.FONT, 12, "bold"), text_color=C.TEXT,
                         anchor="w").pack(side="left", padx=(8, 0))
        ctk.CTkFrame(info, height=6, fg_color="transparent").pack()

        inc = ctk.CTkFrame(sc, fg_color="#f0fdf4", corner_radius=C.RS,
                           border_color="#bbf7d0", border_width=1)
        inc.pack(fill="x", padx=10, pady=(0, 6))
        ctk.CTkLabel(inc, text="INGRESOS", font=(C.FONT, 10, "bold"),
                     text_color=C.OK).pack(anchor="w", padx=20, pady=(14, 6))
        self._row(inc, "Salario Mensual", fmt(sal), color=C.OK, bold=True)
        ctk.CTkFrame(inc, height=8, fg_color="transparent").pack()

        ded = ctk.CTkFrame(sc, fg_color="#fef2f2", corner_radius=C.RS,
                           border_color="#fecaca", border_width=1)
        ded.pack(fill="x", padx=10, pady=(0, 6))
        ctk.CTkLabel(ded, text="DEDUCCIONES", font=(C.FONT, 10, "bold"),
                     text_color=C.DANGER).pack(anchor="w", padx=20, pady=(14, 6))
        self._row(ded, "IHSS (Seguro Social)", f"-{fmt(ihss)}", color=C.DANGER)
        self._row(ded, "ISR (Impuesto Sobre la Renta)", f"-{fmt(isr)}", color=C.DANGER)
        if otro > 0:
            lbl_otro = f"Otro ({obs})" if obs else "Otra Deduccion"
            self._row(ded, lbl_otro, f"-{fmt(otro)}", color=C.DANGER)
        ctk.CTkFrame(ded, height=1, fg_color="#fecaca").pack(fill="x", padx=20, pady=(6, 4))
        self._row(ded, "Total Deducciones", f"-{fmt(td)}", color=C.DANGER, bold=True)
        ctk.CTkFrame(ded, height=8, fg_color="transparent").pack()

        net = ctk.CTkFrame(sc, fg_color=C.PRIMARY, corner_radius=C.RS)
        net.pack(fill="x", padx=10, pady=(0, 6))
        nr = ctk.CTkFrame(net, fg_color="transparent")
        nr.pack(fill="x", padx=24, pady=16)
        ctk.CTkLabel(nr, text="SALARIO NETO", font=(C.FONT, 15, "bold"),
                     text_color="#ffffff").pack(side="left")
        ctk.CTkLabel(nr, text=fmt(neto), font=(C.FONT, 20, "bold"),
                     text_color="#ffffff").pack(side="right")

        for b in (self.b_pdf, self.b_mail, self.b_both):
            b.configure(state="normal")

    def _pdf(self):
        if not self._check():
            return
        try:
            r = generar_pdf(self.emp_actual, self.fi.get().strip(), self.ff.get().strip())
            if r:
                self.db.registrar_pago(self.emp_actual, self.fi.get().strip(),
                                       self.ff.get().strip(), "PDF", r)
                swal_ok(self, "PDF Generado", f"Boleta guardada exitosamente en:\n{r}")
        except Exception as ex:
            swal_err(self, "Error al Generar PDF", str(ex))

    def _email(self):
        if not self._check():
            return
        fi, ff = self.fi.get().strip(), self.ff.get().strip()
        try:
            r = generar_pdf(self.emp_actual, fi, ff)
            if not r:
                return
            enviar_email(self.db.smtp(), self.emp_actual, fi, ff, r)
            self.db.registrar_pago(self.emp_actual, fi, ff, "Email", r)
            swal_ok(self, "Correo Enviado",
                    f"Boleta enviada a:\n{self.emp_actual['correo_institucional']}")
        except Exception as ex:
            swal_err(self, "Error al Enviar", str(ex))

    def _both(self):
        if not self._check():
            return
        fi, ff = self.fi.get().strip(), self.ff.get().strip()
        try:
            r = generar_pdf(self.emp_actual, fi, ff)
            if not r:
                return
            enviar_email(self.db.smtp(), self.emp_actual, fi, ff, r)
            self.db.registrar_pago(self.emp_actual, fi, ff, "PDF+Email", r)
            swal_ok(self, "Proceso Completado",
                    f"PDF guardado y correo enviado a:\n{self.emp_actual['correo_institucional']}")
        except Exception as ex:
            swal_err(self, "Error", str(ex))


# ═════════════════════════════════════════════════════════════════
#  PANEL: HISTORICO DE PAGOS
# ═════════════════════════════════════════════════════════════════
class HistoricoPanel(ctk.CTkFrame):
    def __init__(self, parent, db):
        super().__init__(parent, fg_color="transparent")
        self.db = db
        self._rows = []

        hdr = ctk.CTkFrame(self, fg_color="transparent")
        hdr.pack(fill="x", pady=(0, 14))
        ctk.CTkLabel(hdr, text="Historico de Pagos",
                     font=(C.FONT, 22, "bold"), text_color=C.TEXT).pack(side="left")
        btn(hdr, "Exportar Auditoria", self._exportar, color="#7c3aed",
            hover="#6d28d9", width=200, height=40).pack(side="right")

        # Stats
        st_row = ctk.CTkFrame(self, fg_color="transparent")
        st_row.pack(fill="x", pady=(0, 14))
        self.s_total = stat_card(st_row, "Total Registros", "0", C.PRIMARY)
        self.s_neto = stat_card(st_row, "Monto Neto Total", "L. 0.00", C.OK)
        self.s_ded = stat_card(st_row, "Deducciones Total", "L. 0.00", C.DANGER, last=True)

        # Filtros
        filt = card(self)
        filt.pack(fill="x", pady=(0, 10))
        filt_inner = ctk.CTkFrame(filt, fg_color="transparent")
        filt_inner.pack(fill="x", padx=20, pady=14)

        ctk.CTkLabel(filt_inner, text="Filtros", font=(C.FONT, 13, "bold"),
                     text_color=C.TEXT).pack(side="left", padx=(0, 12))

        ctk.CTkLabel(filt_inner, text="Empleado:", font=(C.FONT, 12),
                     text_color=C.TEXT_SEC).pack(side="left", padx=(0, 4))
        self.f_emp = ctk.CTkEntry(filt_inner, placeholder_text="Nombre o codigo...",
                                  height=36, corner_radius=C.RS,
                                  border_color=C.INP_BORDER, fg_color=C.INP_BG,
                                  border_width=1, font=(C.FONT, 12), text_color=C.TEXT)
        self.f_emp.pack(side="left", fill="x", expand=True, padx=(0, 12))

        ctk.CTkLabel(filt_inner, text="Desde:", font=(C.FONT, 12),
                     text_color=C.TEXT_SEC).pack(side="left", padx=(0, 4))
        self.f_fi = ctk.CTkEntry(filt_inner, placeholder_text="DD/MM/AAAA",
                                 width=110, height=36, corner_radius=C.RS,
                                 border_color=C.INP_BORDER, fg_color=C.INP_BG,
                                 border_width=1, font=(C.FONT, 12), text_color=C.TEXT)
        self.f_fi.pack(side="left", padx=(0, 10))

        ctk.CTkLabel(filt_inner, text="Hasta:", font=(C.FONT, 12),
                     text_color=C.TEXT_SEC).pack(side="left", padx=(0, 4))
        self.f_ff = ctk.CTkEntry(filt_inner, placeholder_text="DD/MM/AAAA",
                                 width=110, height=36, corner_radius=C.RS,
                                 border_color=C.INP_BORDER, fg_color=C.INP_BG,
                                 border_width=1, font=(C.FONT, 12), text_color=C.TEXT)
        self.f_ff.pack(side="left", padx=(0, 12))

        btn(filt_inner, "Buscar", self._filtrar, width=90, height=36).pack(side="left", padx=(0, 6))
        btn(filt_inner, "Limpiar", self._limpiar, outline=True,
            width=80, height=36).pack(side="left")

        # Tabla
        tc = card(self)
        tc.pack(fill="both", expand=True)
        t_inner = ctk.CTkFrame(tc, fg_color="transparent")
        t_inner.pack(fill="both", expand=True, padx=1, pady=1)

        _setup_tree_style("HIST.Treeview")

        cols = ("fecha", "cod", "nombre", "cargo", "periodo", "salario",
                "ihss", "isr", "otro", "deducciones", "neto", "tipo")
        self.tree = ttk.Treeview(t_inner, columns=cols, show="headings",
                                 style="HIST.Treeview", selectmode="browse")
        for col, txt, w, stretch in [
                ("fecha", "Fecha", 90, False), ("cod", "Codigo", 65, False),
                ("nombre", "Empleado", 150, True), ("cargo", "Cargo", 110, True),
                ("periodo", "Periodo", 140, True), ("salario", "Salario", 85, False),
                ("ihss", "IHSS", 65, False), ("isr", "ISR", 65, False),
                ("otro", "Otro", 65, False), ("deducciones", "Deducc.", 80, False),
                ("neto", "Neto", 85, False), ("tipo", "Tipo", 60, False)]:
            self.tree.heading(col, text=txt)
            a = "e" if col in ("salario", "ihss", "isr", "otro", "deducciones", "neto") else "w"
            if col == "tipo":
                a = "center"
            self.tree.column(col, width=w, anchor=a, minwidth=45, stretch=stretch)

        sb = ctk.CTkScrollbar(t_inner, command=self.tree.yview,
                              button_color="#cbd5e1", button_hover_color="#94a3b8")
        self.tree.configure(yscrollcommand=sb.set)
        self.tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y", padx=(0, 3), pady=3)

    def refresh(self):
        self._rows = self.db.historico_all()
        self._render()

    def _filtrar(self):
        emp = self.f_emp.get().strip() or None
        fi = self.f_fi.get().strip() or None
        ff = self.f_ff.get().strip() or None
        self._rows = self.db.historico_filtrar(emp, fi, ff)
        self._render()

    def _limpiar(self):
        self.f_emp.delete(0, "end")
        self.f_fi.delete(0, "end")
        self.f_ff.delete(0, "end")
        self.refresh()

    def _render(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        for r in self._rows:
            self.tree.insert("", "end", values=(
                r["fecha_generacion"] or "", r["cod_empleado"],
                r["nombre_empleado"], r["cargo"],
                f"{r['fecha_inicio']} al {r['fecha_fin']}",
                fmt(r["salario"]), fmt(r["ihss"]), fmt(r["isr"]),
                fmt(r["otro"]), fmt(r["total_deducciones"]),
                fmt(r["salario_neto"]), r["tipo"]))
        st = self.db.historico_stats(self._rows)
        self.s_total.configure(text=str(st["total"]))
        self.s_neto.configure(text=fmt(st["monto_neto"]))
        self.s_ded.configure(text=fmt(st["deducciones"]))

    def _exportar(self):
        if not self._rows:
            swal_info(self, "Sin Datos", "No hay registros para exportar.")
            return
        try:
            filtro = ""
            if self.f_emp.get().strip():
                filtro += f"Empleado: {self.f_emp.get().strip()}"
            if self.f_fi.get().strip():
                filtro += f"  Desde: {self.f_fi.get().strip()}"
            if self.f_ff.get().strip():
                filtro += f"  Hasta: {self.f_ff.get().strip()}"
            ruta = generar_reporte_auditoria(self._rows, filtro)
            swal_ok(self, "Reporte Generado",
                    f"Reporte de auditoria exportado en:\n{ruta}")
        except Exception as ex:
            swal_err(self, "Error", str(ex))


# ═════════════════════════════════════════════════════════════════
#  PANEL: CONFIGURACION SMTP
# ═════════════════════════════════════════════════════════════════
class ConfigPanel(ctk.CTkFrame):
    def __init__(self, parent, db):
        super().__init__(parent, fg_color="transparent")
        self.db = db

        ctk.CTkLabel(self, text="Configuracion SMTP",
                     font=(C.FONT, 22, "bold"), text_color=C.TEXT
                     ).pack(anchor="w", pady=(0, 14))

        c = card(self)
        c.pack(fill="x")
        inner = ctk.CTkFrame(c, fg_color="transparent")
        inner.pack(fill="x", padx=28, pady=24)

        note = ctk.CTkFrame(inner, fg_color="#dbeafe", corner_radius=8)
        note.pack(fill="x", pady=(0, 16))
        ctk.CTkLabel(note, text="  Office 365  —  smtp.office365.com  |  STARTTLS  |  Puerto 587  |  SSL: No",
                     font=(C.FONT, 12), text_color="#1e40af",
                     wraplength=520, anchor="w").pack(padx=14, pady=10, anchor="w")

        cfg = db.smtp()

        ctk.CTkLabel(inner, text="Conexion al Servidor",
                     font=(C.FONT, 13, "bold"), text_color=C.TEXT).pack(anchor="w", pady=(0, 6))
        r1 = ctk.CTkFrame(inner, fg_color="transparent")
        r1.pack(fill="x", pady=(0, 6))
        f1, self.e_srv = field(r1, "Host SMTP", "smtp.office365.com",
                               value=cfg["servidor"] or "smtp.office365.com")
        f1.pack(side="left", fill="x", expand=True, padx=(0, 12))
        f2, self.e_port = field(r1, "Puerto", "587",
                                value=str(cfg["puerto"]) if cfg["puerto"] else "587",
                                width=120)
        f2.pack(side="left")

        ctk.CTkLabel(inner, text="Credenciales",
                     font=(C.FONT, 13, "bold"), text_color=C.TEXT).pack(anchor="w", pady=(10, 6))
        r2 = ctk.CTkFrame(inner, fg_color="transparent")
        r2.pack(fill="x", pady=(0, 6))
        f3, self.e_usr = field(r2, "Username (Cuenta con licencia)", "tu-usuario@cni.hn",
                               value=cfg["usuario"] or "")
        f3.pack(side="left", fill="x", expand=True, padx=(0, 12))
        f4, self.e_pwd = field(r2, "Password", "********", show="*",
                               value=cfg["contrasena"] or "")
        f4.pack(side="left", fill="x", expand=True)

        ctk.CTkLabel(inner, text="Identidad del Remitente",
                     font=(C.FONT, 13, "bold"), text_color=C.TEXT).pack(anchor="w", pady=(10, 6))
        r3 = ctk.CTkFrame(inner, fg_color="transparent")
        r3.pack(fill="x", pady=(0, 6))
        try:
            emisor_val = cfg["emisor"] or "Servicios Online"
        except (KeyError, IndexError):
            emisor_val = "Servicios Online"
        try:
            remitente_val = cfg["remitente_display"] or ""
        except (KeyError, IndexError):
            remitente_val = ""
        f5, self.e_emisor = field(r3, "Nombre del Emisor", "Servicios Online",
                                  value=emisor_val)
        f5.pack(side="left", fill="x", expand=True, padx=(0, 12))
        f6, self.e_remitente = field(r3, "Correo Remitente (From)",
                                     "notificaciones@cni.hn", value=remitente_val)
        f6.pack(side="left", fill="x", expand=True)

        ctk.CTkLabel(inner, text="El Username inicia sesion en el servidor. "
                     "El Correo Remitente es lo que el destinatario ve como direccion de origen. "
                     "Si se deja vacio, se usa el Username.",
                     font=(C.FONT, 11), text_color=C.TEXT_MUTED,
                     wraplength=520, justify="left").pack(anchor="w", pady=(4, 0))

        br = ctk.CTkFrame(inner, fg_color="transparent")
        br.pack(fill="x", pady=(16, 0))
        btn(br, "Guardar Configuracion", self._save, width=200, height=42).pack(side="left")

    def _save(self):
        try:
            self.db.save_smtp(
                self.e_srv.get().strip(),
                int(self.e_port.get().strip() or 587),
                self.e_usr.get().strip(),
                self.e_pwd.get().strip(),
                self.e_emisor.get().strip() or "Servicios Online",
                self.e_remitente.get().strip())
            swal_ok(self, "Configuracion Guardada", "Las credenciales SMTP se guardaron correctamente.")
        except ValueError:
            swal_err(self, "Error de Puerto", "El puerto debe ser un numero valido.")


# ═════════════════════════════════════════════════════════════════
#  SIDEBAR NAV ITEM
# ═════════════════════════════════════════════════════════════════
class NavBtn(ctk.CTkFrame):
    def __init__(self, parent, text, icon="", command=None):
        super().__init__(parent, fg_color="transparent", height=44, cursor="hand2")
        self.pack_propagate(False)
        self._cmd = command
        self._on = False
        self.bar = ctk.CTkFrame(self, width=3, fg_color="transparent", corner_radius=1)
        self.bar.pack(side="left", fill="y", padx=(6, 0), pady=7)
        self.lbl = ctk.CTkLabel(self, text=f"  {icon}   {text}", font=(C.FONT, 13),
                                text_color=C.SIDE_TEXT, anchor="w", cursor="hand2")
        self.lbl.pack(side="left", fill="x", expand=True, padx=(8, 12))
        for w in (self, self.lbl):
            w.bind("<Button-1>", lambda e: self._cmd and self._cmd())
            w.bind("<Enter>", lambda e: not self._on and self.configure(fg_color=C.SIDE_HOVER))
            w.bind("<Leave>", lambda e: not self._on and self.configure(fg_color="transparent"))

    def active(self, on):
        self._on = on
        if on:
            self.configure(fg_color=C.SIDE_ACTIVE)
            self.bar.configure(fg_color=C.SIDE_ACCENT)
            self.lbl.configure(text_color="#ffffff")
        else:
            self.configure(fg_color="transparent")
            self.bar.configure(fg_color="transparent")
            self.lbl.configure(text_color=C.SIDE_TEXT)


# ═════════════════════════════════════════════════════════════════
#  APP PRINCIPAL
# ═════════════════════════════════════════════════════════════════
class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        # ── Ocultar ventana mientras se construye (sin parpadeo) ──
        self.withdraw()

        self.title("Sistema de Recursos Humanos — CNI Honduras")
        self.configure(fg_color=C.BG)

        # ── Tamaño fijo tipo WinForm, centrado ──
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        w, h = 1100, 680
        x = (sw - w) // 2
        y = (sh - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")
        self.minsize(900, 580)
        self.resizable(True, True)

        # ── Marco principal sin bordes redondeados (Windows Form look) ──
        self.db = DB()

        # Contenedor raiz que ocupa toda la ventana sin margenes
        root_frame = ctk.CTkFrame(self, fg_color=C.BG, corner_radius=0)
        root_frame.pack(fill="both", expand=True)

        # ── Barra superior (titulo de la app, como un header fijo) ──
        topbar = ctk.CTkFrame(root_frame, height=48, fg_color=C.SIDE,
                              corner_radius=0)
        topbar.pack(fill="x")
        topbar.pack_propagate(False)
        ctk.CTkLabel(topbar, text="  RRHH  |  Sistema de Recursos Humanos",
                     font=(C.FONT, 13, "bold"), text_color="#ffffff",
                     anchor="w").pack(side="left", padx=16, fill="y")
        ctk.CTkLabel(topbar, text="CNI Honduras  ",
                     font=(C.FONT, 11), text_color=C.SIDE_MUTED,
                     anchor="e").pack(side="right", padx=16, fill="y")

        # ── Cuerpo: sidebar + contenido ──
        body = ctk.CTkFrame(root_frame, fg_color=C.BG, corner_radius=0)
        body.pack(fill="both", expand=True)

        # ── Sidebar ──
        side = ctk.CTkFrame(body, width=220, corner_radius=0,
                            fg_color=C.SIDE, border_width=0)
        side.pack(side="left", fill="y")
        side.pack_propagate(False)

        # Separador visual sutil
        ctk.CTkFrame(body, width=1, fg_color=C.CARD_BORDER,
                     corner_radius=0).pack(side="left", fill="y")

        ctk.CTkLabel(side, text="   MENU", font=(C.FONT, 10, "bold"),
                     text_color=C.SIDE_MUTED, anchor="w"
                     ).pack(fill="x", padx=14, pady=(20, 8))

        self.navs = {}
        for key, txt, ico in [("personal", "Personal", "\u2630"),
                              ("boleta", "Boleta de Pago", "\u2637"),
                              ("historico", "Historico de Pagos", "\u2616"),
                              ("config", "Configuracion", "\u2699")]:
            n = NavBtn(side, txt, ico, lambda k=key: self._go(k))
            n.pack(fill="x", padx=8, pady=1)
            self.navs[key] = n

        # Footer sidebar
        foot = ctk.CTkFrame(side, fg_color="transparent")
        foot.pack(side="bottom", fill="x", padx=16, pady=12)
        ctk.CTkFrame(foot, height=1, fg_color=C.SIDE_HOVER).pack(fill="x", pady=(0, 10))
        ctk.CTkLabel(foot, text="v2.0", font=(C.FONT, 10),
                     text_color=C.SIDE_MUTED, anchor="w").pack(side="left")
        ctk.CTkLabel(foot, text="CNI", font=(C.FONT, 10, "bold"),
                     text_color=C.SIDE_ACCENT, anchor="e").pack(side="right")

        # ── Contenido principal ──
        self.content = ctk.CTkFrame(body, fg_color=C.BG, corner_radius=0)
        self.content.pack(side="right", fill="both", expand=True, padx=20, pady=16)

        self.panels = {
            "personal": PersonalPanel(self.content, self.db),
            "boleta": BoletaPanel(self.content, self.db),
            "historico": HistoricoPanel(self.content, self.db),
            "config": ConfigPanel(self.content, self.db),
        }

        self._go("personal")
        self.protocol("WM_DELETE_WINDOW", self._close)

        # ── Mostrar ventana ya lista (sin flicker) ──
        self.after(50, self._show)

    def _show(self):
        self.deiconify()
        self.lift()
        self.focus_force()

    def _go(self, key):
        for k, n in self.navs.items():
            n.active(k == key)
        for p in self.panels.values():
            p.pack_forget()
        self.panels[key].pack(fill="both", expand=True)
        if key == "boleta":
            self.panels["boleta"].refresh()
        if key == "historico":
            self.panels["historico"].refresh()

    def _close(self):
        self.db.close()
        self.destroy()


if __name__ == "__main__":
    App().mainloop()
