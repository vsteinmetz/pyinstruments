import os
from setuptools import setup
from distutils.core import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "datastore",
    version = "0.0.1",
    author = "Samuel Deleglise",
    author_email = "samuel.deleglise@gmail.com",
    description = ("""A django database to store curves from a data-acquisition system"""),
    license = "BSD",
    keywords = "instruments data-acquisition",
    url = "https://github.com/SamuelDeleglise/pyinstruments",
    packages=['datastore'],
    long_description=read('README'),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Scientific/Engineering :: Human Machine Interfaces",
        "License :: OSI Approved :: BSD License",
    ],
    install_requires=[
                      'django>1.5'
    ]
    )