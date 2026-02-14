# -*- mode: python ; coding: utf-8 -*-
import sys
from PyInstaller.utils.hooks import collect_data_files
import os

# 获取当前脚本目录
script_dir = os.path.dirname(os.path.abspath(__file__))

# 定义要包含的额外文件
datas = [
    ('N_m3u8DL-RE.exe', '.'),
]

binaries = [
    ('N_m3u8DL-RE.exe', '.'),
]

block_cipher = None

a = Analysis(
    ['m3u8dl_gui.py'],
    pathex=[script_dir],
    binaries=binaries,  # 将N_m3u8DL-RE.exe作为二进制文件包含
    datas=datas,       # 同时作为数据文件包含
    hiddenimports=[],
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
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='M3u8DL_GUI',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # 设置为False以创建GUI应用程序
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # 如果有图标文件，可以在这里指定路径
)