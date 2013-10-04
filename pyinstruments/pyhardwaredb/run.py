from guidata import qapplication as __qapplication
from pyinstruments.pyhardwaredb import gui
gui()
_APP = __qapplication()
_APP.exec_()