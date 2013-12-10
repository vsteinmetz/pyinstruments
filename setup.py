import os
from setuptools import setup
from setuptools.command.install import install
import subprocess
import shutil


class installWithPost(install):
    def run(self):
        install.run(self)  
        import postinstallscript
        
# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "pyinstruments",
    cmdclass={"install": installWithPost},
    scripts={'postinstallscript.py'},
    data_files=[('pyinstruments/curvestore/fixtures',['pyinstruments/curvestore/fixtures/initial_data.json'])],
    include_package_data=True,
    version = "0.4.0",
    author = "Samuel Deleglise",
    author_email = "samuel.deleglise@gmail.com",
    description = ("""Control of data acquisition with remote instruments using 
    IVI-C or IVI-COM, Visa, and serial protocols."""),
    license = "BSD",
    keywords = "instruments data-acquisition IVI interface",
    url = "https://github.com/SamuelDeleglise/pyinstruments",
    packages=['pyinstruments',
              'pyinstruments/curvefinder',
              'pyinstruments/curvefinder/gui',
              'pyinstruments/curvefinder/gui/curve_display_widget',
              'pyinstruments/curvefinder/gui/curve_search_widget',
              'pyinstruments/curvestore',
              'pyinstruments/datastore',
              'pyinstruments/pyhardwaredb',
              'pyinstruments/datalogger',
              'curve',
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
