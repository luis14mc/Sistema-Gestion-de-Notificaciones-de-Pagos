# 🚀 INICIO RÁPIDO - Sistema de Pagos CNI v2.0.0

## Consejo Nacional de Inversiones - Honduras

---

## Para Usuarios Finales

### 📦 Instalación

1. **Descargar** el archivo para tu sistema operativo:
   - Windows: `SistemaPagosCNI_v2.0.0_Windows.zip`
   - Linux: `SistemaPagosCNI_v2.0.0_Linux.tar.gz`
   - macOS: `SistemaPagosCNI_v2.0.0_macOS.zip`

2. **Descomprimir** el archivo en cualquier carpeta

3. **Ejecutar**:
   - Windows: Doble clic en `SistemaPagosCNI.exe`
   - Linux: `./SistemaPagosCNI`
   - macOS: `./SistemaPagosCNI`

4. **Leer la documentación**: Abre `INSTALACION.md` y `MANUAL_USUARIO.md`

---

## Para Desarrolladores

### 🔧 Desarrollo

```bash
# 1. Clonar repositorio
git clone https://github.com/luis14mc/Sistema-Gestion-de-Notificaciones-de-Pagos.git
cd app_rrhh_cni

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Ejecutar en modo desarrollo
python server.py  # Modo web (http://localhost:5000)
# o
python app.py     # Modo aplicación de escritorio
```

### 📦 Compilar Ejecutable

```bash
# Linux/Mac
./build.sh

# Windows
build.bat
```

El ejecutable se genera en `dist/SistemaPagosCNI/`

### 🚀 Script de Inicio Rápido

```bash
# Linux/Mac
./start.sh

# Windows
start.bat
```

---

## 📚 Documentación Completa

| Archivo | Descripción |
|---------|-------------|
| **README.md** | Información general del proyecto |
| **INSTALACION.md** | Guía de instalación para usuarios finales |
| **MANUAL_USUARIO.md** | Manual completo de uso |
| **MANUAL_TECNICO.md** | Documentación técnica y APIs |
| **INSTRUCCIONES_BUILD.md** | Cómo compilar el ejecutable |
| **INSTRUCCIONES_PUSH_GITHUB.md** | Cómo subir código a GitHub |
| **RESUMEN_ENTREGA.md** | Checklist de entrega completo |
| **VERSION.txt** | Información de versión y contactos |

---

## 🆘 Ayuda Rápida

### Problema: No inicia la aplicación

**Windows:**
- Instala Visual C++ Redistributable: https://aka.ms/vs/17/release/vc_redist.x64.exe
- Instala WebView2: https://go.microsoft.com/fwlink/p/?LinkId=2124703

**Linux:**
```bash
sudo apt install -y libgtk-3-0 libwebkit2gtk-4.0-37 gir1.2-webkit2-4.0
```

**macOS:**
```bash
xattr -cr /ruta/a/SistemaPagosCNI
```

### Problema: No se puede conectar al servidor

Asegúrate de que el puerto 5000 (o el puerto asignado) no esté siendo usado por otra aplicación.

### Más ayuda

Ver `INSTALACION.md` → Sección "FAQ y Solución de Problemas"

---

## 📞 Contacto

**Desarrollador:**  
Ing. Luis Martínez  
📧 luismartinez.94mc@gmail.com

**Soporte CNI:**  
Oficial de TI  
📧 amartinez@cni.hn

**Repositorio:**  
🔗 https://github.com/luis14mc/Sistema-Gestion-de-Notificaciones-de-Pagos

---

## 🏢 CNI - Consejo Nacional de Inversiones

© 2026 CNI Honduras - Sistema de Gestión de Pagos v2.0.0
