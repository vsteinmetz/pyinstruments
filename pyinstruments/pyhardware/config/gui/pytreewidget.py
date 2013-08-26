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
        self.types = []
        for index, (name, type_) in enumerate(col_names_and_types):
            self.headerItem().setText(index, \
                                      QtGui.QApplication.translate( \
                                                        "MainWindow", \
                                                        name, \
                                                        None, \
                                                        QtGui.QApplication.\
                                                        UnicodeUTF8))
            if type_ not in ['string', 'text']:
                raise ValueError('authorized types are string and text')
            self.types.append(type_)
#        self.itemChanged.connect(self.item_changed)


    def col_nr(self, col_name):
        """returns the index of the column named col_name"""
        
        for index in range(self.columnCount()):
            if self.headerItem().text(index) == str(col_name):
                return index
        raise KeyError("no column named " + str(col_name))
        
    def add_item(self, *args):
        """adds a top level item, with labels in the successive columns as 
        found in args.
        """
        
        labels = list(args)
        itm = PyTreeWidgetItem(self, labels)
        itm.setFlags(itm.flags() | QtCore.Qt.ItemIsUserCheckable)
        if self.is_editable:
            itm.setFlags(itm.flags() | QtCore.Qt.ItemIsEditable)        
        
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
            if ite.text(self.main_key) == val:
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
    
    edit_pressed = QtCore.pyqtSignal(QtGui.QTreeWidgetItem, int, name='edit_pressed')

class TextDialog(QtGui.QDialog):
    def __init__(self, parent = None):
        super(TextDialog, self).__init__(parent)
        self.lay = QtGui.QVBoxLayout()
        self.text_edit = QtGui.QPlainTextEdit(self)
        self.lay.addWidget(self.text_edit)
        self.button_ok = QtGui.QPushButton('OK')
        self.button_cancel = QtGui.QPushButton('Cancel')
        self.hlay = QtGui.QHBoxLayout()
        self.hlay.addWidget(self.button_cancel)
        self.hlay.addWidget(self.button_ok)
        self.lay.addLayout(self.hlay)
        self.setLayout(self.lay)
        self.button_cancel.pressed.connect(self.reject)
        self.button_ok.pressed.connect(self.accept)
        
    def text(self):
        return self.text_edit.toPlainText()    
    
    def set_text(self, text):
        self.text_edit.setPlainText(text)    

class PyTreeWidgetItem(QtGui.QTreeWidgetItem):
    """
    Wrapper for an item in the tree
    """
    
    def __init__(self, parent_tree, list_val):
        self.long_texts = list_val
        self.parent_tree = parent_tree
        self.buttons = []*len(list_val)
        super(PyTreeWidgetItem, self).__init__(list_val)
        self.parent_tree.addTopLevelItem(self)
        for index, type_ in enumerate(self.parent_tree.types):
            if type_ == 'text':
                button = QtGui.QPushButton("edit...")
                self.buttons.append(button)
                self.parent_tree.setItemWidget(self, index, button)
                self.current_index = index
                def emit_with_index(itm=self, idx=index):
                    print "alors"
                    self.parent_tree.edit_pressed.emit(itm, idx)
                button.pressed.connect(emit_with_index)
        self.parent_tree.edit_pressed.connect(self.new_text)
        
                
    def new_text(self, item, index):
        if item==self:
            self.text_dialog = TextDialog()
            self.text_dialog.accepted.connect(self._i_changed)
            self.text_dialog.set_text(self.long_texts[index])
            self.text_dialog.exec_()
            
    
    def _i_changed(self):
        self.long_texts[self.current_index] = str(self.text_dialog.text())
        self.parent_tree.itemChanged.emit(self, 0)
    
    def set_values(self, *args):
        for index, val in enumerate(args):
            if self.parent_tree.types[index] == "string":
                if val:
                    self.setText(index, val)
            else:
                self.long_texts[index] = val
    
    def val(self, col):                
        """column can either be a number or the name of the column"""
        
        if isinstance(col, basestring):
            index = self.parent_tree.col_nr(col)
        else:
            index = col
        if self.parent_tree.types[index] == 'string':
            return str(self.text(index))
        else:
            return self.long_texts[index]
        
    def set_color(self, col_nr , color_str):
        self.setBackgroundColor(col_nr, QtGui.QColor(color_str))
     