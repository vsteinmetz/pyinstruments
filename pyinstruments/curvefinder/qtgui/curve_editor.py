from PyQt4 import QtGui, QtCore
from pyinstruments.curvefinder.qtgui.curve_filter_widget import DateConstraintWidget, \
                                      StringFilterWidget, \
                                      ComboFilterWidget, \
                                      TagFilterWidget, \
                                      BoolFilterWidget
from pyinstruments.curvefinder.models import Window, CurveDB
from pyinstruments.curvefinder.qtgui.gui import CurveCreateWidget
from curve_editor_menus import CurveEditorMenuBar, CurveEditorToolBar, NamedCheckBox 
import pyinstruments.datastore.settings
from pyinstruments.curvefinder.qtgui.plot_window import PlotDialog
from pyinstruments.curvefinder.fitting import FitFunctions

from numpy import array
from guiqwt import plot
from guiqwt.builder import make
import datetime
import dateutil
import json
from collections import OrderedDict
import os
import functools



WINDOWS = dict()

def get_window(name):
    try:
        win = WINDOWS[name]
    except KeyError:
        win = PlotDialog(name)
        WINDOWS[name] = win
    return win

class CurveEditor(QtGui.QMainWindow, object):
        
    def __init__(self):
        super(CurveEditor, self).__init__()
        
        self.menubar = CurveEditorMenuBar(self)
            
        self.setMenuBar(self.menubar)
        self._filter_widget = FilterWidgetFull(self)
        #self._list_curve_widget = self._get_list_curve_widget()
        self.addDockWidget(\
                QtCore.Qt.DockWidgetArea(QtCore.Qt.LeftDockWidgetArea), \
                self._filter_widget)
        #self.addDockWidget(\
        #self._filter_widget._widget_full._filter_layout.addWidget(\
                #QtCore.Qt.DockWidgetArea(QtCore.Qt.RightDockWidgetArea), \
        #        self._list_curve_widget)
        self.toolbar = CurveEditorToolBar(self)
        
        self.addToolBar(self.toolbar)
        self.toolbar.popup_unread_activated.connect(\
                                            self.activate_popup_unread)
        self.toolbar.popup_unread_deactivated.connect(\
                                            self.deactivate_popup_unread)
        
        self._curve_display_widget = CurveDisplayWidget(self)
        self.setCentralWidget(self._curve_display_widget)
        self._filter_widget.value_changed.connect(self.refresh)
        self._filter_widget.value_changed.connect(self.save_defaults)        
        self._filter_widget.current_item_changed.connect(self.display)
        
        
        settings = QtCore.QSettings("pyinstruments", "pyinstruments")
        default_json = str(settings.value("curve_editor_defaults").\
                                                            toString())
        if default_json != "":
            defaults = json.loads(default_json)
            for key in ["date_lte", "date_gte", "date_equals"]:
                enabled, val = defaults[key]
                if val:
                    defaults[key] = enabled, dateutil.parser.parse(val)
        else:
            defaults = {}
        self.set_defaults(**defaults)
        
        self.popup_timer = QtCore.QTimer()
        self.popup_timer.timeout.connect(self.popup_unread_curves)
        self.popup_timer.setSingleShot(False)
        self.popup_timer.setInterval(500) #ms
        self.popup_unread = False
        
        self.show()

    @property
    def plot_popups(self):
        return self.toolbar._checkbox_plot_popups.check_state

    def popup_unread_curves(self):
        unread = CurveDB.objects.filter(user_has_read=False)
        if unread:
            self._filter_widget.refresh()
            curve = unread[0]
            self.display(curve)
            if self.plot_popups:
                win = get_window(curve.window_txt)
                win.plot(curve)
                

    def activate_popup_unread(self):
        self.popup_unread = True
        self.popup_timer.start()
    
    def deactivate_popup_unread(self):
        self.popup_unread = False
        self.popup_timer.stop()
    
    def display(self, curve):
        self._curve_display_widget.display(curve)
        if  curve:
            self._filter_widget.select_by_id(curve.id)
    
    def set_defaults(self, **kwds):
        self._filter_widget.set_defaults(**kwds)
    
    def save_defaults(self):
        defaults = self._filter_widget.get_values()
        for key in ["date_lte", "date_gte", "date_equals"]:
            enabled, val = defaults[key]
            val = str(val)
            defaults[key] = enabled, val
        defaults_json = json.dumps(defaults)
        settings = QtCore.QSettings("pyinstruments", "pyinstruments")
        settings.setValue("curve_editor_defaults", defaults_json)
    
    def refresh(self):
        self._filter_widget.refresh()
    
    def get_filter_widget(self):
        """
        mostly for interactive debugging purposes
        """
        
        return self._filter_widget._widget_full
    
    def get_list_widget(self):
        """
        mostly for interactive debugging purposes
        """
        
        return self._filter_widget._widget_full._list_widget
    
    def get_curve_display_widget(self):
        """
        mostly for interactive debugging purposes
        """
        
        return self._curve_display_widget
    
    #def _get_list_curve_widget(self):
    #    return ListCurveWidget(self)
        
    def get_query_set(self):
        return self._filter_widget.get_query_set()
        
    
