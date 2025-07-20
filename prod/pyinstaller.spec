# Simple PyInstaller spec for the ChatGPT GUI
block_cipher = None

a = Analysis(['src/ui/main.py'], pathex=['..'])
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)
exe = EXE(pyz, a.scripts, [], exclude_binaries=True, name='chatgpt_gui', console=False)
coll = COLLECT(exe, a.binaries, a.zipfiles, a.datas, strip=False, upx=True, name='chatgpt_gui')
