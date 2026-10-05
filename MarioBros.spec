# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all

datas = [('C:\\Users\\ardak\\Desktop\\vucut-oyun-temiz\\venv\\lib\\site-packages\\mediapipe', 'mediapipe')]
binaries = []
hiddenimports = ['matplotlib', 'matplotlib.backends', 'matplotlib.backends.backend_agg', 'matplotlib.backends.backend_svg', 'matplotlib.figure', 'matplotlib.axes', 'matplotlib.artist', 'mediapipe', 'mediapipe.python', 'mediapipe.python.solutions', 'mediapipe.python.solutions.hands', 'mediapipe.python.solutions.hands_connections', 'mediapipe.python.solutions.drawing_utils', 'mediapipe.python.solutions.drawing_styles', 'mediapipe.python.solutions.face_detection', 'mediapipe.python.solutions.face_mesh', 'mediapipe.python.solutions.pose', 'cv2', 'cv2.data', 'numpy', 'numpy.core', 'numpy.core._methods', 'pygame', 'pygame.mixer', 'pygame.surfarray', 'pygame.sndarray', 'pygame.locals', 'pygame.display', 'pygame.event', 'pygame.draw', 'pygame.font', 'pygame.image', 'pygame.key', 'pygame.mouse', 'pygame.rect', 'pygame.surface', 'pygame.time', 'pygame.transform']
tmp_ret = collect_all('mediapipe')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('cv2')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('pygame')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('numpy')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('matplotlib')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
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
    name='MarioBros',
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
