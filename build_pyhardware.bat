rmdir /S autogenerate\pyhardware-package\
XCOPY /s pyhardware autogenerate\pyhardware-package\pyhardware\
XCOPY /s curve autogenerate\pyhardware-package\curve\
XCOPY /s pyivi autogenerate\pyhardware-package\pyivi\
XCOPY pyhardware_setup\* autogenerate\pyhardware-package\

set HOME=C:\Users\Samuel\
cd C:\Users\Samuel\Documents\GitHub\pyinstruments-package\autogenerate\pyhardware-package

C:\Python27\python.exe setup.py bdist_egg
C:\Python27\python.exe setup.py bdist_wininst
C:\Python27\python.exe setup.py sdist
pause
