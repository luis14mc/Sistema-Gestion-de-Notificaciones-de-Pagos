# Pasos: Build Windows + Subir a GitHub

**Versión 2.2.0** | Sistema de Pagos CNI

---

## 1. Compilar para Windows

### En Windows (PowerShell o CMD)

1. Abre la carpeta del proyecto:
   ```
   \\wsl$\Ubuntu\home\luis\app_rrhh_cni\
   ```

2. Instala dependencias (si no lo has hecho):
   ```cmd
   pip install -r requirements.txt
   ```

3. Ejecuta el build:
   ```cmd
   build.bat
   ```

4. El ejecutable estará en:
   ```
   dist\SistemaPagosCNI\SistemaPagosCNI.exe
   ```

5. Crear ZIP para distribuir:
   ```powershell
   cd dist
   Compress-Archive -Path SistemaPagosCNI -DestinationPath SistemaPagosCNI_v2.2.0_Windows.zip
   ```

---

## 2. Subir a GitHub

### Desde WSL (en la carpeta del proyecto)

```bash
# Ver cambios
git status

# Agregar archivos (excluye binarios y DB si prefieres)
git add server.py app.py templates/ static/ VERSION.txt app_rrhh_cni.spec
git add CALCULO_ISR_IHSS.md build.bat COMPILAR_WINDOWS.md INSTRUCCIONES_PUSH_GITHUB.md
git add .gitignore PASOS_WINDOWS_GITHUB.md

# O agregar todo excepto lo que quieras excluir
git add -A

# Commit
git commit -m "v2.2.0 - IHSS IVM, prorrateo primer mes, ISR anual, reglas por fecha ingreso"

# Push
git push -u origin main
```

### Crear Release en GitHub

1. Ve a: https://github.com/luis14mc/Sistema-Gestion-de-Notificaciones-de-Pagos
2. **Releases** → **Create a new release**
3. Tag: `v2.2.0`
4. Título: `Sistema RRHH CNI v2.2.0`
5. Sube el archivo `SistemaPagosCNI_v2.2.0_Windows.zip` como adjunto
6. **Publish release**

---

## Resumen rápido

| Paso | Dónde | Comando |
|------|-------|---------|
| Build | Windows | `build.bat` |
| ZIP | Windows | `Compress-Archive -Path dist\SistemaPagosCNI -DestinationPath SistemaPagosCNI_v2.2.0_Windows.zip` |
| Push | WSL | `git add -A && git commit -m "v2.2.0" && git push` |
| Release | GitHub web | Subir el .zip en Releases |
