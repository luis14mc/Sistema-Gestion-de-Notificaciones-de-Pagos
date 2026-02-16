@echo off
REM Script de construcción para Sistema de Pagos CNI
REM Consejo Nacional de Inversiones - Honduras
REM
REM Desarrollado por: Ing. Luis Martínez
REM Email: luismartinez.94mc@gmail.com
REM Versión: 2.1.0

echo ==========================================
echo Sistema de Pagos CNI - Build Script
echo Consejo Nacional de Inversiones
echo ==========================================
echo.

REM Verificar que estamos en el directorio correcto
if not exist "app.py" (
    echo Error: No se encuentra app.py
    echo Asegurate de ejecutar este script desde el directorio raiz del proyecto
    exit /b 1
)

REM Verificar que existe Python
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python no esta instalado o no esta en el PATH
    exit /b 1
)

REM Verificar dependencias
echo Verificando dependencias...
python -c "import flask" >nul 2>&1
if errorlevel 1 (
    echo Error: Flask no esta instalado
    echo Ejecuta: pip install -r requirements.txt
    exit /b 1
)

python -c "import webview" >nul 2>&1
if errorlevel 1 (
    echo Error: PyWebView no esta instalado
    echo Ejecuta: pip install -r requirements.txt
    exit /b 1
)

python -c "import PyInstaller" >nul 2>&1
if errorlevel 1 (
    echo Instalando PyInstaller...
    pip install pyinstaller
)

echo Dependencias verificadas
echo.

REM Limpiar builds anteriores
echo Limpiando builds anteriores...
if exist "build" rmdir /s /q build
if exist "dist" rmdir /s /q dist
if exist "__pycache__" rmdir /s /q __pycache__
del /s /q *.pyc >nul 2>&1
echo Limpieza completada
echo.

REM Crear el ejecutable
echo Creando ejecutable con PyInstaller...
echo Esto puede tomar varios minutos...
echo.

pyinstaller --clean app_rrhh_cni.spec

if %errorlevel% equ 0 (
    echo.
    echo ==========================================
    echo BUILD EXITOSO!
    echo ==========================================
    echo.
    echo El ejecutable se encuentra en:
    echo   .\dist\SistemaPagosCNI\
    echo.
    echo Para ejecutar la aplicación:
    echo   cd dist\SistemaPagosCNI
    echo   SistemaPagosCNI.exe
    echo.
    echo Para distribuir:
    echo   Comprime la carpeta dist\SistemaPagosCNI\ completa
    echo   y enviala a los usuarios
    echo.
    echo ==========================================
) else (
    echo.
    echo ==========================================
    echo ERROR EN LA COMPILACION
    echo ==========================================
    echo.
    echo Revisa los mensajes de error arriba
    echo Contacta a: luismartinez.94mc@gmail.com
    echo.
    exit /b 1
)
