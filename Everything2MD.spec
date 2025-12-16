# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['src\\gui\\main.py'],
    pathex=['src'],
    binaries=[],
    datas=[('src/filters/clean.lua', 'src/filters')],
    hiddenimports=['pptx2md', 'pptx2md.parser', 'pptx2md.outputter', 'pptx', 'PIL'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='Everything2MD',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
