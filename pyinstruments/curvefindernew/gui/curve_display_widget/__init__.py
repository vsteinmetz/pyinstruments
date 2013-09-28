from pyinstruments.curvefindernew.gui.curve_display_widget.curve_alter_widget import CurveAlterWidget
from pyinstruments.curvefindernew.gui.curve_display_widget.params_display_widget import ParamsDisplayWidget
from pyinstruments.curvefindernew.gui.curve_editor_menus import NamedCheckBox

from PyQt4 import QtCore, QtGui
from guiqwt import plot
from guiqwt.builder import make
from numpy import array

class CurveDisplayWidget(QtGui.QWidget):
    def __init__(self, parent=None):
        super(CurveDisplayWidget, self).__init__(parent)
        self.plot_widget = plot.CurveWidget(self, 'curve graph', \
                                            show_itemlist=False)
        self.plot_widget.plot.set_antialiasing(True)
        self.plot_widget.register_all_curve_tools()
        
        self.lay = QtGui.QHBoxLayout()
        self.sublay = QtGui.QVBoxLayout()
        self.lay.addLayout(self.sublay)
        self.display_params = ParamsDisplayWidget()
        self.lay.addWidget(self.display_params)
        
        self.sublay.addWidget(self.plot_widget)
        self.setup_plot_widget()
        
        self.alter_curve_widget = CurveAlterWidget(self)
        self.alter_curve_widget.curve_saved.connect(self.refresh_params)
        self.sublay.addWidget(self.alter_curve_widget)
        
        self.setLayout(self.lay)
        
             
        #---guiqwt curve item attribute:
        self.curve_item = make.curve([], [], color='b')
        self.plot_widget.plot.add_item(self.curve_item)
        self.displayed_curve = None
    
        self.lay.setStretchFactor(self.display_params, 0)
        self.lay.setStretchFactor(self.sublay, 10)
        self.sublay.setStretchFactor(self.plot_widget, 10)
        self.sublay.setStretchFactor(self.alter_curve_widget, 0)
    
    def refresh_params(self):
        self.display_params.display_curve(self.displayed_curve)
    
    def save(self):
        curve = self.displayed_curve
        self.save_curve(curve)
    
    def save_curve(self, curve):
        self.alter_curve_widget.save_curve(curve)
        
    def setup_plot_widget(self):
         #---guiqwt plot manager
        self.manager = plot.PlotManager(self)
        #---Register plot to manager
        self.manager.add_plot(self.plot_widget.plot)
        #---
        #---Add toolbar and register manager tools
        #toolbar = self.parent().addToolBar("tools")
        self.toolbar = QtGui.QToolBar("plot tools", self)
        self.autoscale = NamedCheckBox(self, 'autoscale')
        self.autoscale.checked.connect(self.plot_widget.plot.do_autoscale)
        self.toolbar.addWidget(self.autoscale)
        self.manager.add_toolbar(self.toolbar, id(self.toolbar))
        self.sublay.insertWidget(0, self.toolbar)
        self.manager.register_all_curve_tools()
        #---
    
    def display_curve(self, curve):
        self.displayed_curve = curve
        if curve:
            self.display_params.display_curve(curve)
            self.alter_curve_widget.display_curve(curve)
            self.curve_item.set_data(array(curve.data.index, \
                                    dtype = float), \
                                    array(curve.data, dtype = float))
            if self.autoscale:
                self.curve_item.plot().do_autoscale()
            self.curve_item.plot().replot()
        
            curve.user_has_read = True
            curve.save()
            self.alter_curve_widget.save_button.hide()