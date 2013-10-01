from pyinstruments.curvestore.models import CurveDB
from pyinstruments.curvefinder.gui.plot_window import get_window

from curve.fitting import FitFunctions

from PyQt4 import QtCore, QtGui
import functools
import numpy

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
    
    def add_curve(self, curve):
        """
        Adds a curve and all its childs in the list if not allready there.
        If the curve is a child, then adds the parent with all the childs
        """
        # check if the curve is a child
        if curve.parent:
            return self.add_curve(curve.parent)
        
        # check if curve already there
        if curve in self:
            return
        
        #otherwise, add the curve
        item = QtGui.QTreeWidgetItem([curve.params['name']])
        item.pk = curve.pk
        self._tree_widget.addTopLevelItem(item)
        
        #and its childs
        for child in curve.childs.all():
            item_child = QtGui.QTreeWidgetItem([child.params['name']])
            item.addChild(item_child)
            item_child.pk = child.pk 
        
    def __contains__(self, curve):
        if not isinstance(curve, int):
            curve = curve.pk
        return curve in self.ids()
    
    def ids(self):
        return [self._tree_widget.topLevelItem(index).pk \
               for index in \
               range(self._tree_widget.topLevelItemCount())]
    
    def refresh(self):
        previous_id = None
        previous_selected = self._tree_widget.currentItem()
        if previous_selected:
            previous_id = previous_selected.pk
        curves = self.parent().query().order_by('id')
        self._tree_widget.blockSignals(True)
        self._tree_widget.clear()
        for curve in curves:
            self.add_curve(curve)
        self._tree_widget.blockSignals(False)
        
        if not previous_id:
            return
        if previous_id in self:
            self.select_by_id(previous_id)
        else:
            dist = numpy.array(self.ids()) - previous_id
            if len(dist[dist>0]):
                next_id = min(dist[dist>0]) + previous_id
            else:
                if len(dist[dist<0]):
                    next_id = max(dist[dist<0]) + previous_id
                else:
                    return
            self.select_by_id(next_id)
    
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
        ### First option: Plot curve(s)
        if len(curves)==1:
            message = "plot in " + curves[0].params['window']
            message_delete = "delete " + curves[0].params['name']
        else:
            message = "plot these in their window"
            message_delete = "delete " + str(len(curves)) + " curves ?"
        
        def delete(dummy, curves=curves):
            message_box = QtGui.QMessageBox(self)
            answer = message_box.question(self, 'delete', message_delete, 'No', 'Yes')
            if not answer:
                return
            for curve in curves:
                curve.delete()
            self.refresh()
        
        def plot(dummy, curves=curves):
            for curve in curves:
                win = get_window(curve.params["window"])
                win.plot(curve)
                win.show()
        
        menu = QtGui.QMenu(self)
        action_plot = QtGui.QAction(message, self)
        action_plot.triggered.connect(plot)
        
        action_delete = QtGui.QAction(message_delete, self)
        action_delete.triggered.connect(delete)
        
        menu.addAction(action_plot)
        menu.addAction(action_delete)
         
        ###second option: fit curve(s)
        
        fitfuncs = list()
        for f in dir(FitFunctions):
            if not f.startswith('_'):
                fitfuncs.append(f)
        
        fitsmenu = menu.addMenu(    'fits')
        
        
        def fitcurve(curvestofit, funcname):
            for curve in curvestofit:
                curve.fit(func = funcname, autosave=True, maxiter=20)
                
        for f in fitfuncs:
            specificfit = functools.partial(fitcurve, curvestofit=curves, funcname=f)
            action_add_tag = QtGui.QAction(f, self)
            action_add_tag.triggered.connect(specificfit)
            fitsmenu.addAction(action_add_tag)
        
        menu.exec_(event.globalPos())
     
    