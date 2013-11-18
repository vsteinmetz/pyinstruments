from pyinstruments.curvestore.models import Tag, top_level_tags
from pyinstruments.curvestore.tags import ROOT


import sys 
from PyQt4.QtCore import * 
from PyQt4.QtGui import * 
from PyQt4 import QtCore, QtGui
from copy import deepcopy 
from cPickle import dumps, load, loads 
from cStringIO import StringIO 



def oldest_ancestors(list_of_nodes):
    """
    returns a list where elements that are descendant of others have been removed
    """
    
    oldest = set()
    for node in list_of_nodes:
        ancestor = node.parent
        older_found = False
        while(ancestor and not older_found):
            older_found = ancestor in list_of_nodes
            ancestor = ancestor.parent
        if not older_found:
            oldest = oldest.union([node])
    return list(oldest)
                

class PyMimeData(QMimeData): 
    """ 
    The PyMimeData wraps a Python instance as MIME data. 
    """ 
    # The MIME type for instances. 
    MIME_TYPE = QString('application/x-ets-qt4-instance') 

    def __init__(self, data=None): 
        """ 
        Initialise the instance. 
        """ 
        QMimeData.__init__(self) 

        # Keep a local reference to be returned if possible. 
        self._local_instance = data 

        if data is not None: 
            # We may not be able to pickle the data. 
            try: 
                pdata = dumps(data) 
            except: 
                return 

            # This format (as opposed to using a single sequence) allows the 
            # type to be extracted without unpickling the data itself. 
            self.setData(self.MIME_TYPE, dumps(data.__class__) + pdata) 

    @classmethod 
    def coerce(cls, md): 
        """ 
        Coerce a QMimeData instance to a PyMimeData instance if possible. 
        """ 
        # See if the data is already of the right type.  If it is then we know 
        # we are in the same process. 
        if isinstance(md, cls): 
            return md 

        # See if the data type is supported. 
        if not md.hasFormat(cls.MIME_TYPE): 
            return None 

        nmd = cls() 
        nmd.setData(cls.MIME_TYPE, md.data()) 

        return nmd 

    def instance(self): 
        """ 
        Return the instance. 
        """ 
        
        if self._local_instance is not None: 
            return self._local_instance 

        io = StringIO(str(self.data(self.MIME_TYPE))) 

        try: 
            # Skip the type. 
            load(io) 

            # Recreate the instance. 
            return load(io) 
        except: 
            pass 

        return None 

    def instanceType(self): 
        """ 
        Return the type of the instance. 
        """ 
        if self._local_instance is not None: 
            return self._local_instance.__class__ 

        try: 
            return loads(str(self.data(self.MIME_TYPE))) 
        except: 
            pass 

        return None 


