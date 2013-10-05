import os
from setuptools import setup
from setuptools.command.install import install
import subprocess
import shutil

        
# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name="pyhardware",
    version="0.0.12",
    author = "Samuel Deleglise",
    author_email = "samuel.deleglise@gmail.com",
    description = ("""Control of data acquisition with remote instruments using 
    IVI-C or IVI-COM, Visa, and serial protocols."""),
    license = "BSD",
    keywords = "instruments data-acquisition IVI interface",
    url = "https://github.com/SamuelDeleglise/pyinstruments",
    packages=['curve',
              'pyhardware',
              'pyhardware/config',
              'pyhardware/config/gui',
              'pyhardware/drivers',
              'pyhardware/drivers/ivi',
              'pyhardware/drivers/serial',
              'pyhardware/drivers/visa',
              'pyhardware/utils',
              'pyhardware/utils/conf_xml',
              'pyhardware/utils/guiwrappersutils',
              'pyivi',
              'pyivi/ivic',
              'pyivi/ivicom',
              'pyivi/ivifactory'
              ],
    long_description=read('README.rst'),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Scientific/Engineering :: Human Machine Interfaces",
        "License :: OSI Approved :: BSD License",
    ],
    install_requires=[]
)