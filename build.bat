set HOME=C:\Users\Samuel\
cd C:\Users\Samuel\Documents\GitHub\pyinstruments
rmdir /S build
rmdir /S dist

C:\Python27\python.exe setup.py bdist_egg
C:\Python27\python.exe setup.py bdist_wininst --install-script postinstallscript.py
C:\Python27\python.exe setup.py sdist
pause
