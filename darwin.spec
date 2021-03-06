# -*- mode: python -*-
a = Analysis(['main.py'],
             pathex=['/Users/kirill/ld48'],
             hiddenimports=[],
             hookspath=None,
             excludes=["matplotlib", "scipy", "numpy", "unicodedata", "smpeg", "readline",
                 "_codecs_jp", "_codecs_hk", "_codecs_cn", "_codecs_kr", "_codecs_tw"]
            )

##### include mydir in distribution #######
def extra_datas(mydir):
    def rec_glob(p, files):
        import os
        import glob
        for d in glob.glob(p):
            if os.path.isfile(d):
                files.append(d)
            rec_glob("%s/*" % d, files)
    files = []
    rec_glob("%s/*" % mydir, files)
    extra_datas = []
    for f in files:
        extra_datas.append((f, f, 'DATA'))

    return extra_datas
###########################################

# append the 'data' dir
a.datas += extra_datas('data')

pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=1,
          name=os.path.join('build/pyi.darwin/main', 'main'),
          debug=False,
          strip=None,
          upx=True,
          console=False )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=None,
               upx=True,
               name=os.path.join('dist', 'main'))
app = BUNDLE(coll,
             name=os.path.join('dist', 'Camouflage.app'))
