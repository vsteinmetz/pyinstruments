from pyinstruments.curvefinder.gui.curve_display_widget.curve_alter_widget import CurveAlterWidget
from pyinstruments.curvefinder.gui.curve_display_widget.params_display_widget import ParamsDisplayWidget
from pyinstruments.curvefinder.gui.curve_editor_menus import NamedCheckBox

from PyQt4 import QtCore, QtGui
from guiqwt import plot
from guiqwt.builder import make
from numpy import array

class CurveDisplayLeftPanel(QtGui.QWidget):
    delete_done = QtCore.pyqtSignal()
    save_pressed = QtCore.pyqtSignal()
    
    def __init__(self, parent=None):
        super(CurveDisplayLeftPanel, self).__init__(parent)     
        self.displayed_curve = None
        self.setup_plot_widget()
        self.lay = QtGui.QVBoxLayout()
        
        self.lay.addWidget(self.toolbar)
        self.lay.addWidget(self.plot_widget)
        self.alter_curve_widget = CurveAlterWidget(self)
        self.alter_curve_widget.curve_saved.connect(self.save_pressed)
        self.alter_curve_widget.delete_done.connect(self.delete_done)
        self.lay.addWidget(self.alter_curve_widget)
        self.setLayout(self.lay)
        
        
    def setup_plot_widget(self):
        self.plot_widget = plot.CurveWidget(self, 'curve graph', \
                                            show_itemlist=False)
        self.plot_widget.plot.set_antialiasing(True)
        self.plot_widget.register_all_curve_tools()
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
        
        
        self.manager.register_all_curve_tools()
        self.curve_item = make.curve([], [], color='b')
        self.plot_widget.plot.add_item(self.curve_item)
        self.displayed_curve = None

    def display_curve(self, curve):
        self.displayed_curve = curve
        if curve:
            curvedata = curve.get_plottable_data()
            #downsample large files for quick preview
            if len(curvedata)>50000:
                dsfactor = len(curvedata)//5000
                curvedata = curvedata[range(0,len(curvedata),dsfactor)]
            self.alter_curve_widget.display_curve(curve)
            self.curve_item.set_data(array(curvedata.index, dtype = float), 
                                    array(curvedata.values, dtype = float))
            if self.autoscale:
                self.curve_item.plot().do_autoscale()
            self.curve_item.plot().replot()
        
            if not curve.params['user_has_read']:
                curve.params['user_has_read'] = True
                curve.save()
            self.alter_curve_widget.save_button.hide()
            
    def save_curve(self, curve):
        self.alter_curve_widget.save_curve(curve) 
            
class CurveDisplayWidget(QtGui.QSplitter):
    delete_done = QtCore.pyqtSignal()
    def __init__(self, parent=None):
        super(CurveDisplayWidget, self).__init__(parent)
        self.left_panel = CurveDisplayLeftPanel()
        self.addWidget(self.left_panel)
        self.display_params = ParamsDisplayWidget()
        self.addWidget(self.display_params)
        self.left_panel.save_pressed.connect(self.refresh_params)
        self.left_panel.delete_done.connect(self.delete_done)
    
    def refresh_params(self):
        self.display_params.display_curve(self.displayed_curve)
    
    def save(self):
        curve = self.displayed_curve
        self.save_curve(curve)
    
    def save_curve(self, curve):
        self.left_panel.save_curve(curve)
    
    def display_curve(self, curve):
        self.displayed_curve = curve
        self.left_panel.display_curve(curve)
        if curve:
            self.display_params.display_curve(curve)
