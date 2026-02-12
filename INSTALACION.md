# Guía de Instalación - Sistema de Pagos CNI

## Consejo Nacional de Inversiones - Honduras

**Versión:** 2.0.0  
**Desarrollado por:** Ing. Luis Martínez  
**Email:** luismartinez.94mc@gmail.com  
**Soporte CNI:** Oficial de TI - amartinez@cni.hn

---

## Requisitos del Sistema

### Windows
- **Sistema Operativo:** Windows 10 o superior (64 bits)
- **RAM:** Mínimo 4 GB (recomendado 8 GB)
- **Espacio en disco:** 500 MB libres
- **Requisitos adicionales:** 
  - Microsoft Edge WebView2 Runtime (incluido en Windows 10/11)
  - Visual C++ Redistributable (si no está instalado)

### Linux
- **Sistema Operativo:** Ubuntu 20.04+ / Debian 10+ / Linux Mint 20+
- **RAM:** Mínimo 4 GB (recomendado 8 GB)
- **Espacio en disco:** 500 MB libres
- **Requisitos adicionales:**
  - GTK+ 3.0
  - WebKit2GTK

### macOS
- **Sistema Operativo:** macOS 10.14 (Mojave) o superior
- **RAM:** Mínimo 4 GB (recomendado 8 GB)
- **Espacio en disco:** 500 MB libres

---

## Instalación

### Windows

#### Método 1: Archivo Comprimido (Portátil)

1. **Descargar** el archivo `SistemaPagosCNI_v2.0.0_Windows.zip`

