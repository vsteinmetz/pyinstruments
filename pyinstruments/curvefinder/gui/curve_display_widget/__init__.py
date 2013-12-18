from pyinstruments.curvefinder.gui.curve_display_widget.curve_alter_widget import CurveAlterWidget
from pyinstruments.curvefinder.gui.curve_display_widget.params_display_widget import ParamsDisplayWidget
from pyinstruments.curvefinder.gui.curve_editor_menus import NamedCheckBox
from pyinstruments.curvefinder import _APP
from pyinstruments.curvestore import models
from pyinstruments.curvefinder import displayed_curve, refresh

from PyQt4 import QtCore, QtGui
from guiqwt import plot
from guiqwt.builder import make
from numpy import array
import guiqwt
from guiqwt.config import _
from guiqwt.interfaces import (IColormapImageItemType, IPlotManager,
                               IVoiImageItemType, IStatsImageItemType,
                               ICurveItemType)
import weakref
from StringIO import StringIO
import pandas
from datetime import datetime

class CutSignalTool(guiqwt.tools.BaseCursorTool):
    TITLE = _("Cut signal")
    ICON = "xrange.png"
    SWITCH_TO_DEFAULT_TOOL = True
    
    def __init__(self, manager, toolbar_id=guiqwt.tools.DefaultToolbarID):#,
                # title=None, icon=None, tip=None):
        super(CutSignalTool, self).__init__(manager, toolbar_id)#, title=title,
                                             # icon=icon, tip=tip)
        self._last_item = None
        self.label = None
        self.option_selected = None
        
    def setup_context_menu(self, menu, plot):
        menu.addAction(self.action)
            
    def setup_toolbar(self, toolbar):
        pass    
    
    def create_action_menu(self, manager):
        menu = QtGui.QMenu()
        self.action_clipboard = manager.create_action('csv in clipboard')
        menu.addAction(self.action_clipboard)
        self.action_file = manager.create_action('csv in file...')
        menu.addAction(self.action_file)
        self.action_curve = manager.create_action('new curve...')
        menu.addAction(self.action_curve)
        self.action_clipboard.triggered.connect(self.set_option_clipboard)
        self.action_file.triggered.connect(self.set_option_file)
        self.action_curve.triggered.connect(self.set_option_curve)
        return menu
    
    def set_option_clipboard(self):
        self.option_selected = 'clipboard'
        self.activate()
    def set_option_curve(self):
        self.option_selected = 'curve'
        self.activate()
    def set_option_file(self):
        self.option_selected = 'file'
        self.activate()

    
    def get_last_item(self):
        if self._last_item is not None:
            return self._last_item()

    def create_shape(self):
        from guiqwt.shapes import XRangeSelection
        return XRangeSelection(0, 0)

    def move(self, filter, event):
        super(CutSignalTool, self).move(filter, event)
    
    def get_message(self):
        if self.option_selected == 'curve':
            return 'make new curve with the selected portion of data ?'
        if self.option_selected == 'clipboard':
            return 'copy the selected portion of data to clipboard ?'
        if self.option_selected == 'file':
            return 'save the selected portion of data to file ?'
    
    def get_truncated_data(self):
        old_one = displayed_curve()
        #item = self.get_associated_item(self.get_active_plot())
        data = old_one.data
        range = self.shape.get_range()
        return data[range[0]:range[1]]
        
    def end_move(self, filter, event):
        truncated_data = self.get_truncated_data()
        self.shape.hide()
        super(CutSignalTool, self).end_move(filter, event)
        plot = self.get_active_plot()
        message_box = QtGui.QMessageBox(plot)
        answer = message_box.question(plot, 'cut signal', self.get_message(), 'No', 'Yes')
        
        if not answer:
            return
        if self.option_selected == 'clipboard':
            clip = _APP.clipboard()
            csv_string = StringIO()
            truncated_data.to_csv(csv_string)
            clip.setText(csv_string.getvalue())
        if self.option_selected == 'file':
            filename = QtGui.QFileDialog.getSaveFileName()
            truncated_data.to_csv(filename)        
        if self.option_selected == 'curve':
            old_one = displayed_curve()
            curve = models.CurveDB()
            curve.set_params(**old_one.params)
            curve.tags = old_one.tags + ["portion"]
            curve.name = "portion_of_" +  str(old_one.id)
            curve.date = datetime.now()
            curve.set_data(truncated_data)
            old_one.add_child(curve)
            
        
    def get_associated_item(self, plot):
        items = plot.get_selected_items(item_type=ICurveItemType)
        if len(items) == 1:
            self._last_item = weakref.ref(items[0])
        return self.get_last_item()
        
    def update_status(self, plot):
        item = self.get_associated_item(plot)
        self.action.setEnabled(item is not None)

