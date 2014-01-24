"""
This module helps to graphically browse between curves
"""

from guidata import qapplication as __qapplication
_APP = __qapplication()

def refresh():
    """
    refresh the content of the curve editor
    """
    curve_editor.refresh()

def displayed_curve():
    return curve_editor.curve_display_widget.left_panel.\
        displayed_curve

def selected_curve():
    return curve_editor.search_widget.widget.list_curve_widget.\
        selected_curve

def selected_curves():
    return curve_editor.search_widget.widget.list_curve_widget.\
        selected_curves

from pyinstruments.curvefinder.gui import CurveEditor
curve_editor = CurveEditor()

_APP.exec_()