2. **Descomprimir** el archivo en cualquier ubicación (ej: `C:\Aplicaciones\SistemaPagosCNI\`)

3. **Ejecutar** doble clic en `SistemaPagosCNI.exe`

4. **Crear acceso directo** (opcional):
   - Clic derecho en `SistemaPagosCNI.exe`
   - "Enviar a" → "Escritorio (crear acceso directo)"

#### Método 2: Instalador (Recomendado si existe)

1. **Descargar** el archivo `SistemaPagosCNI_Setup_v2.0.0.exe`

2. **Ejecutar** el instalador (doble clic)

3. **Seguir** las instrucciones del asistente de instalación

4. **Acceder** desde el menú de inicio o el icono del escritorio

#### Solución de Problemas Windows

**Si aparece "Windows protegió tu PC":**
1. Click en "Más información"
2. Click en "Ejecutar de todas formas"

**Si falta WebView2:**
1. Descarga: https://go.microsoft.com/fwlink/p/?LinkId=2124703
2. Instala y reinicia el sistema

**Si aparece error de DLL faltante:**
1. Instala Visual C++ Redistributable: https://aka.ms/vs/17/release/vc_redist.x64.exe

---

### Linux

#### Ubuntu / Debian / Mint

1. **Instalar dependencias:**
   ```bash
   sudo apt update
   sudo apt install -y libgtk-3-0 libwebkit2gtk-4.0-37 gir1.2-webkit2-4.0
   ```

2. **Descargar** el archivo `SistemaPagosCNI_v2.0.0_Linux.tar.gz`

3. **Descomprimir:**
   ```bash
   tar -xzf SistemaPagosCNI_v2.0.0_Linux.tar.gz
   cd SistemaPagosCNI
   ```

4. **Dar permisos de ejecución:**
   ```bash
   chmod +x SistemaPagosCNI
   ```

5. **Ejecutar:**
   ```bash
   ./SistemaPagosCNI
   ```

6. **Crear acceso directo** (opcional):
   ```bash
   # Crear archivo .desktop
   cat > ~/.local/share/applications/sistema-pagos-cni.desktop << EOF
   [Desktop Entry]
   Version=2.0.0
   Type=Application
   Name=Sistema de Pagos CNI
   Comment=Gestión de Recursos Humanos - CNI Honduras
   Exec=/ruta/completa/a/SistemaPagosCNI/SistemaPagosCNI
   Icon=/ruta/completa/a/SistemaPagosCNI/_internal/img/logo_cni.png
   Terminal=false
   Categories=Office;Finance;
   EOF
   
   # Actualizar cache de aplicaciones
   update-desktop-database ~/.local/share/applications
   ```

#### Fedora / RHEL / CentOS

1. **Instalar dependencias:**
   ```bash
   sudo dnf install -y gtk3 webkit2gtk3
   ```

2. Continúa con los pasos 2-6 de Ubuntu

#### Arch Linux

1. **Instalar dependencias:**
   ```bash
   sudo pacman -S gtk3 webkit2gtk
   ```

2. Continúa con los pasos 2-6 de Ubuntu

---

### macOS

1. **Descargar** el archivo `SistemaPagosCNI_v2.0.0_macOS.zip`

2. **Descomprimir** (doble clic en el archivo .zip)

3. **Mover** la carpeta a `/Applications/` o cualquier ubicación

4. **Abrir Terminal** y navegar a la carpeta:
   ```bash
   cd /Applications/SistemaPagosCNI
   ```

5. **Dar permisos de ejecución:**
   ```bash
   chmod +x SistemaPagosCNI
   ```

6. **Ejecutar:**
   ```bash
   ./SistemaPagosCNI
   ```

#### Primera Ejecución en macOS

Si aparece un mensaje de seguridad:

1. **Sistema Preferences** → **Security & Privacy**
2. En la pestaña **General**, click en **"Open Anyway"**
3. O ejecuta en Terminal:
   ```bash
   xattr -cr /Applications/SistemaPagosCNI
   ```

---

## Configuración Inicial

### 1. Primera Ejecución

Al ejecutar por primera vez, el sistema:
- Creará automáticamente la base de datos `rrhh_cni.db`
- Configurará las carpetas necesarias
- Cargará las tablas de ISR e IHSS por defecto

### 2. Configurar Email (Opcional)

Para enviar boletas por correo:

1. Ve a la sección **"Configuración"**
2. Configura los parámetros SMTP de Office 365:
   - **Servidor:** `smtp.office365.com`
   - **Puerto:** `587`
   - **Usuario:** Tu correo institucional
   - **Contraseña:** Tu contraseña (o App Password)
   - **Remitente:** Tu correo institucional
3. Click en **"Guardar"**
4. Prueba la configuración enviando un correo de prueba

### 3. Verificar Configuración ISR

1. Ve a **"Configuración"** → **"Tabla de ISR"**
2. Verifica que los tramos de ISR sean correctos para Honduras
3. Modifica si es necesario

### 4. Verificar Configuración IHSS

1. Ve a **"Configuración"** → **"IHSS"**
2. Verifica las tasas:
   - EM (Enfermedad y Maternidad): 2.5%
   - IVM (Invalidez, Vejez y Muerte): 2.5%
   - Techo de cotización: actualizar según IHSS
3. Modifica si es necesario

---

## Ubicación de Archivos

### Windows

```
C:\Aplicaciones\SistemaPagosCNI\
├── SistemaPagosCNI.exe         # Ejecutable principal
├── _internal\                   # Librerías y archivos internos
│   ├── templates\               # Plantillas HTML
│   ├── static\                  # Archivos estáticos
│   └── img\                     # Imágenes
├── rrhh_cni.db                  # Base de datos (se crea al iniciar)
└── reportes_pagos_RRHH\         # Reportes generados
    ├── boletas_YYYYMM\          # Boletas por mes
    └── _auditorias\             # Auditorías
```

### Linux / macOS

```
/opt/SistemaPagosCNI/            # O la ubicación elegida
├── SistemaPagosCNI              # Ejecutable principal
├── _internal/                   # Librerías y archivos internos
│   ├── templates/               # Plantillas HTML
│   ├── static/                  # Archivos estáticos
│   └── img/                     # Imágenes
├── rrhh_cni.db                  # Base de datos (se crea al iniciar)
└── reportes_pagos_RRHH/         # Reportes generados
    ├── boletas_YYYYMM/          # Boletas por mes
    └── _auditorias/             # Auditorías
```

---

## Actualización

Para actualizar a una nueva versión:

### Método 1: Instalación Limpia (Recomendado)

1. **Respaldar** la base de datos `rrhh_cni.db`
2. **Respaldar** la carpeta `reportes_pagos_RRHH/`
3. **Desinstalar** la versión anterior (o eliminar la carpeta)
4. **Instalar** la nueva versión siguiendo las instrucciones
5. **Copiar** el archivo `rrhh_cni.db` de respaldo a la nueva ubicación
6. **Copiar** la carpeta `reportes_pagos_RRHH/` si es necesario

### Método 2: Reemplazo (Avanzado)

1. **Respaldar** `rrhh_cni.db` y `reportes_pagos_RRHH/`
2. **Descargar** la nueva versión
3. **Reemplazar** solo el ejecutable y la carpeta `_internal/`
4. **Mantener** `rrhh_cni.db` y `reportes_pagos_RRHH/`

---

## Desinstalación

### Windows

#### Si usaste el instalador:
1. Panel de Control → Programas → Desinstalar un programa
2. Selecciona "Sistema de Pagos CNI"
3. Click en "Desinstalar"

#### Si usaste el archivo portátil:
1. Simplemente elimina la carpeta `SistemaPagosCNI`

### Linux / macOS

1. Elimina la carpeta de instalación:
   ```bash
   rm -rf /opt/SistemaPagosCNI
   # o la ubicación donde la instalaste
   ```

2. Elimina el acceso directo (si lo creaste):
   ```bash
   rm ~/.local/share/applications/sistema-pagos-cni.desktop
   ```

---

## Respaldo de Datos

### ¿Qué respaldar?

1. **Base de datos:** `rrhh_cni.db`
2. **Reportes:** Carpeta `reportes_pagos_RRHH/`

### Frecuencia Recomendada

- **Diario:** Si usas el sistema todos los días
- **Semanal:** Si usas el sistema ocasionalmente
- **Mensual:** Como mínimo, respalda después de generar nómina

### Cómo Respaldar

#### Método Manual:

1. Cierra el programa
2. Copia `rrhh_cni.db` a una ubicación segura
3. Copia la carpeta `reportes_pagos_RRHH/` si necesitas los PDFs

#### Método Automatizado (Windows):

Crea un script `.bat`:

```batch
@echo off
set fecha=%date:~-4%%date:~3,2%%date:~0,2%
xcopy "C:\Aplicaciones\SistemaPagosCNI\rrhh_cni.db" "D:\Respaldos\CNI\%fecha%_rrhh_cni.db*" /Y
xcopy "C:\Aplicaciones\SistemaPagosCNI\reportes_pagos_RRHH" "D:\Respaldos\CNI\reportes\" /E /I /Y
echo Respaldo completado: %fecha%
pause
```

#### Método Automatizado (Linux/macOS):

Crea un script `backup.sh`:

```bash
#!/bin/bash
fecha=$(date +%Y%m%d)
mkdir -p ~/Respaldos/CNI/
cp /opt/SistemaPagosCNI/rrhh_cni.db ~/Respaldos/CNI/${fecha}_rrhh_cni.db
cp -r /opt/SistemaPagosCNI/reportes_pagos_RRHH ~/Respaldos/CNI/reportes_${fecha}/
echo "Respaldo completado: $fecha"
```

Automatiza con cron:
```bash
# Abrir crontab
crontab -e

# Agregar línea para respaldo diario a las 6 PM
0 18 * * * /opt/SistemaPagosCNI/backup.sh
```

---

## Soporte y Ayuda

### Documentación

- **Manual de Usuario:** `MANUAL_USUARIO.md` - Guía completa de uso
- **Manual Técnico:** `MANUAL_TECNICO.md` - Documentación técnica
- **Instrucciones de Compilación:** `INSTRUCCIONES_BUILD.md`

### Contacto

**Desarrollador:**  
Ing. Luis Martínez  
Software Developer  
Email: luismartinez.94mc@gmail.com

**Soporte Interno CNI:**  
Oficial de TI  
Email: amartinez@cni.hn

### Reportar Problemas

Al reportar un problema, incluye:
1. Sistema operativo y versión
2. Versión del Sistema de Pagos CNI (2.0.0)
3. Descripción detallada del problema
4. Pasos para reproducir el error
5. Capturas de pantalla si es posible

---

## Preguntas Frecuentes (FAQ)

### ¿Necesito internet para usar el sistema?

No. El sistema funciona completamente offline. Solo necesitas internet si quieres enviar boletas por correo electrónico.

### ¿Puedo instalar el sistema en múltiples computadoras?

Sí, pero cada instalación tendrá su propia base de datos. Si necesitas compartir datos, debes copiar el archivo `rrhh_cni.db` entre computadoras.

### ¿Los datos están seguros?

Los datos se almacenan localmente en tu computadora en formato SQLite. Te recomendamos hacer respaldos periódicos y mantener los permisos de archivos restringidos.

### ¿Puedo usar el sistema en una red?

La versión actual está diseñada para uso local (una computadora). Para uso en red, contacta al desarrollador.

### ¿Cómo actualizo las tablas de ISR/IHSS?

Ve a la sección "Configuración" en el sistema y modifica los valores según las normativas actuales de Honduras.

### ¿Qué hago si olvidé configurar el correo?

No te preocupes. Puedes configurar el correo en cualquier momento desde "Configuración". Mientras tanto, puedes generar y guardar las boletas en PDF.

### ¿Puedo personalizar el logo?

Sí, pero requiere recompilar el sistema. Contacta al desarrollador para asistencia.

---

## Licencia y Términos de Uso

Este software es propiedad del **Consejo Nacional de Inversiones (CNI) - Honduras**.

- Uso exclusivo para fines institucionales del CNI
- Prohibida su distribución fuera del CNI sin autorización
- Prohibida la modificación del código sin autorización
- Los datos procesados son responsabilidad del usuario

© 2026 CNI Honduras - Todos los derechos reservados.

---

**¡Gracias por usar el Sistema de Pagos CNI!**
