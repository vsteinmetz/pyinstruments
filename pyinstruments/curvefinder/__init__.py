from guidata import qapplication as __qapplication
_APP = __qapplication()
from pyinstruments.curvefinder.gui import CurveEditor
curve_editor = CurveEditor()

_APP.exec_()