class TagModel(QAbstractItemModel):
    def __init__(self, parent=None): 
        super(TagModel, self).__init__(parent) 

        self.treeView = parent 
        self.headers = ['Item'] 

        self.columns = 1
        

    def supportedDropActions(self): 
        return Qt.CopyAction | Qt.MoveAction


    def flags(self, index): 
        defaultFlags = QAbstractItemModel.flags(self, index) 

        if index.isValid(): 
            return Qt.ItemIsEditable | Qt.ItemIsDragEnabled | Qt.ItemIsDropEnabled | defaultFlags 

        else: 
            return Qt.ItemIsDropEnabled | defaultFlags 


    def headerData(self, section, orientation, role): 
        if orientation == Qt.Horizontal and role == Qt.DisplayRole: 
            return QVariant(self.headers[section]) 
        return QVariant() 

    def mimeTypes(self): 
        types = QStringList() 
        types.append('application/x-ets-qt4-instance') 
        return types 

    def mimeData(self, index): 
        node = [self.nodeFromIndex(i) for i in index]
        mimeData = PyMimeData(node) 
        return mimeData 


    def dropMimeData(self, mimedata, action, row, column, parentIndex): 
        if action == Qt.IgnoreAction: 
            return True 
        
        dragNodes = mimedata.instance()
        dragNodes = oldest_ancestors(dragNodes) 
        parentNode = self.nodeFromIndex(parentIndex) 
        if not QtGui.QMessageBox.question(QtGui.QWidget(),
                                   'Confirm move',
                                   "Do you want to move:\n" + \
                                   ','.join([dn.name for dn in dragNodes]) + \
                                   "\nbelow: " + parentNode.name + '?!',
                                    'Cancel', 'OK'):
            return
        for dragNode in dragNodes:
            # make an copy of the node being moved 
            newNode = deepcopy(dragNode) 
            newNode.move(parentNode)
            self.insertRow(len(parentNode)-1, parentIndex)
        self.emit(SIGNAL("dataChanged(QModelIndex,QModelIndex)"), parentIndex, parentIndex) 
        return True 


    def insertRow(self, row, parent): 
        return self.insertRows(row, 1, parent) 


    def insertRows(self, row, count, parent): 
        print 'insertRows'
        self.beginInsertRows(parent, row, (row + (count - 1))) 
        self.endInsertRows() 
        return True 


    def removeRow(self, row, parentIndex):
        return self.removeRows(row, 1, parentIndex) 


    def removeRows(self, row, count, parentIndex):
        #import pdb
        #pdb.set_trace()
        #print 'row:', row, ' count:', count, 'parentIndex: ', parentIndex, 'node:', self.nodeFromIndex(parentIndex) 
        self.beginRemoveRows(parentIndex, row, row+count-1) 
        node = self.nodeFromIndex(parentIndex)
        #print node.children
        for r in range(row, row+count):
            node.removeChild(row) ## removing on a reduced list
        self.endRemoveRows()
        return True 


    def index(self, row, column, parent): 
        node = self.nodeFromIndex(parent) 
        return self.createIndex(row, column, node.childAtRow(row)) 


    def data(self, index, role): 
        if role == Qt.DecorationRole: 
            return QVariant() 

        if role == Qt.TextAlignmentRole: 
            return QVariant(int(Qt.AlignTop | Qt.AlignLeft)) 

        if role != Qt.DisplayRole: 
            return QVariant() 

        node = self.nodeFromIndex(index) 

        if index.column() == 0: 
            return QVariant(node.name) 

        elif index.column() == 1: 
            return QVariant(node.state) 

        elif index.column() == 2: 
            return QVariant(node.description) 
        else: 
            return QVariant() 


    def columnCount(self, parent): 
        return self.columns 


    def rowCount(self, parent): 
        node = self.nodeFromIndex(parent) 
        if node is None: 
            return 0 
        return len(node) 


    def parent(self, child): 
        if not child.isValid(): 
            return QModelIndex() 

        node = self.nodeFromIndex(child) 

        if node is None: 
            return QModelIndex() 

        parent = node.parent 

        if parent is None: 
            return QModelIndex() 

        grandparent = parent.parent 
        if grandparent is None: 
            return QModelIndex() 
        row = grandparent.rowOfChild(parent) 

        assert row != - 1 
        return self.createIndex(row, 0, parent) 


    def nodeFromIndex(self, index): 
        return index.internalPointer() if index.isValid() else ROOT

    def refresh(self):
        self.beginRemoveRows(QtCore.QModelIndex(), 0, self.rowCount(QtCore.QModelIndex())) 
        ROOT.build_children_from_model()
        self.endRemoveRows()
    

