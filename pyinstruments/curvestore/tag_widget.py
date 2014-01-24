from pyinstruments.curvestore.models import CurveDB, Tag, top_level_tags
from pyinstruments.curvestore.tags import ROOT


import sys 
from PyQt4.QtCore import * 
from PyQt4.QtGui import * 
from PyQt4 import QtCore, QtGui
from copy import deepcopy 
from cPickle import dumps, load, loads 
from cStringIO import StringIO 
import json

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
    def __init__(self, root=ROOT, parent=None): 
        super(TagModel, self).__init__(parent) 

        self.treeView = parent 
        self.headers = ['Tags'] 

        self.columns = 1
        self.root = root

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
        types.append('application/curve_ids_json') 
        return types 

    def mimeData(self, index): 
        node = [self.nodeFromIndex(i) for i in index]
        mimeData = PyMimeData(node) 
        return mimeData 

    def dropMimeData(self, mimedata, action, row, column, parentIndex): 
        if action == Qt.IgnoreAction: 
            return True 
        parentNode = self.nodeFromIndex(parentIndex)
        where = parentNode.name
        if where=="":
            where = "root"
        full_tag = parentNode.fullname
        data_id = mimedata.data("application/curve_ids_json")
        if data_id.count(): #curves were dropped
            if where=="root":
                return
            ids = json.loads(data_id.data())
            if QtGui.QMessageBox.question(QtGui.QWidget(),
                                          "add tag",
                                          "do you want to assign tag " \
                                          + full_tag + " to " + str(len(ids)) \
                                          + " curves ?",
                                          "Cancel",
                                          "OK"):
                for curve_id in ids:
                    curve = CurveDB.objects.get(id=curve_id)
                    curve.tags.append(full_tag)
                    curve.save()
            return
        
        dragNodes = mimedata.instance()
        dragNodes = oldest_ancestors(dragNodes)
        
        if len(dragNodes)==1 and dragNodes[0]==parentNode:
            return
        
            
        if not QtGui.QMessageBox.question(QtGui.QWidget(),
                                   'Confirm move',
                                   "Do you want to move:\n" + \
                                   ','.join([dn.name for dn in dragNodes]) + \
                                   "\nbelow: " + where + '?!',
                                    'Cancel', 'OK'):
            return
        for dragNode in dragNodes:
            # make an copy of the node being moved 
            old_index = self.index_from_fullname(dragNode.fullname)
            try:
                dragNode.move(parentNode)#newNode.move(parentNode)
            except ValueError:
                QtGui.QMessageBox.question(QtGui.QWidget(),
                                   "Can't move",
                                   "A tag with name " + dragNode.name + "already exists there",
                                    'Cancel')
            else:
                self.beginRemoveRows(old_index.parent(), old_index.row(), row + 1)
                
                node = self.nodeFromIndex(parentIndex)
                #newNode = deepcopy(dragNode) 
            
                self.endRemoveRows()
                self.insertRow(len(parentNode)-1, parentIndex)
            
            
        self.emit(SIGNAL("dataChanged(QModelIndex,QModelIndex)"), parentIndex, parentIndex) 
        return True 


    def insertRow(self, row, parent): 
        return self.insertRows(row, 1, parent) 


    def insertRows(self, row, count, parent):
        self.beginInsertRows(parent, row, (row + (count - 1))) 
        self.endInsertRows() 
        return True 


    def remove_row(self, row, parentIndex):
        return self.remove_rows(row, 1, parentIndex) 


    def remove_rows(self, row, count, parentIndex):
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


        if role == Qt.EditRole:
            #print "returning" + node.name
            node = self.nodeFromIndex(index) 
            return QString(node.name)

        if role != Qt.DisplayRole: 
           return QVariant() 
        
        node = self.nodeFromIndex(index) 
        if index.column() == 0: 
            return QVariant(node.name)# + "(" + str(CurveDB.objects.filter_tag(node.fullname).count()) + ")")



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
        return index.internalPointer() if index.isValid() else self.root

    def refresh(self):
        self.beginRemoveRows(QtCore.QModelIndex(), 0, self.rowCount(QtCore.QModelIndex())) 
        self.root.build_children_from_model()
        self.endRemoveRows()
    
    def child_from_name(self, index, name):
        for count in range(self.rowCount(index)):
            idx = self.index(count, 0, index)
            node = self.nodeFromIndex(idx)
            if node.name == name:
                return idx
                
    def index_from_fullname(self, fullname):
        tag_elements = fullname.split('/')
        idx = QtCore.QModelIndex()
        for name in tag_elements:
            idx = self.child_from_name(idx, name)
        return idx

class TagTreeView(QTreeView):
    value_changed = QtCore.pyqtSignal()
    refresh_requested = QtCore.pyqtSignal()
    def __init__(self, parent=None): 
        super(TagTreeView, self).__init__(parent) 
        self.setMinimumWidth(170)
        self.myModel = TAG_MODEL
        self.setModel(self.myModel) 

        self.setDragEnabled(True) 
        self.setAcceptDrops(True) 
        self.showDropIndicator() 
