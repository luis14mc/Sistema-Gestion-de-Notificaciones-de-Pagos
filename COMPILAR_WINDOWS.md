# 🪟 Compilar para Windows - Sistema de Pagos CNI

## Consejo Nacional de Inversiones - Honduras

**Versión:** 2.1.0  
**Desarrollado por:** Ing. Luis Martínez  
**Email:** luismartinez.94mc@gmail.com

---

## ⚠️ IMPORTANTE

**PyInstaller no soporta compilación cruzada.** Debes compilar en Windows para crear un `.exe`.

Como estás en WSL (Windows Subsystem for Linux), tienes dos opciones:

---

## Opción 1: Compilar en Windows (Recomendado)

### Paso 1: Instalar Python en Windows

1. **Descargar Python:**
   - Ve a https://www.python.org/downloads/
   - Descarga Python 3.8 o superior (64 bits)
   - **IMPORTANTE:** Marca "Add Python to PATH" durante la instalación

2. **Verificar instalación:**
   ```cmd
   python --version
   pip --version
   ```

### Paso 2: Acceder a los Archivos desde Windows

Tus archivos de WSL están en:
```
\\wsl$\Ubuntu\home\luis\app_rrhh_cni\
```

O navega en el Explorador de Archivos a:
1. Este equipo
2. Linux (o el ícono de pingüino)
3. Ubuntu
4. home → luis → app_rrhh_cni

### Paso 3: Abrir PowerShell o CMD en la Carpeta

1. En el Explorador de Archivos, navega a la carpeta del proyecto
2. En la barra de direcciones, escribe `cmd` y presiona Enter
3. O Shift + Clic derecho → "Abrir PowerShell aquí"

### Paso 4: Instalar Dependencias en Windows

```cmd
REM Crear entorno virtual (opcional pero recomendado)
python -m venv venv_windows
venv_windows\Scripts\activate

REM Instalar dependencias
pip install -r requirements.txt
```

### Paso 5: Compilar

```cmd
REM Ejecutar el script de build
build.bat
```

### Paso 6: Verificar

El ejecutable estará en:
```
dist\SistemaPagosCNI\SistemaPagosCNI.exe
```

Pruébalo:
```cmd
cd dist\SistemaPagosCNI
SistemaPagosCNI.exe
```

### Paso 7: Crear Paquete de Distribución

```cmd
cd dist
tar -czf SistemaPagosCNI_v2.1.0_Windows.zip SistemaPagosCNI\
```

O usa 7-Zip / WinRAR:
1. Clic derecho en la carpeta `SistemaPagosCNI`
2. "Comprimir" → "SistemaPagosCNI_v2.1.0_Windows.zip"

---

## Opción 2: Usar Wine (Avanzado, No Recomendado)

Wine permite ejecutar aplicaciones Windows en Linux, pero es complejo y puede tener problemas.

### Instalar Wine

```bash
# En WSL Ubuntu
sudo dpkg --add-architecture i386
sudo apt update
sudo apt install -y wine64 wine32 winetricks

# Verificar
wine --version
```

### Instalar Python en Wine

```bash
# Descargar Python para Windows
wget https://www.python.org/ftp/python/3.11.0/python-3.11.0-amd64.exe

# Instalar en Wine
wine python-3.11.0-amd64.exe /quiet InstallAllUsers=1 PrependPath=1

# Esperar a que termine (puede tomar varios minutos)
```

### Instalar Dependencias

```bash
wine python -m pip install -r requirements.txt
```

### Compilar

```bash
wine pyinstaller app_rrhh_cni.spec
```

**⚠️ Problemas comunes con Wine:**
- Errores de dependencias
- PyWebView puede no funcionar correctamente
- El ejecutable puede no ser estable
- Proceso muy lento

---

## Opción 3: Compilar Remotamente (GitHub Actions)

Si tienes acceso a GitHub, puedes configurar GitHub Actions para compilar automáticamente.

### Crear `.github/workflows/build.yml`:

```yaml
name: Build Windows Executable

on:
  push:
    tags:
      - 'v*'
  workflow_dispatch:

jobs:
  build-windows:
    runs-on: windows-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    
    - name: Build with PyInstaller
      run: |
        pyinstaller app_rrhh_cni.spec
    
    - name: Create ZIP
      run: |
        Compress-Archive -Path dist/SistemaPagosCNI -DestinationPath SistemaPagosCNI_v2.1.0_Windows.zip
    
    - name: Upload artifact
      uses: actions/upload-artifact@v3
      with:
        name: windows-executable
        path: SistemaPagosCNI_v2.1.0_Windows.zip
```

