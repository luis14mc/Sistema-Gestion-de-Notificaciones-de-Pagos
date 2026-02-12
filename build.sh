#!/bin/bash
# Script de construcción para Sistema de Pagos CNI
# Consejo Nacional de Inversiones - Honduras
#
# Desarrollado por: Ing. Luis Martínez
# Email: luismartinez.94mc@gmail.com
# Versión: 2.0.0

echo "=========================================="
echo "Sistema de Pagos CNI - Build Script"
echo "Consejo Nacional de Inversiones"
echo "=========================================="
echo ""

# Verificar que estamos en el directorio correcto
if [ ! -f "app.py" ]; then
    echo "❌ Error: No se encuentra app.py"
    echo "   Asegúrate de ejecutar este script desde el directorio raíz del proyecto"
    exit 1
fi

# Verificar que existe el entorno virtual o las dependencias
echo "🔍 Verificando dependencias..."
if ! python3 -c "import flask" 2>/dev/null; then
    echo "❌ Error: Flask no está instalado"
    echo "   Ejecuta: pip install -r requirements.txt"
    exit 1
fi

if ! python3 -c "import webview" 2>/dev/null; then
    echo "❌ Error: PyWebView no está instalado"
    echo "   Ejecuta: pip install -r requirements.txt"
    exit 1
fi

if ! python3 -c "import PyInstaller" 2>/dev/null; then
    echo "⚙️  Instalando PyInstaller..."
    pip install pyinstaller
fi

echo "✅ Dependencias verificadas"
echo ""

# Limpiar builds anteriores
echo "🧹 Limpiando builds anteriores..."
rm -rf build/ dist/ __pycache__/ *.pyc
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
echo "✅ Limpieza completada"
echo ""

# Crear el ejecutable
echo "📦 Creando ejecutable con PyInstaller..."
echo "   Esto puede tomar varios minutos..."
echo ""

pyinstaller --clean app_rrhh_cni.spec

# Verificar si la compilación fue exitosa
if [ $? -eq 0 ]; then
    echo ""
    echo "=========================================="
    echo "✅ ¡BUILD EXITOSO!"
    echo "=========================================="
    echo ""
    echo "📁 El ejecutable se encuentra en:"
    echo "   ./dist/SistemaPagosCNI/"
    echo ""
    echo "📋 Contenido del directorio:"
    ls -lh dist/SistemaPagosCNI/ | head -20
    echo ""
    echo "🚀 Para ejecutar la aplicación:"
    echo "   cd dist/SistemaPagosCNI"
    echo "   ./SistemaPagosCNI"
    echo ""
    echo "📦 Para distribuir:"
    echo "   Comprime la carpeta dist/SistemaPagosCNI/ completa"
    echo "   y envíala a los usuarios"
    echo ""
    echo "=========================================="
else
    echo ""
    echo "=========================================="
    echo "❌ ERROR EN LA COMPILACIÓN"
    echo "=========================================="
    echo ""
    echo "Revisa los mensajes de error arriba"
    echo "Contacta a: luismartinez.94mc@gmail.com"
    echo ""
    exit 1
fi
