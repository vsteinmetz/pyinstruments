"""
This package provides a graphical user interface to query the curves present in the 
database this tool is quite powerful and can be used to plot the curves in 'real time'
while they are acquired by the instruments

to launch the Graphical User Interface, type:
curvefinder.gui()
"""

from guidata import qapplication as __qapplication
_APP = __qapplication()
from pyinstruments.curvefinder.qtgui.curve_editor import CurveEditor as gui

__all__ = ['gui']

if __name__ == "__main__":
    GUI = gui()
    _APP.exec_()
    
