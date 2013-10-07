from curve_editor_menus import NamedCheckBox 

from guidata.qt.QtGui import QFont
from guiqwt.plot import CurveDialog
from guiqwt.builder import make
from numpy import array


WINDOWS = dict()

def get_window(name):
    try:
        win = WINDOWS[name]
    except KeyError:
        win = PlotDialog(name)
        WINDOWS[name] = win
    return win

class PlotDialog(CurveDialog):
    colors = ['red', 'green', 'blue', 'purple', 'yellow', 'orange', 'brown']
    def __init__(self, name):
        super(PlotDialog, self).__init__(edit=False, toolbar=True, wintitle=name,
                      options=dict(title=name, xlabel="xlabel",
                                   ylabel="ylabel"))
        self.get_itemlist_panel().show()
        self._current_color_index = -1
        self.autoscale = NamedCheckBox(self, 'autoscale')
        self.autoscale.checked.connect(self.plot_widget.plot.do_autoscale)
        self.toolbar.addWidget(self.autoscale)
        
        self.show()
    
    def get_next_color(self):
        self._current_color_index+=1
        if self._current_color_index == len(self.colors):
            self._current_color_index = 0
        return self.colors[self._current_color_index]
        
    def plot(self, curve):
        _plot = self.get_plot()
        _plot.add_item(make.curve(array(curve.get_plottable_data().index, dtype=float),
                                  curve.get_plottable_data().values,
                                  color=self.get_next_color(),
                                  title='['+str(curve.id)+']'+curve.params['name'])
                       )
        _plot.replot()
        #_plot.set_axis_font("left", QFont("Courier"))
        
        