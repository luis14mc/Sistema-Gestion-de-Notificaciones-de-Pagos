# Instrucciones para Subir el Código a GitHub

## Repositorio
**URL:** https://github.com/luis14mc/Sistema-Gestion-de-Notificaciones-de-Pagos.git

---

## Opción 1: Usar Token de Acceso Personal (PAT) - Más Fácil

### Paso 1: Crear un Token de Acceso Personal en GitHub

1. Ve a GitHub y accede a tu cuenta
2. Click en tu foto de perfil (esquina superior derecha) → **Settings**
3. En el menú izquierdo, baja hasta **Developer settings**
4. Click en **Personal access tokens** → **Tokens (classic)**
5. Click en **Generate new token** → **Generate new token (classic)**
6. Dale un nombre descriptivo (ej: "App RRHH CNI")
7. Selecciona el alcance: **repo** (acceso completo a repositorios privados)
8. Click en **Generate token**
9. **¡IMPORTANTE!** Copia el token inmediatamente (solo se muestra una vez)

### Paso 2: Configurar el Remote con el Token

Abre una terminal en `/home/luis/app_rrhh_cni` y ejecuta:

```bash
# Cambiar el remote para usar tu token
git remote set-url origin https://TU_TOKEN_AQUI@github.com/luis14mc/Sistema-Gestion-de-Notificaciones-de-Pagos.git

# Verificar
git remote -v

# Subir el código
git push -u origin main
```

**Reemplaza `TU_TOKEN_AQUI` con el token que copiaste.**

---

## Opción 2: Usar SSH (Más Seguro)

### Paso 1: Generar una Clave SSH

```bash
# Generar clave SSH
ssh-keygen -t ed25519 -C "luismartinez.94mc@gmail.com"

# Presiona Enter para la ubicación predeterminada
# Presiona Enter para sin passphrase (o ingresa una si quieres más seguridad)

# Iniciar el agente SSH
eval "$(ssh-agent -s)"

# Agregar la clave al agente
ssh-add ~/.ssh/id_ed25519

# Copiar la clave pública
cat ~/.ssh/id_ed25519.pub
```

### Paso 2: Agregar la Clave SSH a GitHub

1. Copia todo el contenido de `~/.ssh/id_ed25519.pub`
2. Ve a GitHub → **Settings** (tu perfil)
3. **SSH and GPG keys** → **New SSH key**
4. Dale un título (ej: "WSL Ubuntu")
5. Pega la clave pública
6. Click en **Add SSH key**

### Paso 3: Verificar y Subir

```bash
# Verificar conexión SSH
ssh -T git@github.com

# Si dice "Hi luis14mc! You've successfully authenticated" entonces funciona

# El remote ya está configurado, solo sube
git push -u origin main
```

---

## Opción 3: Usar GitHub CLI (gh) - Más Moderno

### Instalación

```bash
# Instalar GitHub CLI (si no está instalado)
type -p curl >/dev/null || (sudo apt update && sudo apt install curl -y)
curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg \
&& sudo chmod go+r /usr/share/keyrings/githubcli-archive-keyring.gpg \
&& echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null \
&& sudo apt update \
&& sudo apt install gh -y
```

### Autenticación y Push

```bash
# Autenticarte
gh auth login

# Sigue las instrucciones en pantalla
# - Selecciona "GitHub.com"
# - Selecciona "HTTPS"
# - Selecciona "Login with a web browser"
# - Copia el código de 8 dígitos
# - Presiona Enter para abrir el navegador
# - Pega el código en GitHub

# Una vez autenticado, subir el código
git push -u origin main
```

---

## Verificar que Subió Correctamente

Después de hacer push, verifica en:
**https://github.com/luis14mc/Sistema-Gestion-de-Notificaciones-de-Pagos**

Deberías ver todos los archivos:
- `server.py`
- `app.py`
- `templates/index.html`
- `static/`
- `README.md`
- `MANUAL_TECNICO.md`
- `MANUAL_USUARIO.md`
- Y todos los demás archivos

---

## Crear un Release (Opcional pero Recomendado)

Una vez que el código esté subido:

```bash
# Crear un tag para la versión 2.0.0
git tag -a v2.0.0 -m "Release 2.0.0 - Sistema RRHH CNI completo"

# Subir el tag
git push origin v2.0.0
```

Luego en GitHub:
1. Ve a tu repositorio
2. Click en **Releases** → **Create a new release**
3. Selecciona el tag `v2.0.0`
4. Título: "Sistema RRHH CNI v2.0.0"
5. Descripción: Copia el contenido de la sección "Historial de Versiones" del README.md
6. Click en **Publish release**

---

## Problemas Comunes

### "Permission denied"
- Verifica que tu token o SSH key esté correctamente configurado
- Verifica que tengas permisos de escritura en el repositorio

### "Repository not found"
- Verifica que el repositorio existe: https://github.com/luis14mc/Sistema-Gestion-de-Notificaciones-de-Pagos
- Verifica que estés autenticado con la cuenta correcta

### "Failed to push some refs"
- Primero haz `git pull origin main --rebase`
- Luego `git push -u origin main`

---

## Soporte

**Desarrollador:** Ing. Luis Martínez  
**Email:** luismartinez.94mc@gmail.com  

**Soporte CNI:** Oficial de TI  
**Email:** amartinez@cni.hn

---

## Comandos de Referencia Rápida

```bash
# Ver estado actual
git status

# Ver commits
git log --oneline

# Ver diferencias
git diff

# Ver remotes
git remote -v

# Cambiar remote
git remote set-url origin NUEVA_URL

# Eliminar remote
git remote remove origin

# Agregar nuevo remote
git remote add origin URL
```

---

**Nota:** Te recomiendo usar la **Opción 1 (Token PAT)** si es la primera vez que usas Git con GitHub, es la más sencilla.
