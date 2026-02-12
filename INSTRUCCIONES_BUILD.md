# Instrucciones de Compilación - Sistema de Pagos CNI

## Consejo Nacional de Inversiones - Honduras

**Versión:** 2.0.0  
**Desarrollado por:** Ing. Luis Martínez  
**Email:** luismartinez.94mc@gmail.com  
**Soporte CNI:** Oficial de TI - amartinez@cni.hn

---

## Requisitos Previos

### 1. Python 3.8 o superior

Verifica tu versión de Python:

```bash
python --version
# o en Linux/Mac:
python3 --version
```

Si no tienes Python instalado:
- **Windows:** Descarga desde https://www.python.org/downloads/
- **Linux:** `sudo apt install python3 python3-pip`
- **Mac:** `brew install python3`

### 2. Dependencias del Sistema

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install -y python3-dev python3-pip
sudo apt install -y libgtk-3-dev libwebkit2gtk-4.0-dev
sudo apt install -y gir1.2-webkit2-4.0
```

**Mac:**
```bash
brew install python3
# PyWebView usa WebKit nativo, no requiere instalación adicional
```

**Windows:**
- PyWebView usa Edge WebView2 (ya incluido en Windows 10/11)
- No requiere instalación adicional

---

## Proceso de Compilación

### Opción 1: Script Automático (Recomendado)

#### En Windows:

1. Abre PowerShell o CMD en el directorio del proyecto
2. Ejecuta:
   ```cmd
   build.bat
   ```

#### En Linux/Mac:

1. Abre una terminal en el directorio del proyecto
2. Dale permisos de ejecución al script:
   ```bash
   chmod +x build.sh
   ```
3. Ejecuta:
   ```bash
   ./build.sh
   ```

### Opción 2: Manual

#### Paso 1: Instalar Dependencias

```bash
# Instalar todas las dependencias del proyecto
pip install -r requirements.txt

# Instalar PyInstaller si no está incluido
pip install pyinstaller
```

#### Paso 2: Limpiar Builds Anteriores (Opcional)

```bash
# Windows
rmdir /s /q build dist
del /s /q *.pyc

# Linux/Mac
rm -rf build/ dist/ __pycache__/
find . -type d -name "__pycache__" -exec rm -rf {} +
```

#### Paso 3: Compilar con PyInstaller

```bash
pyinstaller --clean app_rrhh_cni.spec
```

---

## Resultado de la Compilación

Después de la compilación exitosa, encontrarás:

```
dist/
└── SistemaPagosCNI/
    ├── SistemaPagosCNI         # Ejecutable (Linux/Mac)
    ├── SistemaPagosCNI.exe      # Ejecutable (Windows)
    ├── templates/               # Plantillas HTML
    ├── static/                  # Archivos estáticos (CSS, JS, imágenes)
    ├── img/                     # Imágenes del proyecto
    └── [muchos otros archivos de librerías]
```

### Tamaño Aproximado

- **Windows:** ~150-200 MB
- **Linux:** ~120-150 MB
- **Mac:** ~130-160 MB

---

## Probar el Ejecutable

### Windows:

```cmd
cd dist\SistemaPagosCNI
SistemaPagosCNI.exe
```

### Linux/Mac:

```bash
cd dist/SistemaPagosCNI
./SistemaPagosCNI
```

---

## Distribución

### Para Usuarios Finales

1. **Comprimir la carpeta completa:**
   - Windows: Clic derecho en `dist/SistemaPagosCNI` → "Enviar a" → "Carpeta comprimida"
   - Linux/Mac: `zip -r SistemaPagosCNI_v2.0.0.zip dist/SistemaPagosCNI/`

2. **Enviar el archivo comprimido** a los usuarios

3. **Instrucciones para el usuario:**
   - Descomprimir el archivo en cualquier carpeta
   - Ejecutar `SistemaPagosCNI.exe` (Windows) o `SistemaPagosCNI` (Linux/Mac)
   - **NO** mover ni eliminar ningún archivo de la carpeta

### Crear Instalador (Opcional)

#### Windows con Inno Setup:

1. Instala Inno Setup: https://jrsoftware.org/isinfo.php
2. Crea un archivo `installer.iss`:

```ini
[Setup]
AppName=Sistema de Pagos CNI
AppVersion=2.0.0
DefaultDirName={pf}\SistemaPagosCNI
DefaultGroupName=CNI
OutputDir=installers
OutputBaseFilename=SistemaPagosCNI_Setup_v2.0.0

[Files]
Source: "dist\SistemaPagosCNI\*"; DestDir: "{app}"; Flags: recursesubdirs

