@echo off
REM Quick Start - Sistema de Pagos CNI v2.0.0
REM Consejo Nacional de Inversiones - Honduras

echo.
echo ================================================================
echo    Sistema de Pagos CNI v2.0.0
echo    Consejo Nacional de Inversiones - Honduras
echo ================================================================
echo.

REM Verificar si ya esta compilado
if exist "dist\SistemaPagosCNI\SistemaPagosCNI.exe" (
    echo Ya existe un ejecutable compilado
    echo.
    echo Opciones:
    echo   1) Ejecutar la aplicacion
    echo   2) Recompilar
    echo   3) Crear paquete de distribucion
    echo   4) Salir
    echo.
    set /p opcion="Selecciona una opcion [1-4]: "
    
    if "%opcion%"=="1" (
        echo.
        echo Ejecutando Sistema de Pagos CNI...
        cd dist\SistemaPagosCNI
        start SistemaPagosCNI.exe
    ) else if "%opcion%"=="2" (
        echo.
        echo Recompilando...
        call build.bat
    ) else if "%opcion%"=="3" (
        echo.
        echo Creando paquete de distribucion...
        cd dist
        tar -czf SistemaPagosCNI_v2.0.0_Windows.zip SistemaPagosCNI\
        echo Paquete creado: dist\SistemaPagosCNI_v2.0.0_Windows.zip
        dir SistemaPagosCNI_v2.0.0_Windows.zip
    ) else if "%opcion%"=="4" (
        echo Hasta luego!
        exit /b 0
    ) else (
        echo Opcion invalida
        exit /b 1
    )
) else (
    echo Ejecutable no encontrado
    echo.
    set /p respuesta="Deseas compilar ahora? [s/N]: "
    
    if /i "%respuesta%"=="s" (
        echo.
        echo Compilando...
        call build.bat
        
        if %errorlevel% equ 0 (
            echo.
            set /p ejecutar="Deseas ejecutar la aplicacion ahora? [s/N]: "
            
            if /i "%ejecutar%"=="s" (
                echo.
                echo Ejecutando Sistema de Pagos CNI...
                cd dist\SistemaPagosCNI
                start SistemaPagosCNI.exe
            )
        )
    ) else (
        echo Compilacion cancelada
        echo.
        echo Para compilar manualmente ejecuta:
        echo   build.bat
        exit /b 1
    )
)

echo.
echo ================================================================
echo.
pause
