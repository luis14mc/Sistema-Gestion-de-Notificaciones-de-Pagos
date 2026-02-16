# 📘 Manual Técnico - Sistema de Pagos CNI

**Consejo Nacional de Inversiones - Honduras**  
Versión 2.1.0 - Febrero 2026

---

## 📑 Tabla de Contenidos

1. [Arquitectura del Sistema](#arquitectura-del-sistema)
2. [Estructura de Archivos](#estructura-de-archivos)
3. [Base de Datos](#base-de-datos)
4. [APIs REST](#apis-rest)
5. [Lógica de Negocio](#lógica-de-negocio)
6. [Frontend](#frontend)
7. [Seguridad](#seguridad)
8. [Desarrollo y Mantenimiento](#desarrollo-y-mantenimiento)

---

## 🏗️ Arquitectura del Sistema

### Arquitectura General

```
┌─────────────────────────────────────────┐
│         Aplicación Desktop              │
│         (PyWebView + Flask)             │
├─────────────────────────────────────────┤
│                                         │
│  ┌────────────┐      ┌──────────────┐  │
│  │  Frontend  │◄────►│   Backend    │  │
│  │  HTML/CSS  │      │    Flask     │  │
│  │ JavaScript │      │    Python    │  │
│  └────────────┘      └───────┬──────┘  │
│                              │          │
│                      ┌───────▼──────┐   │
│                      │   SQLite     │   │
│                      │  rrhh_cni.db │   │
│                      └──────────────┘   │
│                                         │
│  ┌─────────────┐    ┌──────────────┐   │
│  │  Generación │    │    Email     │   │
│  │     PDF     │    │    SMTP      │   │
│  └─────────────┘    └──────────────┘   │
└─────────────────────────────────────────┘
```

### Componentes Principales

1. **`app.py`**: Punto de entrada de la aplicación desktop
2. **`server.py`**: Servidor Flask con toda la lógica backend
3. **`templates/index.html`**: SPA (Single Page Application) del frontend
4. **`rrhh_cni.db`**: Base de datos SQLite
5. **`static/`**: Recursos estáticos (logo, etc.)

---

## 📁 Estructura de Archivos

```
app_rrhh_cni/
├── app.py                    # Aplicación desktop (PyWebView)
├── server.py                 # Backend Flask + Lógica de negocio
├── requirements.txt          # Dependencias Python
├── README.md                 # Documentación principal
├── MANUAL_TECNICO.md         # Este archivo
├── MANUAL_USUARIO.md         # Guía de usuario
├── .gitignore               # Archivos excluidos de Git
│
├── templates/
│   └── index.html           # Frontend SPA (HTML + CSS + JS)
│
├── static/
│   └── logo_cni.png         # Logo institucional
│
├── rrhh_cni.db              # Base de datos SQLite
│
└── reportes_pagos_RRHH/     # PDFs generados (auto-creado)
    ├── 2026/
    │   ├── 01/
    │   └── 02/
    └── auditoria/
```

---

## 🗄️ Base de Datos

### Esquema SQLite

#### Tabla: `empleados`

Almacena información de los empleados.

```sql
CREATE TABLE empleados (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cod_empleado TEXT UNIQUE NOT NULL,
    nombre_empleado TEXT NOT NULL,
    cargo TEXT NOT NULL,
    salario_mensual REAL NOT NULL,
    ihss REAL DEFAULT 0,
    isr REAL DEFAULT 0,
    otro REAL DEFAULT 0,
    observacion_otro TEXT DEFAULT '',
    correo_institucional TEXT DEFAULT ''
);
```

#### Tabla: `smtp_config`

Configuración del servidor SMTP (Office 365).

```sql
CREATE TABLE smtp_config (
    id INTEGER PRIMARY KEY CHECK (id=1),
    servidor TEXT DEFAULT 'smtp.office365.com',
    puerto INTEGER DEFAULT 587,
    usuario TEXT DEFAULT '',
    contrasena TEXT DEFAULT '',
    emisor TEXT DEFAULT 'Servicios Online',
    remitente_display TEXT DEFAULT ''
);
```

#### Tabla: `historico_pagos`

Registro histórico de boletas generadas.

```sql
CREATE TABLE historico_pagos (
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
);
```

#### Tabla: `isr_tramos`

Tabla progresiva de ISR configurable.

```sql
CREATE TABLE isr_tramos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tasa REAL NOT NULL,
    desde_mensual REAL NOT NULL,
    hasta_mensual REAL NOT NULL,
    descripcion TEXT DEFAULT ''
);
```

**Datos iniciales 2026**:
- 0% exento: L. 0.01 - L. 22,360.36
- 15%: L. 22,360.37 - L. 32,346.18
- 20%: L. 32,346.19 - L. 70,805.06
- 25%: L. 70,805.07 en adelante

#### Tabla: `ihss_config`

Configuración de tasas IHSS.

```sql
CREATE TABLE ihss_config (
    id INTEGER PRIMARY KEY CHECK (id=1),
    tasa_em REAL DEFAULT 2.5,
    tasa_ivm REAL DEFAULT 2.5,
    techo_mensual REAL DEFAULT 12000.00
);
```

---

## 🔌 APIs REST

Todas las APIs devuelven JSON. Base URL: `http://localhost:5000/api`

### Empleados

#### `GET /api/empleados`
Obtiene lista de todos los empleados.

**Query params**:
- `q` (opcional): Filtro de búsqueda por nombre o código

**Response**:
```json
[
  {
    "id": 1,
    "cod_empleado": "CNI001",
    "nombre_empleado": "Juan Pérez",
    "cargo": "Analista",
    "salario_mensual": 25000.00,
    "ihss": 625.00,
    "isr": 1200.50,
    "otro": 0,
    "observacion_otro": "",
    "correo_institucional": "juan.perez@cni.hn"
  }
]
```

#### `POST /api/empleados`
Crea un nuevo empleado.

**Body**:
```json
{
  "cod_empleado": "CNI002",
  "nombre_empleado": "María López",
  "cargo": "Coordinadora",
  "salario_mensual": 30000.00,
  "otro": 0,
  "observacion_otro": "",
  "correo_institucional": "maria.lopez@cni.hn"
}
```

**Response**:
```json
{
  "ok": true,
  "isr_calculado": 1500.75,
  "ihss_calculado": 750.00
}
```

#### `PUT /api/empleados/<id>`
Actualiza un empleado existente.

#### `DELETE /api/empleados/<id>`
Elimina un empleado.

#### `GET /api/next_cod`
Obtiene el siguiente código de empleado secuencial.

**Response**:
```json
{
  "next_cod": "CNI003"
}
```

---

### Boletas de Pago

#### `POST /api/boleta`
Genera boleta de pago individual.

**Body**:
```json
{
  "empleado_id": 1,
  "fecha_inicio": "01/02/2026",
  "fecha_fin": "28/02/2026",
  "modo": "PDF"  // "PDF", "Email", "Both"
}
```

**Response**:
```json
{
  "ok": true,
  "mensaje": "Boleta generada exitosamente",
  "ruta": "reportes_pagos_RRHH/2026/02/Boleta_CNI001_01-02-28-02.pdf"
}
```

#### `POST /api/boleta/batch`
Genera boletas para todos los empleados.

**Body**:
```json
{
  "fecha_inicio": "01/02/2026",
  "fecha_fin": "28/02/2026",
  "modo": "PDF"
}
```

**Response**:
```json
{
  "exitosos": 45,
  "fallidos": 2,
  "total": 47,
  "errores": [
    {
      "empleado": "Pedro García",
      "error": "No tiene correo institucional"
    }
  ]
}
```

---

### Configuración ISR

#### `GET /api/isr/tramos`
Obtiene la tabla progresiva de ISR.

**Response**:
```json
[
  {
    "id": 1,
    "tasa": 0.0,
    "desde_mensual": 0.01,
    "hasta_mensual": 22360.36,
    "descripcion": "Exentos"
  },
  ...
]
```

#### `POST /api/isr/tramos`
Actualiza la tabla completa de ISR.

**Body**:
```json
{
  "tramos": [
    {
      "tasa": 0,
      "desde_mensual": 0.01,
      "hasta_mensual": 22360.36,
      "descripcion": "Exentos"
    },
    ...
  ]
}
```

#### `GET /api/isr/calcular?salario=25000`
Calcula ISR para un salario dado.

**Response**:
```json
{
  "isr_mensual": 1200.50
}
```

#### `POST /api/isr/recalcular`
Recalcula ISR de todos los empleados con la tabla actual.

---

### Configuración IHSS

#### `GET /api/ihss`
Obtiene configuración de IHSS.

**Response**:
```json
{
  "tasa_em": 2.5,
  "tasa_ivm": 2.5,
  "techo_mensual": 12000.00
}
```

#### `POST /api/ihss`
Actualiza configuración de IHSS.

**Body**:
```json
{
  "tasa_em": 2.5,
  "tasa_ivm": 2.5,
  "techo_mensual": 12000.00
}
```

#### `POST /api/ihss/recalcular`
Recalcula IHSS de todos los empleados.

---

### Histórico

#### `GET /api/historico`
Obtiene histórico de pagos con filtros opcionales.

**Query params**:
- `emp` (opcional): Nombre o código del empleado
- `fi` (opcional): Fecha inicio filtro (DD/MM/AAAA)
- `ff` (opcional): Fecha fin filtro (DD/MM/AAAA)

**Response**:
```json
{
  "rows": [...],
  "stats": {
    "total": 47,
    "neto": 7125000.50,
    "deducciones": 425000.00
  }
}
```

**Notas del Frontend**:
- Los resultados se ordenan por fecha de mayor a menor (más reciente primero)
- La tabla muestra solo: Fecha, Código, Empleado, Cargo, Tipo y botón "Ver"
- Paginación de 10 registros por página
- Modal de detalle con desglose financiero completo al hacer clic en "Ver"

#### `POST /api/historico/exportar`
Genera reporte PDF de auditoría con logo CNI y colores institucionales.

---

### Configuración SMTP

#### `GET /api/smtp`
Obtiene configuración SMTP (sin contraseña).

#### `POST /api/smtp`
Actualiza configuración SMTP.

---

## ⚙️ Lógica de Negocio

### Cálculo de ISR

**Función**: `_calcular_isr(salario, db)`

**Algoritmo**:
1. Obtiene tramos de la tabla `isr_tramos`
2. Aplica cálculo progresivo:
   - Para cada tramo, calcula la porción gravable
   - Aplica la tasa correspondiente
   - Suma todos los impuestos parciales
3. Retorna ISR mensual redondeado a 2 decimales

**Ejemplo** (salario L. 30,000):
```
Tramo 1 (0%):     22,360.36 × 0%    = L.     0.00
Tramo 2 (15%):     9,985.82 × 15%   = L. 1,497.87
Tramo 3 (20%):       653.82 × 20%   = L.   130.76
Total ISR mensual:                   = L. 1,628.63
```

---

### Cálculo de IHSS

**Función**: `_calcular_ihss(salario, db)`

**Fórmula**:
```
Salario Base = MIN(Salario Real, Techo de Cotización)
IHSS Total = Salario Base × (Tasa EM + Tasa IVM) / 100
```

**Ejemplo** (salario L. 30,000, techo L. 12,000):
```
Salario Base = MIN(30,000, 12,000) = 12,000
IHSS = 12,000 × (2.5% + 2.5%) = 12,000 × 5% = L. 600.00
```

---

### Generación de PDF

**Clase**: `BoletaPDF(FPDF)`

**Estructura del PDF**:
1. **Header**: Fondo azul CNI, logo `img/logo_cni.png`, línea decorativa cyan
2. **Texto**: "BOLETA DE PAGO" + "Consejo Nacional de Inversiones - Honduras, C.A."
3. **Datos del empleado**: Código, nombre, cargo, correo, período (labels en azul CNI)
4. **Ingresos**: Sección con header verde CNI, salario mensual y total
5. **Deducciones**: Sección con header rojo, IHSS, ISR, Otro (si aplica), total
6. **Salario Neto**: Barra azul CNI prominente con texto blanco
7. **Footer**: Línea separadora azul, fecha de generación, versión del sistema

**Colores Institucionales**:
- `CNI_BLUE`: RGB(35, 57, 129) - #233981 - Header, labels, salario neto
- `CNI_CYAN`: RGB(42, 170, 214) - #2AAAD6 - Línea decorativa
- `CNI_GREEN`: RGB(27, 174, 100) - #1BAE64 - Sección ingresos
- Deducciones: RGB(180, 40, 40) - Rojo oscuro

**Reporte de Auditoría**:
- Header con logo CNI y fondo azul institucional
- Línea cyan decorativa bajo el header
- Encabezados de tabla en azul CNI
- Filas alternas para legibilidad
- Footer con total de registros y fecha

---

### Envío de Email

**Función**: `_enviar_email(smtp_cfg, emp, fi, ff, ruta_pdf)`

**Proceso**:
1. Valida configuración SMTP y correo del empleado
2. Calcula desglose: salario, IHSS, ISR, otro, total deducciones, neto
3. Genera HTML del email con diseño corporativo limpio
4. Adjunta PDF si existe
5. Envía vía SMTP (Office 365, puerto 587, STARTTLS)

**Formato HTML del Email**:
- Diseño table-based para máxima compatibilidad con clientes de correo
- `color-scheme: light only` para evitar alteraciones en modo oscuro
- Fondo blanco, header azul CNI (#233981)
- Tabla de conceptos: salario, deducciones (rojo #cc0000), neto (azul CNI)
- Paleta limitada: solo #233981, #ffffff, #333333, #cc0000
- Compatible con Outlook, Gmail, Apple Mail, Thunderbird

---

## 🎨 Frontend

### Tecnologías

- **HTML5**: Estructura semántica
- **Tailwind CSS 3**: Utilidades y diseño
- **JavaScript Vanilla**: Lógica de interfaz
- **SweetAlert2**: Diálogos interactivos

### Arquitectura SPA

**Single Page Application** - Un solo HTML con navegación por paneles:

```javascript
function go(key) {
  // Oculta todos los paneles
  document.querySelectorAll('.panel').forEach(p => 
    p.classList.remove('active')
  );
  
  // Muestra el panel seleccionado
  document.getElementById('p-'+key).classList.add('active');
  
  // Actualiza menú
  updateNavigation(key);
}
```

### Paneles Principales

1. **Personal** (`#p-personal`): Gestión de empleados
2. **Boleta de Pago** (`#p-boleta`): Generación de boletas
3. **Histórico de Pagos** (`#p-historico`): Consulta y reportes
4. **Configuración** (`#p-config`): ISR, IHSS, SMTP

### Funciones JavaScript Clave

- `loadEmpleados()`: Carga lista de empleados
- `showForm(id)`: Muestra formulario de edición
- `saveEmpleado()`: Guarda empleado (POST/PUT)
- `updateFormISR()`: Calcula ISR automáticamente
- `previewBoleta()`: Genera vista previa de boleta
- `generarTodos()`: Generación masiva de boletas
- `loadHistorico()`: Carga histórico con filtros

---

## 🔒 Seguridad

### Consideraciones

1. **Sin autenticación**: Aplicación de escritorio para uso interno
2. **Base de datos local**: SQLite en filesystem
3. **Contraseñas SMTP**: Almacenadas en texto plano (usar .env para producción)
4. **Sin HTTPS**: Servidor local (127.0.0.1)

### Recomendaciones

- No exponer el puerto Flask externamente
- Mantener actualizadas las dependencias
- Realizar backups periódicos de `rrhh_cni.db`
- Usar variables de entorno para credenciales en producción

---

## 🔧 Desarrollo y Mantenimiento

### Entorno de Desarrollo

```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar en modo desarrollo
python server.py
```

### Debug Mode

Activar debug en `server.py`:

```python
if __name__ == '__main__':
    app.run(debug=True, port=5000)
```

### Base de Datos

**Backup**:
```bash
sqlite3 rrhh_cni.db ".backup rrhh_cni_backup.db"
```

**Restaurar**:
```bash
cp rrhh_cni_backup.db rrhh_cni.db
```

### Testing

**Probar APIs manualmente**:
```bash
# Obtener empleados
curl http://localhost:5000/api/empleados

# Calcular ISR
curl "http://localhost:5000/api/calcular_isr?salario=25000"
```

---

## 📊 Métricas y Logs

### Logs de Aplicación

Los logs se muestran en consola durante ejecución.

### Monitoreo

- Total de empleados: `SELECT COUNT(*) FROM empleados`
- Boletas generadas hoy: `SELECT COUNT(*) FROM historico_pagos WHERE fecha_generacion = date('now')`
- Espacio en disco: Verificar carpeta `reportes_pagos_RRHH/`

---

## 🔄 Actualizaciones

### Migración de Base de Datos

El sistema incluye migraciones automáticas en `init_db()`:

```python
# Agregar nueva columna si no existe
cols = {r[1] for r in c.execute("PRAGMA table_info(empleados)").fetchall()}
if "nueva_columna" not in cols:
    c.execute("ALTER TABLE empleados ADD COLUMN nueva_columna TEXT DEFAULT ''")
```

### Versionamiento

- Mantener versionado semántico: MAJOR.MINOR.PATCH
- Actualizar `README.md` con changelog
- Crear tags en Git para cada versión

---

## 📞 Contacto Técnico

### Desarrollador del Sistema
Para dudas técnicas, bugs o desarrollo:
- **Nombre**: Ing. Luis Martínez
- **Rol**: Software Developer
- **Email**: luismartinez.94mc@gmail.com

### Soporte CNI (Interno)
Para soporte operativo y configuración:
- **Departamento**: Oficial de TI
- **Email**: amartinez@cni.hn
- **Organización**: Consejo Nacional de Inversiones

---

**Última actualización**: 11 de Febrero 2026  
**Versión del Sistema**: 2.0.0  
**Versión del Manual**: 2.0  
**Estado**: Producción