#        self.setDragDropMode(QAbstractItemView.DragDrop)#InternalMove) 
        self.setSelectionMode(self.ExtendedSelection)

        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._contextMenu)
        #self.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.refresh_requested.connect(self.refresh)

        self.connect(self.model(), SIGNAL("dataChanged(QModelIndex,QModelIndex)"), self.change) 
        
        self.refresh_requested.emit()
        self.expandAll()
    
    

    def get_tags(self):
        return self.get_selected_tags()
    

    def set_tags(self, tags):
        return self._set_tags(tags)
        
    def _set_tags(self, tags):
        self.clearSelection()
        for tag in tags:
            self.select(tag)
            
    def get_selected_tags(self):    
        tags = [self.model().nodeFromIndex(index).fullname \
                for index in self.selectedIndexes()]
        return tags

    def select(self, tag):
        index = self.model().index_from_fullname(tag)
        self.selectionModel().select(index, QtGui.QItemSelectionModel.Select)
        self.repaint()

    def selectionChanged(self, i1, i2):
        super(TagTreeView, self).selectionChanged(i1, i2)
        self.value_changed.emit()

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
            (tag, confirm) = dialog.getText(QtGui.QWidget(),
                                     "new tag",
                                     "enter tag name",
                                     0,
                                     "")
            tag = str(tag)
            if confirm:
                if tag.find("/")>=0:
                    raise ValueError("""tag name should not contain /""")
                if tag=="":
                    raise ValueError("""tag name should not be blank""")
                try:
                    node_clicked.add_child(tag)
                except ValueError:
                    QtGui.QMessageBox.question(QtGui.QWidget(),
                                   "can't add",
                                   "A tag with name " + tag + " already exists there",
                                    'Cancel')
                else:
                    self.model().emit(SIGNAL("dataChanged(QModelIndex,QModelIndex)"), index, index) 
                
                
        def remove_tag(dummy, name=name_clicked):
            confirm = QtGui.QMessageBox.question(QtGui.QWidget(),
                                   "Delete ?",
                                   "Delete tag '" + name + "': are you sure ?\n" + \
                                   "Tag will be removed from all referenced curves...",
                                    'Cancel', 'OK')
            if confirm:
                tag = node_clicked.model_tag()
                self.model().remove_row(index.row(), index.parent())
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
                try:
                    node_clicked.rename(new_name)
                except ValueError:
                    QtGui.QMessageBox.question(QtGui.QWidget(),
                                   "Can't rename",
                                   "A tag with name " + new_name + " already exists there",
                                    'Cancel')
                else:
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



class CurveTagWidget(QtGui.QWidget):
    value_changed = QtCore.pyqtSignal()
    def __init__(self, parent=None):
        super(CurveTagWidget, self).__init__(parent)
        self.tree = TagTreeView()
        self.tree.value_changed.connect(self._update_tag_list)
        
        self.tag_list = QtGui.QTextEdit()
        
        width = self.tag_list.sizeHint().width()
        self.tag_list.setMaximumHeight(30)
        self.tag_list.setEnabled(False)
        
        
        self.lay = QtGui.QVBoxLayout()
        self.lay.addWidget(self.tree)
        self.lay.addWidget(self.tag_list)
    
        self.setLayout(self.lay)
        self.lay.setSpacing(0)
        

        
    def _update_tag_list(self, *args, **kwds):
        string = ""
        for tag in self.tree.get_selected_tags():
            string += """'""" + tag + """' ;"""
        self.tag_list.setText(string)
        self.value_changed.emit()
    

        
    
    def _set_tags(self, tags):
        self.tree.clearSelection()
        for tag in tags:
            self.select(tag)
            
    def get_tags(self):
        return self.tree.get_selected_tags()
    
    def set_tags(self, tags):
        return self.tree.set_tags(tags)
    
TAG_MODEL = TagModel(ROOT)

class DummyNode:
    def __init__(self, name):
        self.name = name

class TagStringModelOld(QtGui.QStringListModel):
    def __init__(self):
        super(TagStringModel, self).__init__() 
        self.refresh_nodes()
        
    def refresh_nodes(self):
        self.nodes = [DummyNode(tag.name) for tag in Tag.objects.all()]
        
    def index(self, row, column, parent):
        return self.createIndex(row, column, self.nodes[row])
    
    def flags(self, index):
        defaultFlags = QAbstractItemModel.flags(self, index) 

        if index.isValid(): 
            return Qt.ItemIsEditable | Qt.ItemIsDragEnabled | Qt.ItemIsDropEnabled | defaultFlags 

        else: 
            return Qt.ItemIsDropEnabled | defaultFlags 

    def data(self, index, role):
        if role == Qt.DecorationRole: 
            return QVariant() 
        if role == Qt.TextAlignmentRole: 
            return QVariant(int(Qt.AlignTop | Qt.AlignLeft))
        if role == Qt.EditRole:
            return QString(index.internalPointer().name)
        if role != Qt.DisplayRole: 
           return QVariant()
        if index.column() == 0: 
            return QVariant(index.internalPointer().name)
        
    def columnCount(self, parent): 
        return 1

    def rowCount(self, parent):
        self.refresh_nodes()
        return len(self.nodes)
"""
class TagStringModel(QtGui.QStringListModel):
    def __init__(self):
        super(TagStringModel, self).__init__() 
        self.refresh_nodes()
        
    def refresh_nodes(self):
        self.setStringList([tag.name for tag in Tag.objects.all()])

TAG_STRING_MODEL = TAG_MODEL#TagStringModel()#QtGui.QStringListModel([tag.name for tag in Tag.objects.all()])"""