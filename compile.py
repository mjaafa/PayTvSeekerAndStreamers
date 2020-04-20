from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext
#from logic import main

ext_modules = [
    Extension("Database",  ["database.py"]),
    Extension("Seeker",  ["seeker.py"]),
    Extension("Crypto",  ["crypto.py"])
]

setup(
    name='PayTV Blackmamba seeker ',
    cmdclass = {'build_ext': build_ext},
)
