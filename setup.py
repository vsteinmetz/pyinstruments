import os
from setuptools import setup

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "pyinstruments",
    version = "0.0.9",
    author = "Samuel Deleglise",
    author_email = "samuel.deleglise@gmail.com",
    description = ("""Control of data acquisition with remote instruments using 
    (IVI-)dotnet, (IVI-)COM, Visa, and serial protocols.
    python dotnet and/or comtypes should be installed"""),
    license = "BSD",
    keywords = "instruments data-acquisition IVI interface",
    url = "https://github.com/SamuelDeleglise/pyinstruments",
    packages=['pyinstruments',
              'pyinstruments.config',
              'pyinstruments.config.gui',
              'pyinstruments.drivers',
              'pyinstruments.drivers.ivi_interop',
              'pyinstruments.drivers.ivi_interop.ivicom',
              'pyinstruments.drivers.ivi_interop.ividotnet',
              'pyinstruments.drivers.serial',
              'pyinstruments.drivers.visa',
              'pyinstruments.instruments',
              'pyinstruments.wrappers',
              'pyinstruments.factories',
              'hdnavigator',
              'guiwrappersutils',
              'conf_xml',
              'mypandas'],
    long_description=read('README'),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Scientific/Engineering :: Human Machine Interfaces",
        "License :: OSI Approved :: BSD License",
    ],
    install_requires=[
]
)