class FilterWidgetFull(QtGui.QDockWidget):
    def __init__(self, parent):
        super(FilterWidgetFull, self).__init__(parent)
        self._widget_full = self._get_filter_widget()
        self._widget_full.value_changed.connect(self.value_changed)
        self._widget_full._list_widget.current_item_changed.connect( \
                                                self.current_item_changed)
        self.setWidget(self._widget_full)
        
    value_changed = QtCore.pyqtSignal(name = "value_changed")
    current_item_changed = QtCore.pyqtSignal(object, \
                                    name = "current_item_changed")
    
    def select_by_id(self, id):
        """if the curve is in the list, selects it, otherwise cancels
        the current selection
        """
        self._widget_full.select_by_id(id)
    
    def refresh(self):
        self._widget_full._list_widget.refresh()    
        
    def set_defaults(self, **kwds):
        self._widget_full.set_defaults(**kwds)
    
    def get_values(self):
        return self._widget_full.get_values()
    
    def get_query_set(self):
        return self._widget_full.get_query_set()
    
    def _get_filter_widget(self):
        class InnerFilterWidgetFull(QtGui.QWidget):
            def __init__(self, parent):
                super(InnerFilterWidgetFull, self).__init__(parent)
                self._lay = QtGui.QHBoxLayout()
                self._filter_layout = QtGui.QVBoxLayout()
                self._filters = OrderedDict()
                self._filters["unread"] = \
                    BoolFilterWidget('user_has_read', \
                                     False, \
                                     'only unread curves', \
                                     self)
                self._filters["date_equals"] = \
                    DateConstraintWidget('=', self)
                self._filters["date_lte"] = \
                    DateConstraintWidget('>=', self)
                self._filters["date_gte"] = \
                    DateConstraintWidget('<=', self)
                    
                self._filters["date_equals"].enabled_on.connect( \
                                                    self._disable_lte_gte)
                self._filters["date_lte"].enabled_on.connect( \
                                                    self._disable_equals)
                self._filters["date_gte"].enabled_on.connect( \
                                                    self._disable_equals)
                
                
                self._filters["name"] = \
                    StringFilterWidget('name', self)
                self._filters["comment"] = \
                    StringFilterWidget('comment', self)
                self._filters["window"] = \
                    ComboFilterWidget(Window, 'window', self)
                self._filters["tags"] = \
                    TagFilterWidget(self)    

            
                for name, filter in self._filters.iteritems():
                    self._filter_layout.addWidget(filter)
                    filter.value_changed.connect(self.value_changed)
                self._lay.addLayout(self._filter_layout)
                self._list_widget = ListCurveWidget(self)
                
                self._lay.addWidget(self._list_widget)
                self.setLayout(self._lay)
                
            value_changed = QtCore.pyqtSignal(name = "value_changed")
            
            def select_by_id(self, id):
                """if the curve is in the list, selects it, otherwise cancels
                the current selection
                """
                
                self._list_widget.select_by_id(id)
            
            def _disable_lte_gte(self):
                self._filters["date_lte"].enabled = False
                self._filters["date_gte"].enabled = False
                
            def _disable_equals(self):
                self._filters["date_equals"].enabled = False
            
            def get_values(self):
                values = {}
                for key, widget in self._filters.iteritems():
                    values[key] = widget.value
                return values
                
            def set_defaults(self, **kwds):
                for key, widget in self._filters.iteritems():
                    try:
                        val = kwds[key]
                    except KeyError:
                        print "no key " + key + " found" 
                    else:
                        if val:
                            widget.value = val
            
            def get_query_set(self):
                kwds = dict()
                ## first query for the required tags
                filters = self._filters.copy()
                tag_filter = filters.pop("tags")
                queryset = \
                    tag_filter.get_query_set()
                for name, filter in filters.iteritems():
                    kwds.update(filter.get_kwds_for_query())
                
                return queryset.filter(**kwds)
            
        return InnerFilterWidgetFull(self)
        
        
