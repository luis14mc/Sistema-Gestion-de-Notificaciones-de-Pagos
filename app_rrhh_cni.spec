# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file para Sistema de Pagos CNI
Consejo Nacional de Inversiones - Honduras

Desarrollado por: Ing. Luis Martinez
Email: luismartinez.94mc@gmail.com
Version: 2.2.0
"""

import os

block_cipher = None

added_files = [
    ('templates', 'templates'),
    ('static', 'static'),
    ('img', 'img'),
]

hidden = [
    'flask',
    'fpdf',
    'sqlite3',
    'threading',
    'socket',
    'smtplib',
    'webbrowser',
    'email.mime.text',
    'email.mime.multipart',
    'email.mime.base',
]

# Incluir webview solo si esta disponible
try:
    import webview
    hidden.append('webview')
except ImportError:
    pass

# Icono opcional
icon_path = 'img/logo_cni.ico' if os.path.exists('img/logo_cni.ico') else None

a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=[],
    datas=added_files,
    hiddenimports=hidden,
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
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=icon_path,
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
