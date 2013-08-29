import os
from setuptools import setup
from setuptools.command.install import install
import subprocess
import shutil



class installWithPost(install):
    def run(self):
        install.run(self)
        ##===========================================
        ##   COPIED FROM postinstallscript
        ##===========================================   
        from PyQt4.QtCore import QSettings
        QSettings('pyinstruments', 'pyinstruments').setValue('database_file', '')
        import subprocess
        def set_environment_variable_on_windows(name, value):
            subprocess.call(['setx', name, value])
            os.environ[name] = value
        
        subprocess.call(['pip', 'install', 'django'])
        set_environment_variable_on_windows('DJANGO_SETTINGS_MODULE', 
                                            'pyinstruments.datastore.settings')
        subprocess.call(['pip', 'install', 'django-model-utils'])
        subprocess.call(['pip', 'install', 'django-utils'])
        
        build_folder = os.path.join(os.environ['TEMP'], 'pip_build_' + os.environ['USERNAME'], 'pyhardware')
        if os.path.exists(build_folder):
            shutil.rmtree(build_folder)
        if subprocess.call(['pip', 'install','pyhardware', '-I', '-U']):
            raise RuntimeError('problem installing pyhardware')

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
    version = "0.2.11",
    author = "Samuel Deleglise",
    author_email = "samuel.deleglise@gmail.com",
    description = ("""Control of data acquisition with remote instruments using 
    IVI-C or IVI-COM, Visa, and serial protocols."""),
    license = "BSD",
    keywords = "instruments data-acquisition IVI interface",
    url = "https://github.com/SamuelDeleglise/pyinstruments",
    packages=['pyinstruments',
              'pyinstruments/curvefinder',
              'pyinstruments/curvefinder/qtgui',
              'pyinstruments/datastore',
              'pyinstruments/pyhardwaredb',
              'pyinstruments/datalogger'],
    long_description=read('README.rst'),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Scientific/Engineering :: Human Machine Interfaces",
        "License :: OSI Approved :: BSD License",
    ],
    install_requires=[]
)