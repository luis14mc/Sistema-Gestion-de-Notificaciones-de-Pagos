# 🚀 Instrucciones para Subir a GitHub

**Sistema de Pagos CNI**  
Desarrollado por: Ing. Luis Martínez

---

## 📋 Pasos para Crear y Subir el Repositorio

### 1. Crear Repositorio en GitHub

1. Ir a [github.com](https://github.com)
2. Clic en el botón **"+"** → **"New repository"**
3. Configurar:
   - **Repository name**: `sistema-pagos-cni`
   - **Description**: "Sistema de Gestión de Recursos Humanos y Nómina - Consejo Nacional de Inversiones"
   - **Visibility**: 
     - ✅ **Private** (Recomendado - uso interno)
     - ⚠️ Public (solo si quieres compartir públicamente)
   - **NO** marcar "Initialize with README" (ya tienes uno)
4. Clic en **"Create repository"**

---

### 2. Conectar tu Repositorio Local

GitHub te mostrará instrucciones. Copia el comando con tu URL y ejecuta:

```bash
cd /home/luis/app_rrhh_cni

# Agregar el remote (cambia la URL por la tuya)
git remote add origin https://github.com/TU-USUARIO/sistema-pagos-cni.git

# Verificar que se agregó correctamente
git remote -v
```

---

### 3. Subir el Código

```bash
# Subir a GitHub (primera vez)
git push -u origin main
```

Te pedirá tus credenciales de GitHub. Si tienes 2FA habilitado, necesitas un **Personal Access Token** en lugar de tu contraseña.

---

### 4. Crear Personal Access Token (si es necesario)

Si GitHub rechaza tu contraseña:

1. Ir a GitHub → **Settings** → **Developer settings** → **Personal access tokens** → **Tokens (classic)**
2. Clic en **"Generate new token"** → **"Generate new token (classic)"**
3. Configurar:
   - **Note**: "Sistema Pagos CNI"
   - **Expiration**: 90 days o No expiration
   - **Select scopes**: Marcar **"repo"** (full control of private repositories)
4. Clic en **"Generate token"**
5. **IMPORTANTE**: Copiar el token (solo se muestra una vez)
6. Usar este token en lugar de tu contraseña cuando hagas `git push`

---

### 5. Verificar en GitHub

1. Ir a tu repositorio en GitHub
2. Deberías ver todos los archivos:
   - ✅ README.md
   - ✅ app.py
   - ✅ server.py
   - ✅ templates/index.html
   - ✅ MANUAL_USUARIO.md
   - ✅ MANUAL_TECNICO.md
   - ✅ requirements.txt
   - ✅ etc.

---

## 📦 Crear una Release (Versión)

Para marcar tu versión 2.0:

1. En GitHub, ir a **"Releases"** → **"Create a new release"**
2. Configurar:
   - **Tag**: `v2.0`
   - **Release title**: `v2.0 - Sistema de Pagos CNI`
   - **Description**:
     ```markdown
     ## Sistema de Pagos CNI v2.0
     
     Primera versión completa del sistema de gestión de recursos humanos.
     
     ### ✨ Características
     - Gestión completa de empleados
     - Cálculo automático de ISR e IHSS
     - Generación de boletas PDF
     - Envío por email (Office 365)
     - Histórico de pagos
     - Interfaz moderna con colores institucionales
     
     ### 🛠️ Tecnologías
     - Python 3.8+, Flask 3.0
     - SQLite3, FPDF2
     - HTML5, Tailwind CSS, JavaScript
     - PyWebView para desktop
     
     ### 📚 Documentación
     Ver README.md, MANUAL_USUARIO.md y MANUAL_TECNICO.md
     
     **Desarrollado por**: Ing. Luis Martínez - Software Developer
     ```
3. Clic en **"Publish release"**

---

## 🔄 Futuras Actualizaciones

Cuando hagas cambios:

```bash
# 1. Ver cambios
git status

# 2. Agregar cambios
git add .

# 3. Commit con mensaje descriptivo
git commit -m "fix: Corrección de bug en cálculo de ISR"

# 4. Subir a GitHub
git push
```

---

## 📝 Convenciones de Commits

Usar prefijos para mensajes claros:

- `feat:` Nueva funcionalidad
- `fix:` Corrección de bugs
- `docs:` Cambios en documentación
- `style:` Cambios de formato/estilo
- `refactor:` Refactorización de código
- `test:` Agregar tests
- `chore:` Tareas de mantenimiento

**Ejemplos**:
```bash
git commit -m "feat: Agregar exportación a Excel"
git commit -m "fix: Corregir cálculo de IHSS para salarios altos"
git commit -m "docs: Actualizar manual de usuario con nueva sección"
```

---

## 🔐 Seguridad

⚠️ **IMPORTANTE**: 

- La base de datos `rrhh_cni.db` ya está en `.gitignore` (comentada)
- Si contiene datos sensibles, asegúrate de que esté en `.gitignore`
- NUNCA subas contraseñas o credenciales reales
- Usa variables de entorno para datos sensibles

---

## 🆘 Solución de Problemas

### Error: "fatal: remote origin already exists"

```bash
git remote remove origin
git remote add origin https://github.com/TU-USUARIO/sistema-pagos-cni.git
```

### Error: "rejected - non-fast-forward"

```bash
git pull origin main --rebase
git push origin main
```

### Olvidaste agregar archivos

```bash
git add archivo-olvidado.py
git commit --amend --no-edit
git push --force
```

---

## ✅ Estado Actual del Repositorio

Tu repositorio local ya tiene:

- ✅ **3 commits** realizados
- ✅ **Rama main** configurada
- ✅ **Git inicializado**
- ✅ **.gitignore** configurado
- ✅ **Documentación completa**
- ✅ **Créditos actualizados** (Ing. Luis Martínez)

**Solo falta**: Conectar con GitHub y hacer `push`

---

## 📧 Contacto

**Desarrollador**: Ing. Luis Martínez  
**Email**: luismartinez.94mc@gmail.com  
**GitHub**: (agrega tu usuario aquí después de crear cuenta)

---

**¡Listo para publicar! 🎉**
