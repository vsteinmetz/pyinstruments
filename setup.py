import os
from distutils.core import setup
from distutils.command.install import install
from distutils.command.bdist_wininst import bdist_wininst
import subprocess



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
    version = "0.1.16",
    author = "Samuel Deleglise",
    author_email = "samuel.deleglise@gmail.com",
    description = ("""Control of data acquisition with remote instruments using 
    (IVI-)dotnet, (IVI-)COM, Visa, and serial protocols.
    python dotnet and/or comtypes should be installed"""),
    license = "BSD",
    keywords = "instruments data-acquisition IVI interface",
    url = "https://github.com/SamuelDeleglise/pyinstruments",
    packages=['pyinstruments',
              'pyinstruments/curvefinder',
              'pyinstruments/curvefinder/qtgui',
              'pyinstruments/datastore',
              'pyinstruments/pyhardware',
              'pyinstruments/pyhardware/config',
              'pyinstruments/pyhardware/config/gui',
              'pyinstruments/pyhardware/drivers',
              'pyinstruments/pyhardware/drivers/ivi_interop',
              'pyinstruments/pyhardware/drivers/ivi_interop/ivicom',
              'pyinstruments/pyhardware/drivers/ivi_interop/ividotnet',
              'pyinstruments/pyhardware/drivers/ivi_interop',
              'pyinstruments/pyhardware/drivers/serial',
              'pyinstruments/pyhardware/drivers/visa',
              'pyinstruments/pyhardware/factories',
              'pyinstruments/pyhardware/instruments',
              'pyinstruments/pyhardware/wrappers',
              'pyinstruments/pyhardwaredb',
              'pyinstruments/utils',
              'pyinstruments/utils/conf_xml',
              'pyinstruments/utils/curve',
              'pyinstruments/utils/guiwrappersutils'],
    long_description=read('README'),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Scientific/Engineering :: Human Machine Interfaces",
        "License :: OSI Approved :: BSD License",
    ],
    install_requires=[
                      'django>1.5',
                      'guiqwt',
                      'guidata'
    ]
)