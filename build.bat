set HOME=C:\Users\Samuel\
cd C:\Users\Samuel\Documents\GitHub\pyinstruments

C:\Python27\python.exe setup.py bdist_egg
C:\Python27\python.exe setup.py bdist_wininst --install-script postinstallscript.py
C:\Python27\python.exe setup.py sdist
pause