[Icons]
Name: "{group}\Sistema de Pagos CNI"; Filename: "{app}\SistemaPagosCNI.exe"
Name: "{commondesktop}\Sistema de Pagos CNI"; Filename: "{app}\SistemaPagosCNI.exe"
```

3. Compila con Inno Setup para crear un instalador `.exe`

---

## Solución de Problemas

### Error: "No se encuentra Flask"

**Solución:**
```bash
pip install -r requirements.txt
```

### Error: "PyInstaller no se encuentra"

**Solución:**
```bash
pip install pyinstaller
```

### Error en Linux: "No module named 'gi'"

**Solución:**
```bash
sudo apt install python3-gi python3-gi-cairo gir1.2-gtk-3.0 gir1.2-webkit2-4.0
```

### El ejecutable no inicia (Windows)

**Posibles causas:**
1. Falta WebView2 Runtime
   - Descarga: https://developer.microsoft.com/en-us/microsoft-edge/webview2/
2. Antivirus bloqueando el ejecutable
   - Agrega una excepción para la carpeta del programa
3. Archivos DLL faltantes
   - Instala Visual C++ Redistributable: https://aka.ms/vs/17/release/vc_redist.x64.exe

### El ejecutable es muy grande

**Es normal.** PyInstaller empaqueta Python y todas las librerías necesarias. Para reducir tamaño:

1. Usa UPX (ya habilitado en el `.spec`):
   ```bash
   # Instalar UPX
   # Windows: Descarga de https://upx.github.io/
   # Linux: sudo apt install upx-ucl
   # Mac: brew install upx
   ```

2. Compila en modo optimizado:
   ```bash
   python -O -m PyInstaller app_rrhh_cni.spec
   ```

### Base de datos no se crea

**Solución:** La base de datos `rrhh_cni.db` se crea automáticamente en el primer arranque. Si hay problemas:

1. Verifica permisos de escritura en la carpeta
2. Ejecuta la aplicación como administrador (solo la primera vez)
3. Revisa los logs en la consola

---

## Compilación Cruzada

### Compilar para Windows desde Linux (Wine)

```bash
# Instalar Wine
sudo apt install wine64 python3-wine

# Instalar Python en Wine
wine python-3.11.0-amd64.exe

# Compilar
wine pyinstaller app_rrhh_cni.spec
```

**Nota:** La compilación cruzada es compleja y puede tener problemas. Se recomienda compilar en el sistema operativo objetivo.

---

## Personalización del Ejecutable

### Cambiar el Icono

1. Crea o descarga un archivo `.ico` (Windows) o `.icns` (Mac)
2. Edita `app_rrhh_cni.spec`:
   ```python
   exe = EXE(
       ...
       icon='img/logo_cni.ico',  # Ruta a tu icono
       ...
   )
   ```

### Cambiar el Nombre del Ejecutable

Edita `app_rrhh_cni.spec`:
```python
exe = EXE(
    ...
    name='MiNombrePersonalizado',
    ...
)
```

### Compilar en un Solo Archivo

Edita `app_rrhh_cni.spec`:
```python
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,      # Mover aquí
    a.zipfiles,      # Mover aquí
    a.datas,         # Mover aquí
    [],
    name='SistemaPagosCNI',
    ...
    onefile=True,    # Agregar esta línea
)

# ELIMINAR la sección COLLECT completamente
```

**Nota:** El modo `onefile` crea un único ejecutable pero es más lento al iniciar.

---

## Verificación de Calidad

### Checklist Pre-Distribución

- [ ] El ejecutable inicia correctamente
- [ ] Todas las funcionalidades funcionan (Personal, Boleta, Histórico, Config)
- [ ] Los PDFs se generan correctamente
- [ ] Los correos se envían correctamente (con configuración SMTP válida)
- [ ] La base de datos se crea automáticamente
- [ ] No hay errores en la consola
- [ ] El logo de CNI se muestra correctamente
- [ ] Los reportes se guardan en `reportes_pagos_RRHH/`

### Pruebas Recomendadas

1. **Instalación limpia:** Prueba en un sistema sin Python instalado
2. **Usuarios sin privilegios:** Prueba con un usuario no-administrador
3. **Rutas con espacios:** Instala en `C:\Archivos de Programa\` para probar
4. **Antivirus:** Verifica que no marque falsos positivos

---

## Actualizaciones

Para crear una nueva versión:

1. Actualiza el número de versión en:
   - `VERSION.txt`
   - `app.py` (docstring)
   - `server.py` (docstring)
   - `README.md`
   - `app_rrhh_cni.spec` (docstring)

2. Recompila con el script de build

3. Nombra el archivo comprimido con la versión:
   `SistemaPagosCNI_v2.0.0.zip`

---

## Soporte

**Desarrollador:**  
Ing. Luis Martínez  
Software Developer  
Email: luismartinez.94mc@gmail.com

**Soporte Interno CNI:**  
Oficial de TI  
Email: amartinez@cni.hn

**Documentación:**
- `README.md` - Información general del proyecto
- `MANUAL_TECNICO.md` - Documentación técnica completa
- `MANUAL_USUARIO.md` - Guía de usuario final
- `INSTRUCCIONES_GITHUB.md` - Gestión de código fuente

---

## Licencia y Uso

Este software es propiedad del **Consejo Nacional de Inversiones (CNI) - Honduras**.  
Uso exclusivo para fines institucionales.  
Prohibida su distribución o uso fuera del CNI sin autorización.

© 2026 CNI Honduras - Todos los derechos reservados.
