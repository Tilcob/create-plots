# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all
import os

# Ressourcen, die du mitgeben willst:
datas = [
    ('app/resources/Logo_Raug-klein.png', 'app/resources'),
    ('app/resources/Logo_Raug.ico', 'app/resources'),
    ('app/resources/Logo_Raug-Diagramm.png', 'app/resources')
]

binaries = []
hiddenimports = ['openpyxl', 'PIL.ImageTk']

for pkg in ['pandas', 'matplotlib', 'PIL']:
    d, b, h = collect_all(pkg)
    datas += d
    binaries += b
    hiddenimports += h

a = Analysis(
    ['app/main.py'],
    pathex=['app'],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=1,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='main',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    windowed=True,
    icon='app/resources/Logo_Raug.ico',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='main',
)

# Onefile packen:
from PyInstaller.building.build_main import EXE as EXE_onefile

onefile = EXE_onefile(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    name='main',
    debug=False,
    strip=False,
    upx=True,
    console=False,
    windowed=True,
    icon='app/resources/Logo_Raug.ico',
)