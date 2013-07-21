set HOME=C:\Users\Owner\
cd C:\Users\Samuel\Documents\GitHub\pyinstruments

C:\Python27\python.exe setup.py bdist_egg upload --identity="Samuel Deleglise" --sign --quiet
C:\Python27\python.exe setup.py bdist_wininst register upload --identity="Samuel Deleglise" --sign --quiet
C:\Python27\python.exe setup.py sdist upload --identity="Samuel Deleglise" --sign --quiet
pause