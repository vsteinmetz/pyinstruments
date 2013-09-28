from pyinstruments.curvefindernew.models import CurveDB

from PyQt4 import QtCore, QtGui

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
        curves = self.parent().query().order_by('id')
        self._tree_widget.blockSignals(True)
        self._tree_widget.clear()
        self._tree_widget.blockSignals(False)
        for curve in curves:
            item = QtGui.QTreeWidgetItem([curve.params['name']])
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
        """ First option: Plot curve(s)"""
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
     
    