class ListCurveWidget(QtGui.QWidget, object):
    current_item_changed = QtCore.pyqtSignal(object)
    def __init__(self, parent):
        super(ListCurveWidget, self).__init__(parent)
        self._tree_widget = self._get_tree_widget()
        self._lay = QtGui.QVBoxLayout()
        self._refresh_button = QtGui.QPushButton('refresh')
        self._refresh_button.pressed.connect(self.refresh)
        self._lay_refresh = QtGui.QHBoxLayout()
        self._lay_refresh.addWidget(self._refresh_button)
        self._lay.addLayout(self._lay_refresh)
        
        self._lay.setContentsMargins(0, 0, 0, 0)
        self._lay.addWidget(self._tree_widget)
        self.refresh()
        self._tree_widget.itemSelectionChanged.connect(
                                          self._current_item_changed)
        self.setLayout(self._lay)
        self.setMinimumWidth(180)
        
    def _current_item_changed(self):
        if self.selected_curve:
            self.current_item_changed.emit(self.selected_curve)
    
    def select_by_id(self, id):
        """if the curve is in the list, selects it, otherwise cancels
        the current selection
        """
        #import pdb
        #pdb.set_trace()
        for index in range(self._tree_widget.topLevelItemCount()):
            item = self._tree_widget.topLevelItem(index)
            if item.pk == id:
                #item.setSelected(True)
                self._tree_widget.setCurrentItem(item)
                return
        self._tree_widget.clearSelection()
        
    @property
    def selected_curve(self):
        """
        Returns None if several or 0 curves are selected.
        """
        sel = self._tree_widget.selectedItems()
        if len(sel)!=1:
            return None
        else:
            try:
                curve = CurveDB.objects.get(pk = sel[0].pk)
            except CurveDB.DoesNotExist:
                return None
            else:
                return curve 

    @property
    def selected_curves(self):
        """
        Returns the list of selected curves
        """ 
        sel = self._tree_widget.selectedItems()
        curves = []
        for curve_item in sel:
            try:
                curve = CurveDB.objects.get(pk = curve_item.pk)
            except CurveDB.DoesNotExist:
                print "Didn't find curve id " + str(pk) + " in the db"
            else:
                curves.append(curve)
        return curves
        
    def refresh(self):
        next_select = None
        next_pk = None
        previous_selected = self.selected_curve
        previous_pk = None
        if previous_selected:
            previous_pk = previous_selected.pk
        curves = self.parent().get_query_set().order_by('id')
        self._tree_widget.blockSignals(True)
        self._tree_widget.clear()
        self._tree_widget.blockSignals(False)
        for curve in curves:
            item = QtGui.QTreeWidgetItem([curve.name])
            self._tree_widget.addTopLevelItem(item)
            item.pk = curve.pk
            if item.pk == previous_pk:
                next_select = item
                next_pk = item.pk
            
        if not next_select:
            next_select = self._tree_widget.topLevelItem(0)
        if next_select:
            self._tree_widget.blockSignals(True)
            next_select.setSelected(True)
            self._tree_widget.blockSignals(False)
            #self._tree_widget.setCurrentItem(next_select)
        if previous_pk != next_pk:
            self.current_item_changed.emit(self.selected_curve)
    
    def _get_tree_widget(self):
        class ListTreeWidget(QtGui.QTreeWidget):
            def __init__(self, parent):
                super(ListTreeWidget, self).__init__(parent)                    
                self.headerItem().setText(0, "curve name")
                self.setSelectionMode( \
                            QtGui.QAbstractItemView.ExtendedSelection)
        return ListTreeWidget(self)



            

    def contextMenuEvent(self, event):
        """
        Context Menu (right click on the treeWidget)
        """
        curves = self.selected_curves
        """ First a) option: Plot curve(s)"""
        if len(curves)==1:
            message = "plot in " + curves[0].window_txt
        else:
            message = "plot these in their window"
        
        def plot(dummy, curves=curves):
            for curve in curves:
                win = get_window(curve.window_txt)
                win.plot(curve)
        
        menu = QtGui.QMenu(self)
        action_add_tag = QtGui.QAction(message, self)
        action_add_tag.triggered.connect(plot)
        menu.addAction(action_add_tag)
        
        """ First b) option: Plot curve(s) with fits"""
        if len(curves)==1:
            messagefit = "plot with fits in " + curves[0].window_txt
        else:
            messagefit = "plot these with resp. fits in their window"
        
        def plotfit(dummy, curves=curves):
            for curve in curves:
                win = get_window(curve.window_txt)
                win.plot(curve)
                for children in curve.childs.all():
                    win.plot(children)
        
        action_add_tag_fit = QtGui.QAction(messagefit, self)
        action_add_tag_fit.triggered.connect(plotfit)
        menu.addAction(action_add_tag_fit)
          
        """second option: fit curve(s)"""
        
        fitfuncs = list()
        for f in dir(FitFunctions):
            if not f.startswith('_'):
                fitfuncs.append(f)
        
        fitsmenu = menu.addMenu(    'fits')

        def fitcurve(curvestofit, funcname):
            for curve in curvestofit:
                curve.fit(func = funcname, autosave=True, maxiter=20)
                
        for f in fitfuncs:
            specificfit = functools.partial(fitcurve,curvestofit=curves,funcname = f)
            action_add_tag = QtGui.QAction(f, self)
            action_add_tag.triggered.connect(specificfit)
            fitsmenu.addAction(action_add_tag)
        
        menu.exec_(event.globalPos())
     
    