Luego:
1. Sube el código a GitHub
2. Ve a "Actions" en tu repositorio
3. Ejecuta el workflow manualmente
4. Descarga el ejecutable compilado

---

## Comparación de Opciones

| Opción | Dificultad | Tiempo | Confiabilidad | Recomendado |
|--------|-----------|--------|---------------|-------------|
| **Compilar en Windows** | Fácil | 5-10 min | ✅ Alta | ✅ Sí |
| **Wine** | Difícil | 30-60 min | ⚠️ Media | ❌ No |
| **GitHub Actions** | Media | 10-15 min | ✅ Alta | ✅ Sí |

---

## Instrucciones Detalladas - Compilar en Windows

### Pre-requisitos

1. **Windows 10 o superior** (64 bits)
2. **Python 3.8+** instalado en Windows
3. **Git para Windows** (opcional): https://git-scm.com/download/win

### Proceso Completo Paso a Paso

#### 1. Preparar el Entorno

```cmd
REM Abrir PowerShell como Administrador y habilitar scripts
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser

REM Navegar a la carpeta del proyecto
cd \\wsl$\Ubuntu\home\luis\app_rrhh_cni

REM O copiar todo a una carpeta Windows nativa (más rápido)
xcopy \\wsl$\Ubuntu\home\luis\app_rrhh_cni C:\Temp\app_rrhh_cni /E /I /H /Y
cd C:\Temp\app_rrhh_cni
```

#### 2. Crear Entorno Virtual

```cmd
REM Crear venv
python -m venv venv_windows

REM Activar venv
venv_windows\Scripts\activate

REM Verificar que estás en el venv
where python
REM Debería mostrar: C:\...\app_rrhh_cni\venv_windows\Scripts\python.exe
```

#### 3. Instalar Dependencias

```cmd
REM Actualizar pip
python -m pip install --upgrade pip

REM Instalar dependencias del proyecto
pip install -r requirements.txt

REM Verificar instalación
pip list
```

#### 4. Probar la Aplicación

Antes de compilar, prueba que funcione:

```cmd
REM Probar modo web
python server.py
REM Abrir http://localhost:5000 en navegador

REM Probar modo escritorio (Ctrl+C para cerrar server.py primero)
python app.py
```

#### 5. Compilar con PyInstaller

```cmd
REM Opción 1: Usar el script automatizado
build.bat

REM Opción 2: Compilar manualmente
pyinstaller --clean app_rrhh_cni.spec
```

#### 6. Verificar el Ejecutable

```cmd
REM Navegar a la carpeta de distribución
cd dist\SistemaPagosCNI

REM Listar archivos
dir

REM Ejecutar la aplicación
SistemaPagosCNI.exe
```

Verifica que:
- [ ] La aplicación inicia correctamente
- [ ] La interfaz se muestra bien
- [ ] Puedes agregar un empleado
- [ ] Puedes generar una boleta
- [ ] Los PDFs se crean correctamente

#### 7. Crear Paquete de Distribución

```cmd
REM Volver al directorio raíz
cd ..\..

REM Comprimir (si tienes tar en Windows)
cd dist
tar -czf SistemaPagosCNI_v2.1.0_Windows.zip SistemaPagosCNI

REM O comprimir con PowerShell
Compress-Archive -Path SistemaPagosCNI -DestinationPath SistemaPagosCNI_v2.1.0_Windows.zip

REM Verificar
dir *.zip
```

#### 8. Probar en Otra Máquina Windows

1. Copia el archivo `.zip` a otra computadora Windows (sin Python)
2. Descomprime
3. Ejecuta `SistemaPagosCNI.exe`
4. Verifica todas las funcionalidades

---

## Tamaño Esperado del Ejecutable

- **Descomprimido:** ~150-200 MB
- **Comprimido (ZIP):** ~50-70 MB

El ejecutable es grande porque incluye:
- Python runtime completo
- Flask y todas sus dependencias
- PyWebView y Edge WebView2
- FPDF2 y PIL (para PDFs)
- Todas las librerías necesarias

---

## Solución de Problemas en Windows

### Error: "Python no se reconoce como comando"

