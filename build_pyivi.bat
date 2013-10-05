rmdir /S autogenerate\pyivi-package\
XCOPY /s pyivi autogenerate\pyivi-package\pyivi\
XCOPY pyivi_setup\* autogenerate\pyivi-package\

set HOME=C:\Users\Samuel\
cd C:\Users\Samuel\Documents\GitHub\pyinstruments-package\autogenerate\pyivi-package

C:\Python27\python.exe setup.py bdist_egg
C:\Python27\python.exe setup.py bdist_wininst
C:\Python27\python.exe setup.py sdist
pause
