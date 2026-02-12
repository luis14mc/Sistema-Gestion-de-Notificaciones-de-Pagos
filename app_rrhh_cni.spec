# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file para Sistema de Pagos CNI
Consejo Nacional de Inversiones - Honduras

Desarrollado por: Ing. Luis Martínez
Email: luismartinez.94mc@gmail.com
Versión: 2.0.0
"""

block_cipher = None

# Recopilar todos los archivos de datos necesarios
added_files = [
    ('templates', 'templates'),
    ('static', 'static'),
    ('img', 'img'),
]

a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=[],
    datas=added_files,
    hiddenimports=[
        'flask',
        'webview',
        'fpdf',
        'sqlite3',
        'threading',
        'socket',
        'smtplib',
        'email.mime.text',
        'email.mime.multipart',
        'email.mime.base',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='SistemaPagosCNI',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # No mostrar consola en Windows
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Puedes agregar un .ico aquí si tienes uno
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='SistemaPagosCNI',
)
