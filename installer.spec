# -*- mode: python -*-

block_cipher = None


a = Analysis(['main.py'],
             pathex=['cython_pyinstaller_sample/binary'],
             binaries=[('program_a.cpython-36m-x86_64-linux-gnu.so', '.'),('program_b.cpython-36m-x86_64-linux-gnu.so', '.')],
             datas=[('config_file.txt', '.')],
             hiddenimports=['licensing', 'licensing.methods', 'pandas'],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False) pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher) exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='sample_app',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          runtime_tmpdir=None,
          console=True )
