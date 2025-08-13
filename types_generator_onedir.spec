# types_generator_onedir.spec
# Build on Windows (onedir): pyinstaller types_generator_onedir.spec --clean
# Produces: dist/Dayz Types Generator/ (folder with EXE and Qt libs)

from PyInstaller.utils.hooks import collect_all, collect_submodules
from PyInstaller.building.build_main import Analysis, PYZ, EXE, COLLECT
import os

# App metadata
APP_NAME = "Dayz Types Generator"
SCRIPT = "types_generator.py"
VERSION_FILE = "version_info.txt"  # keep this next to the spec & script
RUNTIME_HOOKS = ["qt_env_runtime_hook.py"]  # ensures proper Qt DPI env

# Pull in all PySide6 resources (Qt plugins, styles, etc.)
pyside_datas, pyside_binaries, pyside_hidden = collect_all('PySide6')

a = Analysis(
    [SCRIPT],
    pathex=[],
    binaries=pyside_binaries,
    datas=pyside_datas,
    hiddenimports=pyside_hidden + collect_submodules('xml.etree'),
    hookspath=[],
    runtime_hooks=RUNTIME_HOOKS,
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    name=APP_NAME,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,         # keep False to reduce AV flags
    console=False,     # set True during debugging if needed
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,         # set to your .ico path if you have one, e.g., "app.ico"
    version=VERSION_FILE,
)

# Onedir output with all Qt dependencies in the folder
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    name=APP_NAME,
)