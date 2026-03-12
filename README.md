# 💼 Sistema de Pagos - CNI Honduras

**Sistema de Gestión de Recursos Humanos y Nómina**  
Consejo Nacional de Inversiones - Honduras

![Version](https://img.shields.io/badge/version-2.2.0-blue)
![Release](https://img.shields.io/badge/release-Feb_2026-brightgreen)
![Python](https://img.shields.io/badge/python-3.8+-green)
![Flask](https://img.shields.io/badge/flask-3.0-red)
![License](https://img.shields.io/badge/license-Privado-orange)
![Status](https://img.shields.io/badge/status-Production-success)

---

## 📋 Descripción

Sistema integral para la gestión de recursos humanos, nómina y generación de boletas de pago del Consejo Nacional de Inversiones de Honduras.

### ✨ Características Principales

- **Gestión de Personal**: CRUD completo de empleados con cálculos automáticos
- **Boletas de Pago**: Generación individual y masiva con exportación a PDF
- **Cálculos Automáticos**: 
  - ISR (Impuesto Sobre la Renta) con tabla progresiva, prorrateo por fecha de ingreso
  - IHSS (EM + IVM) con tasas configurables, prorrateado en primer mes
- **Histórico de Pagos**: Registro completo con reportes de auditoría
- **Envío por Email**: Distribución automática de boletas vía Office 365
- **Interfaz Moderna**: Diseño responsive con colores institucionales CNI

---

## 🚀 Instalación

### Opción 1: Ejecutable Pre-compilado (Recomendado para Usuarios)

**Descarga el ejecutable para Windows:**

- **Windows:** `SistemaPagosCNI_v2.2.0_Windows.zip` (~150-200 MB) — [Releases](https://github.com/luis14mc/Sistema-Gestion-de-Notificaciones-de-Pagos/releases)

**Instrucciones:** Extraer el ZIP, ejecutar `SistemaPagosCNI.exe`. El sistema está diseñado para Windows.

### Opción 2: Instalación desde Código Fuente (Para Desarrolladores)

#### Requisitos Previos

- Python 3.8 o superior
- pip (gestor de paquetes Python)
- Sistema operativo: Windows, Linux o macOS

#### Instalación Rápida

1. **Clonar el repositorio**:
```bash
git clone https://github.com/luis14mc/Sistema-Gestion-de-Notificaciones-de-Pagos.git
cd app_rrhh_cni
```

2. **Instalar dependencias**:
```bash
pip install -r requirements.txt
```

3. **Ejecutar la aplicación**:

**Modo Web**:
```bash
python server.py
```
Abrir en navegador: `http://localhost:5000`

**Modo Aplicación de Escritorio**:
```bash
python app.py
```

---

## 📦 Compilar Ejecutable (Windows)

**⚠️ Debes compilar en Windows nativo** (no WSL) para crear el `.exe`:

```cmd
pip install -r requirements.txt
build.bat
```

El ejecutable se genera en `dist\SistemaPagosCNI\SistemaPagosCNI.exe`. Para distribuir, comprimir esa carpeta en `SistemaPagosCNI_v2.2.0_Windows.zip`.

---

## 🎯 Uso Rápido

1. **Configurar SMTP**: Ir a Configuración y establecer credenciales de Office 365
2. **Configurar IHSS**: Establecer tasas EM, IVM y techo de cotización
3. **Revisar Tabla ISR**: Verificar/ajustar tramos de impuesto sobre la renta
4. **Agregar Empleados**: Ir a Personal → Nuevo Empleado
5. **Generar Boletas**: Seleccionar empleado, establecer período y generar

---

## 🛠️ Tecnologías

- **Backend**: Python 3, Flask 3.0
- **Frontend**: HTML5, Tailwind CSS 3, JavaScript
- **Base de Datos**: SQLite3
- **PDFs**: FPDF2
- **Email**: SMTP (Office 365)
- **Desktop**: PyWebView

---

## 🎨 Colores Institucionales

- **Azul CNI**: `#233981`
- **Cyan**: `#2AAAD6`
- **Verde**: `#1BAE64`

---

## 📞 Soporte

### Desarrollador
- **Nombre**: Ing. Luis Martínez
- **Rol**: Software Developer
- **Email**: luismartinez.94mc@gmail.com

### Contacto CNI (Soporte Interno)
- **Departamento**: Oficial de TI
- **Email**: amartinez@cni.hn

---

## 📄 Licencia

© 2026 Consejo Nacional de Inversiones - Honduras.  
Software de uso interno. Todos los derechos reservados.

---

## 🔄 Historial de Versiones

### v2.2.0 - Febrero 2026 (Actual)
- Salario prorrateado primer mes según fecha de ingreso: `(Salario/30) × días trabajados`
- ISR con ingreso anual proyectado: salario primer mes + (salario × meses restantes)
- IHSS calculado sobre salario efectivo del periodo (prorrateado en primer mes)
- Configuración IHSS con EM + IVM
- Fecha de ingreso laboral en formulario de empleados

### v2.1.0 - Febrero 16, 2026
- Selector de mes en Boleta de Pago (periodo del 20 al 20 automatico)
- Historico de Pagos rediseñado: tabla simplificada, paginacion, modal de detalle
- PDFs con logo CNI y colores institucionales (boleta y auditoria)
- Email corporativo limpio, fondo blanco, compatible modo oscuro
- Validacion de fechas en formularios
- Reporte de auditoria con branding CNI

### v2.0.0 - Febrero 11, 2026
**Estado**: ✅ Producción

**Nuevas Características**:
- ✨ Migración completa a aplicación web Flask + PyWebView
- 🎨 Interfaz moderna con Tailwind CSS 3
- 🧮 Cálculo automático de ISR con tabla progresiva configurable
- 💰 Cálculo automático de IHSS con tasas y techo configurables
- 📄 Generación individual y masiva de boletas PDF
- 📧 Envío automático de boletas por email (Office 365)
- 📊 Histórico de pagos con filtros y reportes de auditoría
- 🎨 Implementación de colores institucionales CNI
- 📚 Documentación completa (3 manuales profesionales)
- 🔐 Sistema de configuración integrado (ISR, IHSS, SMTP)
- 🖥️ Modo desktop con ventana nativa

**Mejoras Técnicas**:
- Arquitectura SPA (Single Page Application)
- APIs REST completas
- Base de datos SQLite optimizada
- Código modularizado y documentado
- Control de versiones Git implementado

**Desarrollado por**: Ing. Luis Martínez - Software Developer  
**Email**: luismartinez.94mc@gmail.com

---

### v1.0 (2025)
**Estado**: ⚠️ Deprecado

- Versión inicial desktop con Tkinter
- Funcionalidades básicas de nómina
- Sin cálculos automáticos
