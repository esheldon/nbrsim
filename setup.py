import os
import distutils
from distutils.core import setup, Extension, Command
import numpy

scripts=['nbrsim-make-scripts']

scripts=[os.path.join('bin',s) for s in scripts]

setup(
    name="nbrsim", 
    packages=['nbrsim'],
    scripts=scripts,
    version="0.1",
)