class AllFieldDisplayWidget(QtGui.QWidget):
    def __init__(self, parent, dic):
        super(AllFieldDisplayWidget, self).__init__(parent)
        self._lay = QtGui.QGridLayout()
        self.field_display_widgets = dict()
        self.rows = 3
        row = 0
        col = 0
        for field, val in dic.iteritems():
            widget = FieldDisplayWidget(self, field, val)
            self.field_display_widgets[field] = widget
            self._lay.addWidget(widget, row, col)
            row += 1
            if row>=self.rows:
                row = 0
                col+=1
    
        self.setLayout(self._lay)
        self.setMinimumHeight(150)
        self.setMinimumWidth(600)
        self.setMaximumWidth(600)
class FieldDisplayWidget(QtGui.QWidget):
    def __init__(self, parent, field, value):
        super(FieldDisplayWidget, self).__init__(parent)
        self._lay = QtGui.QHBoxLayout()
        self.label = QtGui.QLabel(field + ' : ' + value)
        self._lay.addWidget(self.label)
        self.setLayout(self._lay)

class CurveIdWidget(QtGui.QWidget):
    def __init__(self, parent = None):
        super(CurveIdWidget, self).__init__(parent)
        self._lay = QtGui.QGridLayout()
        self.label_id = QtGui.QLabel("ID : ")
        self.label_type = QtGui.QLabel("")
        font = QtGui.QFont()
        font.setPointSize(20)
        self.label_id.setFont(font)
        self.label_type.setFont(font)
        self._title_lay = QtGui.QVBoxLayout()
        self._title_lay.addWidget(self.label_id)
        self._title_lay.addWidget(self.label_type)
        self._lay.addLayout(self._title_lay, 0, 0)
        self.setLayout(self._lay)
        self.widget_all_fields = AllFieldDisplayWidget(self, dict())
        self._lay.addWidget(self.widget_all_fields, 0, 1)
        self.delete_button = QtGui.QPushButton("Delete...")
        self.delete_button.pressed.connect(self.delete)
        self.delete_button.setMaximumWidth(100)
        self.delete_button.setMinimumHeight(150)
        self._lay.addWidget(self.delete_button, 0, 2)
        self.curve_displayed = None
        
    def delete(self, confirm=True):
        if not self.curve_displayed:
            return
        if confirm:
            
            message_box = QtGui.QMessageBox(self)
            answer = message_box.question(self, 'delete', \
                        'are you sure you want to delete curve id =' \
                        + str(self.curve_displayed.id) + ' ?', 'No', 'Yes')
            if not answer:
                return
        self.curve_displayed.delete()
        self.parent().parent().refresh()
    
    def dump_in_gui(self, curve):
        self.curve_displayed = curve
        fields = curve.get_subclass_fields()
        if self.widget_all_fields:
            self.widget_all_fields.deleteLater()
        self.widget_all_fields = AllFieldDisplayWidget(self, fields)
        self._lay.addWidget(self.widget_all_fields, 0, 1)
        self.label_id.setText("ID : " + str(curve.id))
        self.label_type.setText(\
                        curve.curve_types._choice_dict[curve.curve_type])

