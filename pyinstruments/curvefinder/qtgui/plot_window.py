from curve_editor_menus import NamedCheckBox 


from guidata.qt.QtGui import QFont
from guiqwt.plot import CurveDialog
from guiqwt.builder import make
from numpy import array

class PlotDialog(CurveDialog):
    def __init__(self, name):
        super(PlotDialog, self).__init__(edit=False, toolbar=True, wintitle=name,
                      options=dict(title=name, xlabel="xlabel",
                                   ylabel="ylabel"))
        self.get_itemlist_panel().show()
        
        self.autoscale = NamedCheckBox(self, 'autoscale')
        self.autoscale.checked.connect(self.plot_widget.plot.do_autoscale)
        self.toolbar.addWidget(self.autoscale)

        self.show()
    
    def plot(self, curve):
        _plot = self.get_plot()
        _plot.add_item(make.curve(array(curve.data.index, dtype=float),
                                  curve.data.values,
                                  title='['+str(curve.id)+']'+curve.name)
                       )
        #_plot.set_axis_font("left", QFont("Courier"))
        
        