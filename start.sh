#!/bin/bash
# Quick Start - Sistema de Pagos CNI v2.0.0
# Consejo Nacional de Inversiones - Honduras

echo ""
echo "════════════════════════════════════════════════════════════"
echo "   Sistema de Pagos CNI v2.0.0"
echo "   Consejo Nacional de Inversiones - Honduras"
echo "════════════════════════════════════════════════════════════"
echo ""

# Verificar si ya está compilado
if [ -f "dist/SistemaPagosCNI/SistemaPagosCNI" ]; then
    echo "✅ Ejecutable ya compilado"
    echo ""
    echo "Opciones:"
    echo "  1) Ejecutar la aplicación"
    echo "  2) Recompilar"
    echo "  3) Crear paquete de distribución"
    echo "  4) Salir"
    echo ""
    read -p "Selecciona una opción [1-4]: " opcion
    
    case $opcion in
        1)
            echo ""
            echo "🚀 Ejecutando Sistema de Pagos CNI..."
            cd dist/SistemaPagosCNI
            ./SistemaPagosCNI
            ;;
        2)
            echo ""
            echo "🔨 Recompilando..."
            ./build.sh
            ;;
        3)
            echo ""
            echo "📦 Creando paquete de distribución..."
            cd dist
            tar -czf SistemaPagosCNI_v2.0.0_Linux.tar.gz SistemaPagosCNI/
            echo "✅ Paquete creado: dist/SistemaPagosCNI_v2.0.0_Linux.tar.gz"
            ls -lh SistemaPagosCNI_v2.0.0_Linux.tar.gz
            ;;
        4)
            echo "👋 ¡Hasta luego!"
            exit 0
            ;;
        *)
            echo "❌ Opción inválida"
            exit 1
            ;;
    esac
else
    echo "⚠️  Ejecutable no encontrado"
    echo ""
    read -p "¿Deseas compilar ahora? [s/N]: " respuesta
    
    if [ "$respuesta" = "s" ] || [ "$respuesta" = "S" ]; then
        echo ""
        echo "🔨 Compilando..."
        ./build.sh
        
        if [ $? -eq 0 ]; then
            echo ""
            read -p "¿Deseas ejecutar la aplicación ahora? [s/N]: " ejecutar
            
            if [ "$ejecutar" = "s" ] || [ "$ejecutar" = "S" ]; then
                echo ""
                echo "🚀 Ejecutando Sistema de Pagos CNI..."
                cd dist/SistemaPagosCNI
                ./SistemaPagosCNI
            fi
        fi
    else
        echo "❌ Compilación cancelada"
        echo ""
        echo "Para compilar manualmente ejecuta:"
        echo "  ./build.sh"
        exit 1
    fi
fi

echo ""
echo "════════════════════════════════════════════════════════════"
echo ""