class CurveDisplayLeftPanel(QtGui.QWidget):
    delete_done = QtCore.pyqtSignal()
    save_pressed = QtCore.pyqtSignal()
    
    def __init__(self, parent=None):
        super(CurveDisplayLeftPanel, self).__init__(parent)     
        self.displayed_curve_id = None
        self.setup_plot_widget()
        self.lay = QtGui.QVBoxLayout()
        
        self.lay.addWidget(self.toolbar)
        self.lay.addWidget(self.plot_widget)
        self.alter_curve_widget = CurveAlterWidget(self)
        self.alter_curve_widget.curve_saved.connect(self.save_pressed)
        self.alter_curve_widget.delete_done.connect(self.delete_done)
        self.lay.addWidget(self.alter_curve_widget)
        self.setLayout(self.lay)
        
    @property
    def displayed_curve(self):
        if self.displayed_curve_id:
            return models.CurveDB.objects.get(id=self.displayed_curve_id)
    
    def setup_plot_widget(self):
        self.plot_widget = plot.CurveWidget(self, 'curve graph',
                                            show_itemlist=False)
        self.plot_widget.plot.set_antialiasing(True)
        
        #self.plot_widget.register_all_curve_tools()
        #self.plot_widget.add_tool(guiqwt.tools.AntiAliasingTool)
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
    
        self.curve_item = make.curve([], [], color='b')
        self.plot_widget.plot.add_item(self.curve_item)
        
        self.manager.register_all_curve_tools()
        self.manager.add_tool(CutSignalTool)
        #=============================
        # for tools such as CurveStatsTool to work 
        # the curve needs to have been selected at least once.
        self.plot_widget.plot.set_active_item(self.curve_item)
        self.curve_item.unselect()
        #=============================

    def display_curve(self, curve):
        self.displayed_curve_id = curve.id
        if curve:
            self.plot_widget.get_plot().set_title(str(curve.id) + " (" + curve.params["curve_type"] + ")")
            #self.plot_widget.title = str(curve.id)
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
            
    def refresh(self):
        if self.displayed_curve:
            self.display_curve(self.displayed_curve)
    
    def save_curve(self, curve):
        self.alter_curve_widget.save_curve(curve) 
            
class CurveDisplayWidget(QtGui.QSplitter):
    delete_done = QtCore.pyqtSignal()
    def __init__(self, parent=None):
        super(CurveDisplayWidget, self).__init__(parent)
        self.left_panel = CurveDisplayLeftPanel()
        self.addWidget(self.left_panel)
        self.display_params = ParamsDisplayWidget()
        self.display_params.curve_modified.connect(self.left_panel.alter_curve_widget.curve_modified)
        self.left_panel.alter_curve_widget.curve_modified.connect(self.display_params.refresh)
        self.addWidget(self.display_params)
        self.left_panel.alter_curve_widget.curve_saved.connect(self.refresh_params)
        
        self.left_panel.delete_done.connect(self.delete_done)
        self.displayed_curve_id = None
        self._displayed_curve = None
        
    @property
    def displayed_curve(self):
        if self._displayed_curve:
            return self._displayed_curve
        else:
            return None
            if self.displayed_curve_id:
                return models.CurveDB.objects.get(id=self.displayed_curve_id)
    
    def refresh(self):
        self.left_panel.refresh()
        self.refresh_params()
    
    def refresh_params(self):
        self.display_params.refresh()
        #print self.displayed_curve.params
        #if self.displayed_curve:
        #    self.display_params.display_curve(self.displayed_curve)
    
    def save(self):
        curve = self.displayed_curve
        self.save_curve(curve)
        
    def save_curve(self, curve):
        self.left_panel.save_curve(curve)
    
    def display_curve(self, curve):
        self._display_curve = curve
        self.displayed_curve_id = curve.id
        self.left_panel.display_curve(curve)
        if curve:
            self.display_params.display_curve(curve)