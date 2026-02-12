# 💼 Sistema de Pagos - CNI Honduras

**Sistema de Gestión de Recursos Humanos y Nómina**  
Consejo Nacional de Inversiones - Honduras

![Version](https://img.shields.io/badge/version-2.0-blue)
![Python](https://img.shields.io/badge/python-3.8+-green)
![Flask](https://img.shields.io/badge/flask-3.0-red)
![License](https://img.shields.io/badge/license-Privado-orange)

---

## 📋 Descripción

Sistema integral para la gestión de recursos humanos, nómina y generación de boletas de pago del Consejo Nacional de Inversiones de Honduras.

### ✨ Características Principales

- **Gestión de Personal**: CRUD completo de empleados con cálculos automáticos
- **Boletas de Pago**: Generación individual y masiva con exportación a PDF
- **Cálculos Automáticos**: 
  - ISR (Impuesto Sobre la Renta) con tabla progresiva configurable
  - IHSS (Instituto Hondureño de Seguridad Social) con tasas configurables
- **Histórico de Pagos**: Registro completo con reportes de auditoría
- **Envío por Email**: Distribución automática de boletas vía Office 365
- **Interfaz Moderna**: Diseño responsive con colores institucionales CNI

---

## 🚀 Instalación

### Requisitos Previos

- Python 3.8 o superior
- pip (gestor de paquetes Python)
- Sistema operativo: Windows, Linux o macOS

### Instalación Rápida

1. **Clonar el repositorio**:
```bash
git clone <URL_DEL_REPOSITORIO>
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

## 📦 Empaquetar como Ejecutable

Para crear un ejecutable independiente:

```bash
pyinstaller --name="Sistema_Pagos_CNI" \
            --windowed \
            --onefile \
            --icon=static/logo_cni.png \
            --add-data="templates:templates" \
            --add-data="static:static" \
            app.py
```

El ejecutable se generará en la carpeta `dist/`.

---

## 🎯 Uso Rápido

1. **Configurar SMTP**: Ir a Configuración y establecer credenciales de Office 365
2. **Configurar IHSS**: Establecer tasas EM, IVM y techo de cotización
3. **Revisar Tabla ISR**: Verificar/ajustar tramos de impuesto sobre la renta
4. **Agregar Empleados**: Ir a Personal → Nuevo Empleado
5. **Generar Boletas**: Seleccionar empleado, establecer período y generar

---

## 📚 Documentación

- **[Manual de Usuario](MANUAL_USUARIO.md)**: Guía detallada paso a paso
- **[Manual Técnico](MANUAL_TECNICO.md)**: Arquitectura, APIs y desarrollo

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

Para consultas técnicas o soporte, contactar al departamento de TI del Consejo Nacional de Inversiones.

---

## 📄 Licencia

© 2026 Consejo Nacional de Inversiones - Honduras.  
Software de uso interno. Todos los derechos reservados.

---

## 🔄 Versiones

### v2.0 (Febrero 2026)
- Migración a aplicación web con Flask
- Interfaz moderna con Tailwind CSS
- Cálculos automáticos de ISR e IHSS
- Generación masiva de boletas
- Colores institucionales CNI
- Manual de usuario y técnico

### v1.0 (2025)
- Versión inicial desktop con Tkinter
- Funcionalidades básicas de nómina
