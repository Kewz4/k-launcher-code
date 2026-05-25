# -*- mode: python ; coding: utf-8 -*-
#
# PyInstaller spec for Vanilla+ Launcher
#
# SmartScreen / Antivirus mitigation notes:
#   1. noupx=True     — UPX-compressed exes are a major AV false-positive trigger.
#                       Disabling UPX makes the binary larger but far less suspicious.
#   2. version_info   — Embeds CompanyName, FileDescription etc. into the exe.
#                       Windows shows these in Properties → Details; SmartScreen
#                       uses them when evaluating unknown publishers.
#   3. manifest       — Sets executionLevel=asInvoker (no UAC elevation request).
#                       Requesting admin causes SmartScreen to warn on EVERY launch.
#   4. console=False  — Hides the console window; a popping console looks suspicious.
#   5. icon           — A recognisable icon improves user trust and AV heuristics.
#
# For the best SmartScreen outcome, code-sign the produced exe with an
# EV (Extended Validation) certificate from a trusted CA such as DigiCert,
# Sectigo, or Certum. Even a standard OV certificate helps build reputation
# over time via Microsoft SmartScreen Application Reputation.

import os
from PyInstaller.utils.hooks import collect_data_files

block_cipher = None

a = Analysis(
    ['launcher_main.py'],
    pathex=['.'],
    binaries=[],
    datas=[
        ('launcher_version.txt', '.'),
        ('Kewz Launcher.ico',    '.'),
        ('music_player.py',      '.'),
        # imageio_ffmpeg bundles a pre-compiled ffmpeg.exe inside its package;
        # without this entry PyInstaller omits it and yt-dlp falls back to
        # low-quality pre-merged formats (no stream merging possible).
        *collect_data_files('imageio_ffmpeg'),
    ],
    hiddenimports=[
        'pywebview',
        'pywebview.platforms.winforms',
        'clr',
        'webview',
        'pythonnet',
        'pkg_resources.py2_warn',
        'psutil',
        'imageio_ffmpeg',
        'yt_dlp',
        'yt_dlp.extractor',
        'yt_dlp.extractor.youtube',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter',
        'matplotlib',
        'numpy',
        'scipy',
        'pandas',
        'PIL',
        'PyQt5',
        'PyQt6',
        'PySide2',
        'PySide6',
        'wx',
        'test',
        'unittest',
    ],
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
    name='VanillaPlusLauncher',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,

    # ── Antivirus / SmartScreen mitigations ──────────────────────────────────
    upx=False,          # Disable UPX — compressed exes trigger many AV engines
    upx_exclude=[],
    # ─────────────────────────────────────────────────────────────────────────

    runtime_tmpdir=None,
    console=False,      # No console window
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,

    # Windows-specific metadata
    icon='Kewz Launcher.ico',
    version='version_info.txt',  # Embeds publisher info into the exe
    manifest='launcher.manifest', # Sets asInvoker, DPI awareness, OS compat
    uac_admin=False,   # Never request admin — SmartScreen warns on every launch
)