**Solución:**
1. Reinstala Python marcando "Add to PATH"
2. O agrega manualmente:
   - Panel de Control → Sistema → Configuración avanzada del sistema
   - Variables de entorno → Path → Editar
   - Agregar: `C:\Users\TuUsuario\AppData\Local\Programs\Python\Python311\`

### Error: "No module named 'XXX'"

**Solución:**
```cmd
pip install -r requirements.txt --force-reinstall
```

### Error: "pyinstaller no se reconoce"

**Solución:**
```cmd
pip install pyinstaller
# O si ya está instalado:
python -m PyInstaller app_rrhh_cni.spec
```

### El ejecutable no inicia

**Solución:**
1. Ejecuta desde cmd para ver errores:
   ```cmd
   cd dist\SistemaPagosCNI
   SistemaPagosCNI.exe
   ```

2. Instala WebView2 Runtime:
   https://go.microsoft.com/fwlink/p/?LinkId=2124703

3. Instala Visual C++ Redistributable:
   https://aka.ms/vs/17/release/vc_redist.x64.exe

### Antivirus bloquea el ejecutable

**Solución:**
1. Agrega excepción en Windows Defender:
   - Windows Security → Virus & threat protection
   - Manage settings → Add exclusion
   - Agregar carpeta: `dist\SistemaPagosCNI`

2. Opcionalmente, puedes firmar el ejecutable (requiere certificado)

---

## Crear Instalador (Opcional)

Para una experiencia más profesional, crea un instalador con Inno Setup:

### 1. Descargar Inno Setup

https://jrsoftware.org/isinfo.php

### 2. Crear Script de Instalador

Guarda como `installer.iss`:

```ini
[Setup]
AppName=Sistema de Pagos CNI
AppVersion=2.1.0
AppPublisher=Consejo Nacional de Inversiones
DefaultDirName={pf}\SistemaPagosCNI
DefaultGroupName=CNI
OutputDir=installers
OutputBaseFilename=SistemaPagosCNI_Setup_v2.1.0
Compression=lzma2
SolidCompression=yes
ArchitecturesInstallIn64BitMode=x64

[Files]
Source: "dist\SistemaPagosCNI\*"; DestDir: "{app}"; Flags: recursesubdirs

[Icons]
Name: "{group}\Sistema de Pagos CNI"; Filename: "{app}\SistemaPagosCNI.exe"
Name: "{group}\Manual de Usuario"; Filename: "{app}\_internal\MANUAL_USUARIO.md"
Name: "{commondesktop}\Sistema de Pagos CNI"; Filename: "{app}\SistemaPagosCNI.exe"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Crear icono en el escritorio"

[Run]
Filename: "{app}\SistemaPagosCNI.exe"; Description: "Ejecutar Sistema de Pagos CNI"; Flags: nowait postinstall skipifsilent
```

### 3. Compilar el Instalador

1. Abre Inno Setup Compiler
2. File → Open → Selecciona `installer.iss`
3. Build → Compile
4. El instalador se crea en `installers\SistemaPagosCNI_Setup_v2.1.0.exe`

---

## Resumen de Comandos

```cmd
REM En Windows CMD o PowerShell

REM 1. Navegar al proyecto
cd \\wsl$\Ubuntu\home\luis\app_rrhh_cni

REM 2. Crear entorno virtual
python -m venv venv_windows
venv_windows\Scripts\activate

REM 3. Instalar dependencias
pip install -r requirements.txt

REM 4. Compilar
build.bat

REM 5. Probar
cd dist\SistemaPagosCNI
SistemaPagosCNI.exe

REM 6. Comprimir
cd ..
Compress-Archive -Path SistemaPagosCNI -DestinationPath SistemaPagosCNI_v2.1.0_Windows.zip
```

---

## 📞 Soporte

**Desarrollador:**  
Ing. Luis Martínez  
Software Developer  
📧 luismartinez.94mc@gmail.com

**Soporte CNI:**  
Oficial de TI  
📧 amartinez@cni.hn

---

## ✅ Checklist de Compilación

Antes de distribuir, verifica:

- [ ] Ejecutable compilado en Windows nativo
- [ ] Probado en máquina Windows sin Python
- [ ] Todas las funcionalidades funcionan
- [ ] PDFs se generan correctamente
- [ ] Logo CNI se muestra
- [ ] No hay errores en la consola
- [ ] Archivo comprimido creado
- [ ] Tamaño razonable (~50-70 MB)
- [ ] Documentación incluida

---

**🎯 Recomendación Final:** Usa la **Opción 1 (Compilar en Windows)** para mejores resultados.
