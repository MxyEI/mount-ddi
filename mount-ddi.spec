# -*- mode: python ; coding: utf-8 -*-
# PyInstaller 打包配置:把 mount-ddi.py + pymobiledevice3 打成单个 exe。
# 用法:pyinstaller --noconfirm --clean mount-ddi.spec  (通常由 build-windows.bat 调用)
from PyInstaller.utils.hooks import collect_all

datas, binaries, hiddenimports = [], [], []

# pymobiledevice3 的 CLI 子命令是运行时动态 import 的(pymobiledevice3.cli.*),
# 普通静态分析抓不全;这些包都用 collect_all 把子模块 + 数据文件(DDI 资源、plist 等)一起收进来。
for pkg in ("pymobiledevice3", "typer", "typer_injector", "click", "coloredlogs", "construct"):
    d, b, h = collect_all(pkg)
    datas += d
    binaries += b
    hiddenimports += h

a = Analysis(
    ["mount-ddi.py"],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="mount-ddi",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    runtime_tmpdir=None,
    console=True,      # 需要看输出/暂停,保留控制台窗口
    disable_windowed_traceback=False,
)