class TagTreeView(QTreeView):
    def __init__(self, parent=None): 
        super(TagTreeView, self).__init__(parent) 

        self.myModel = TagModel() 
        self.setModel(self.myModel) 

        self.dragEnabled() 
        self.acceptDrops() 
        self.showDropIndicator() 
        self.setDragDropMode(QAbstractItemView.InternalMove) 
        self.setSelectionMode(self.ExtendedSelection)

        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._contextMenu)
        

        self.connect(self.model(), SIGNAL("dataChanged(QModelIndex,QModelIndex)"), self.change) 
        self.expandAll() 

    def change(self, topLeftIndex, bottomRightIndex): 
        self.update(topLeftIndex) 
        self.expandAll() 
        self.expanded() 

    def expanded(self): 
        for column in range(self.model().columnCount(QModelIndex())): 
            self.resizeColumnToContents(column)

    def refresh(self):
        self.model().refresh()
        
    
    def _get_tag_from_index(self, index):
        parent = self.model().nodeFromIndex(index)
        return parent.name
        
        parent_names = []
        while parent:
            parent_names.append(parent.name)
            parent = parent.parent
        parent_names.reverse()
        name_clicked = ""
        for string in parent_names:
            if name_clicked != "":
                name_clicked += '/'
            name_clicked += string
        return name_clicked

    
    def _exec_menu_at_right_place(self, menu, point):
        p = QtCore.QPoint(point)
        p.setY(p.y() + menu.height())
        where = self.mapToGlobal(p)
        menu.exec_(where)   
        
    def _contextMenu(self, point):
        """
        Context Menu (right click on the treeWidget)
        """
        
        index = self.indexAt(point)
        name_clicked = self._get_tag_from_index(index)
        node_clicked = self.model().nodeFromIndex(index)
        
        
        
        def add_tag():
            dialog = QtGui.QInputDialog()
            dialog.setTextValue(name_clicked)
            #if name_clicked != "":
            #    proposition = name_clicked + '/'
            #else:
            #    proposition = name_clicked
            (tag, confirm) = dialog.getText(QtGui.QWidget(), \
                                     "new tag", \
                                     "enter tag name", \
                                     0, \
                                     "")
            tag = str(tag)
            if confirm:
                if tag.find("/")>=0:
                    raise ValueError("""tag name should not contain /""")
                if tag=="":
                    raise ValueError("""tag name should not be blank""")
                node_clicked.add_child(tag)
                self.model().emit(SIGNAL("dataChanged(QModelIndex,QModelIndex)"), index, index) 
                
                
        def remove_tag(dummy, name=name_clicked):
            dial = QtGui.QMessageBox()
            dial.setText("Delete tag '" + name + "': are you sure ?")
            dial.setInformativeText("Tag will be removed from all referenced curves...")
            dial.setStandardButtons(QtGui.QMessageBox.Cancel|QtGui.QMessageBox.Ok)
            dial.setDefaultButton(QtGui.QMessageBox.Ok);
            if dial.exec_():
                tag = node_clicked.model_tag()
                self.model().removeRow(index.row(), index.parent())
                tag.remove()
                
                
        def rename(dummy, name=name_clicked):
            dialog = QtGui.QInputDialog()
            dialog.setTextValue(name_clicked)
            proposition = name_clicked
            (tag, confirm) = dialog.getText(QtGui.QWidget(), \
                                     "rename tag", \
                                     "enter tag name", \
                                     0, \
                                     proposition)
            if confirm:
                new_name = str(tag)
                node_clicked.rename(new_name)
                self.model().emit(SIGNAL("dataChanged(QModelIndex,QModelIndex)"), index, index) 
                
        
        
        menu = QtGui.QMenu(self)
        action_add_tag = QtGui.QAction("add tag...", self)
        action_add_tag.triggered.connect(add_tag)
        menu.addAction(action_add_tag)

        action_rename_tag = QtGui.QAction("rename tag", self)
        action_rename_tag.triggered.connect(rename)
        menu.addAction(action_rename_tag)
        
        action_remove_tag = QtGui.QAction("remove tag", self)
        action_remove_tag.triggered.connect(remove_tag)
        menu.addAction(action_remove_tag)
        
        action_refresh_list = QtGui.QAction("refresh list", self)
        action_refresh_list.triggered.connect(self.refresh)
        menu.addAction(action_refresh_list)
        
        self._exec_menu_at_right_place(menu, point)