class CurveDisplayWidget(QtGui.QWidget):
    def __init__(self, parent):
        super(CurveDisplayWidget, self).__init__(parent)
        self.plot_widget = plot.CurveWidget(self, 'curve graph', \
                                            show_itemlist=False)
        self.plot_widget.setMinimumHeight(450)
        self.plot_widget.plot.set_antialiasing(True)
        self.plot_widget.register_all_curve_tools()
        self._lay = QtGui.QVBoxLayout()
        
        
        
        self.curve_id_widget = CurveIdWidget(self)
        self._lay.addWidget(self.curve_id_widget)
        self._lay.addWidget(self.plot_widget)
        self.setup_plot_widget()
        self.alter_curve_widget = CurveCreateWidget(parent = self)
        self.alter_curve_widget.curve_modified.connect(
                                    self.alter_curve_widget.save_button.show)
        self.alter_curve_widget.save_pressed.connect(
                                    self.alter_curve_widget.save_button.hide)
        self.alter_curve_widget.save_pressed.connect(self.save)
        self._lay.addWidget(self.alter_curve_widget)
        
        #---guiqwt curve item attribute:
        self.curve_item = make.curve([], [], color='b')
        self.plot_widget.plot.add_item(self.curve_item)
        self.setLayout(self._lay)
        self.displayed_curve = None
    
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
        self._lay.addWidget(self.toolbar)
        self.manager.register_all_curve_tools()
        #---
    
    def display(self, curve):
        self.displayed_curve = curve
        if curve:
            self.curve_id_widget.dump_in_gui(curve)
            self.alter_curve_widget.dump_in_gui(curve)
            self.curve_item.set_data(array(curve.data.index, \
                                    dtype = float), \
                                    array(curve.data, dtype = float))
            if self.autoscale:
                self.curve_item.plot().do_autoscale()
            self.curve_item.plot().replot()
        
            curve.user_has_read = True
            curve.save()
            self.alter_curve_widget.save_button.hide()