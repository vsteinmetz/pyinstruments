"""
Defines a class inheriting from QTreeWidget to handle instruments
configuration
"""

from PyQt4 import QtCore, QtGui

class PyTreeWidget(QtGui.QTreeWidget):
    """
    a class inheriting from QTreeWidget to handle instruments
    configuration
    """
    
    def __init__(self, col_names_and_types, main_key=0, is_editable=True):
        super(PyTreeWidget, self).__init__()
        self.main_key = main_key
        self.is_editable = is_editable
        for index, (name, type_) in enumerate(col_names):
            self.headerItem().setText(index, \
                                      QtGui.QApplication.translate( \
                                                        "MainWindow", \
                                                        name, \
                                                        None, \
                                                        QtGui.QApplication.\
                                                        UnicodeUTF8))
        self.itemChanged.connect(self.item_changed)


    def item_changed(self, item, col):
        """
        an item in the gui was changed
        """
        
        if item.types[col] == bool:
            res = item.checkState(col) != 0
            self.blockSignals(True)
            item.setText(col, str(res))
            

    def col_nr(self, col_name):
        """returns the index of the column named col_name"""
        
        for index in range(self.columnCount()):
            if self.headerItem().text(index) == str(col_name):
                return index
        raise KeyError("no column named " + str(col_name))
        
    def add_item(self, *args):
        """adds a top level item, with labels in the successive columns as 
        found in args.
        if a list is provided, will create a combobox,
        if boolean provided, makes a checkbox
        """
        
        labels = [""]*len(args)
        choices = [None]*len(args)
        boolean = [None]*len(args)
        types = [None]*len(args)
        for index, val in enumerate(args):
            if isinstance(val, basestring):
                labels[index] = val
                types[index] = str
            if isinstance(val, list):
                choices[index] = val
                types[index] = list
            if isinstance(val, bool):
                boolean[index] = val
                types[index] = bool
        
        itm = PyTreeWidgetItem(labels)
        itm.parentTree = self
        itm.types = types
        itm.setFlags(itm.flags() | QtCore.Qt.ItemIsUserCheckable)
        if self.is_editable:
            itm.setFlags(itm.flags() | QtCore.Qt.ItemIsEditable)
        
        self.addTopLevelItem(itm)
        for index, (choice, boo) in enumerate(zip(choices, boolean)):
            if choice is not None:
                cmb = ComboBoxItem(itm, index)
                for c in choice:
                    cmb.addItem(c)
                self.setItemWidget(itm, index, cmb)
            if boo is not None:
                if boo == "False":
                    boo = False
                if boo == "True":
                    boo = True
                itm.setCheckState(index, boo*2)
                self.item_changed(itm, index)
        return itm
    
    
    def remove_all_items(self):
        """removes all items from the Tree but keeps the column structure"""
        
        for index in range(self.topLevelItemCount()):
            ite = self.takeTopLevelItem(0)
            del ite

    def __getitem__(self, val):
        """returns an item according to the main_key column value"""
        
        if(self.topLevelItemCount() == 0):
            raise KeyError("no elements in the tree")
        for index in range(self.topLevelItemCount()):
            ite = self.topLevelItem(index)
            if ite.val(self.main_key) == val:
                return ite 
        raise KeyError("no element with value " + \
                       str(val) + \
                       " in column " + \
                       str(self.main_key) + \
                       " in the tree")
    
    def __iter__(self):
        """iterator on the items"""
        
        for index in range(self.topLevelItemCount()):
            itm = self.topLevelItem(index)
            yield itm

    def __len__(self):
        return self.topLevelItemCount()

    def __delitem__(self):
        raise NotImplementedError("That should have been though, sorry...")

    def __setitem__(self):
        raise NotImplementedError("That should have been though, sorry...")


class PyTreeWidgetItem(QtGui.QTreeWidgetItem):
    """
    Wrapper for an item in the tree
    """
    
    def val(self, col):
        """column can either be a number or the name of the column"""
        
        if isinstance(col, basestring):
            index = self.parentTree.col_nr(col)
        else:
            index = col
        if self.types[index] == bool:
            if str(self.text(index)) == 'True':
                return True
            if str(self.text(index)) == 'False':
                return False
        else:
            return str(self.text(index))
    
    def set_values(self, *args):
        """displays the values as they appear in args. raises an exception 
        if something is inconsistent with the possible values previously 
        entered in add_item
        """
        
        for index, val in enumerate(args):
            self._set_val(index, val)

    def set_value(self, **kwds):
        """
        Sets the value for the whole line
        """
        
        if len(kwds)!=1:
            raise ValueError("set_value expects only a single kwd:value pair")
        col = kwds.keys()[0]
        val = kwds.values()[0]
        for index in range(self.parentTree.columnCount()):
            if kwds.keys()[0] == self.parentTree.headerItem().text(index):
                self._set_val(index, val)
                
    def _set_val(self, index, val):
        """
        sets only one value
        """
        
        if self.types[index] == str:
            self.setText(index, str(val))
        if self.types[index] == bool:
            if val == "True":
                val = True
            if val == "False":
                val = False
            if not isinstance(val, bool):
                raise ValueError("boolean expected for a checkbox")
            self.setCheckState(index, val*2)
            self.parentTree.item_changed(self, index)
        if self.types[index] == list:
            #self.parentTree.itemWidget(self,1)
            cmb = self.parentTree.itemWidget(self, index)
            for index in range(cmb.count()):
                if cmb.itemText(index) == val:
                    cmb.setCurrentIndex(index)
               
    def set_color(self, col_nr , color_str):
        self.setBackgroundColor(col_nr, QtGui.QColor(color_str))    
         
class ComboBoxItem(QtGui.QComboBox):
    """
    Item for multiple choice
    """
    
    def __init__(self, item, column):
        super(ComboBoxItem, self).__init__()
        self.item = item
        self.column = column
        QtCore.QObject.connect(self, \
                               QtCore.SIGNAL("currentIndexChanged(int)"), \
                               self.change_item)

    #@QtCore.pyqtSlot(int)
    def change_item(self, index):
        """
        selected item changed
        """
        
        self.item.setText(self.column, self.itemText(index))

    def data(self):
        """
        returns the data string associated with the combobox value
        """
        
        return str(tl.data(0, QtCore.Qt.UserRole).toString())
     