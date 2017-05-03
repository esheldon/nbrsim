import os
import distutils
from distutils.core import setup, Extension, Command
from glob import glob
import numpy

scripts=[
    'nbrsim-make-scripts',
    'nbrsim-reduce',
    'nbrsim-make-meds',
]

scripts=[os.path.join('bin',s) for s in scripts]


configs = glob('config/*')

configs = [c for c in configs if '~' not in c]

data_files=[]
for f in configs:
    data_files.append( ('share/nbrsim-config',[f]) )


setup(
    name="nbrsim", 
    packages=['nbrsim'],
    scripts=scripts,
    data_files=data_files,
    version="0.1",
)




