from PyQt4 import QtGui, QtCore
from curvefinder.models import Tag, Curve

class ToolTiper(object):
    def __init__(self,parent_widget):
        self.parent = parent_widget
        
    def make_tooltips(self):
        widget = self.parent
        if widget.driver.Next.dir == None:
            message = "this would bring you out of the root_path !"
        else:
            message = "Create \"" + widget.driver.Next.dir + "\" !"


class CurveSelectWidget(QtGui.QWidget, object):
    pass

class CurveCommentWidget(QtGui.QWidget, object):
    def __init__(self):
        super(CurveCommentWidget, self).__init__()
        self.setup_ui()
        
    def setup_ui(self):
        """sets up the GUI"""
        
        self.label = QtGui.QLabel("comment")
        self.comment_box = QtGui.QTextEdit()
        self.lay = QtGui.QVBoxLayout()
        self.lay.addWidget(self.label)
        self.lay.addWidget(self.comment_box)
        self.setLayout(self.lay)
        
    @property
    def comment(self):
        return str(self.comment_box.toPlainText())
    
    @comment.setter
    def comment(self, comment):
        return self.comment_box.setText(comment)
        
class CurveCreateWidget(QtGui.QWidget, object):
    """combines a CurveTagWidget, CurveCommentWidget, a name and window 
    input fields
    """
    
    def __init__(self, default_name = "some_curve", \
                 default_window = "default", \
                 comment = "", \
                 tags = [], parent = None):
        super(CurveCreateWidget, self).__init__(parent)
        self.setup_ui()
        self.name = default_name
        self.window = default_window
        self.comment = comment
        self.tags = tags
        self.save_button.pressed.connect(self.save_pressed)
    
    save_pressed = QtCore.pyqtSignal(name = 'save_pressed')
    
    @property
    def tags(self):
        return self.curve_tag_widget.tags
    
    @tags.setter
    def tags(self, tags):
        self.curve_tag_widget.tags = tags
        return tags
    
    @property
    def comment(self):
        return self.curve_comment_widget.comment
    
    @comment.setter
    def comment(self, comment):
        self.curve_comment_widget.comment = comment
        return comment
    
    @property
    def name(self):
        return str(self.name_widget.text())
    
    @name.setter
    def name(self, name):
        self.name_widget.setText(name)
        return name
    
    @property
    def window(self):
        return str(self.window_widget.text())
    
    @window.setter
    def window(self, window):
        self.window_widget.setText(window)
        return window
    
    def setup_ui(self):
        """sets up the GUI"""
        
        self.h_lay1 = QtGui.QHBoxLayout()
        self.name_label = QtGui.QLabel("name")
        
        self.name_widget = QtGui.QLineEdit("some_curve")
        
        self.h_lay1.addWidget(self.name_label)
        self.h_lay1.addWidget(self.name_widget)
        self.window_widget = QtGui.QLineEdit("default")
        self.window_label = QtGui.QLabel("plot window")
        self.h_lay1.addWidget(self.window_label)
        self.h_lay1.addWidget(self.window_widget)
        
        self.h_lay2 = QtGui.QHBoxLayout()
        self.curve_tag_widget = CurveTagWidget()
        self.curve_comment_widget = CurveCommentWidget()
        self.h_lay2.addWidget(self.curve_tag_widget)
        self.h_lay2.addWidget(self.curve_comment_widget)
        self.save_button = QtGui.QPushButton("save")
        self.h_lay2.addWidget(self.save_button)
        
        
        self.v_lay = QtGui.QVBoxLayout()
        
        self.v_lay.addLayout(self.h_lay1)
        self.v_lay.addLayout(self.h_lay2)
        self.setLayout(self.v_lay)
        
    def dump_in_gui(self, curve):
        self.comment = curve.comment
        self.name = curve.name
        self.window = curve.window_txt
        self.tags = curve.tags_txt
        
    def save_curve(self, curve):
        curve.comment = self.comment
        curve.name = self.name
        curve.window_txt = self.window
        curve.tags_txt = self.tags
        curve.save()
    
    def hide_save_button(self):
        self.save_button.hide()
        
class CurveTagWidget(QtGui.QWidget, object):
    def __init__(self, parent = None):
        super(CurveTagWidget, self).__init__(parent)
        self._setup_ui()
        self.tree_widget.itemSelectionChanged.connect(self._update_tag_list)
        self._update_tag_list()
    
    value_changed = QtCore.pyqtSignal(name = "value_changed")
    
    @property
    def tags(self):
        return self.get_selected_tags()
    
    @tags.setter
    def tags(self, tags):
        return self._set_tags(tags)
        
    def get_selected_tags(self):    
        tags = [self._get_tag_from_item(item) \
                for item in self.tree_widget.selectedItems()]
        return tags
        
    def _update_tag_list(self, *args, **kwds):
        string = ""
        for tag in self.get_selected_tags():
            string += """'""" + tag + """' ;"""
        self.tag_list.setText(string)
        self.value_changed.emit()
        
    def _setup_ui(self):
        """sets up the GUI"""
        
        self.tag_list = QtGui.QTextEdit()
        width = self.tag_list.sizeHint().width()
        self.tag_list.setMaximumHeight(30)
        self.tag_list.setEnabled(False)
        
        self.tree_widget = QtGui.QTreeWidget()
        self.tree_widget.setColumnCount(1)
        self.tree_widget.setGeometry(QtCore.QRect(0, 0, 401, 400))
        self.tree_widget.setIndentation(20)
        self.tree_widget.setObjectName("tree_widget")
        self.tree_widget.setSelectionMode( \
                            QtGui.QAbstractItemView.ExtendedSelection)
        
        self.lay = QtGui.QVBoxLayout()
        self.lay.addWidget(self.tree_widget)
        self.lay.addWidget(self.tag_list)
        
        self.tree_widget.headerItem().setText(0, \
                                      QtGui.QApplication.translate( \
                                                        "MainWindow", \
                                                        "tags", \
                                                        None, \
                                                        QtGui.QApplication.\
                                                        UnicodeUTF8))
        
        self.tree_widget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.tree_widget.customContextMenuRequested.connect(self._contextMenu)
        
        self.setLayout(self.lay)
        self.lay.setSpacing(0)
        self.refresh()
    
    def _remove_all_items(self):
        """removes all items from the Tree but keeps the column structure"""
        
        for index in range(self.tree_widget.topLevelItemCount()):
            ite = self.tree_widget.takeTopLevelItem(0)
            del ite
     
    def _get_or_add_top_level(self, name):
        for index in range(self.tree_widget.topLevelItemCount()):
            item = self.tree_widget.topLevelItem(index)
            if str(item.text(0)) == name:
                return item
        item = QtGui.QTreeWidgetItem([name])
        self.tree_widget.addTopLevelItem(item)
        return item
        
    def _get_or_add_child(self, item, name):
        child = self._get_child(item, name)
        if child:
            return child
        child = QtGui.QTreeWidgetItem([name])
        item.addChild(child)
        return child
    
    def refresh(self):
        self._remove_all_items()
        tags = Tag.objects.all()
        for tag in tags:
            self.add_item(tag.name)
    
    def _set_tags(self, tags):
        self.tree_widget.clearSelection()
        for tag in tags:
            self.select(tag)
    
    def set_for_curve(self, curve):
        """
        taking a curve from the datamodel, will select the current tags
        """
        for index in range(self.tree_widget.topLevelItemCount()):
            item = self.tree_widget.topLevelItem(index)
            item.setSelected(False)
        for tag in curve.tags.all():
            self.select(tag)
            
    def _get_child(self, item, name):
        for index in range(item.childCount()):
            child = item.child(index)
            if child.text(0) == name:
                return child
    
    def select(self, tag):
        tag_elements = tag.split('/')
        child = None
        for index in range(self.tree_widget.topLevelItemCount()):
            item = self.tree_widget.topLevelItem(index)
            if item.text(0) == tag_elements[0]:
                child = item
                for tag_element in tag_elements[1:]:
                    child = self._get_child(child, tag_element)
                    if not child:
                        return
        if child:
            child.setSelected(True)
  
    def _exec_menu_at_right_place(self, menu, point):
        p = QtCore.QPoint(point)
        p.setY(p.y() + menu.height())
        where = self.mapToGlobal(p)
        menu.exec_(where)           
    
    def add_item(self, name):
        tag_elements = name.split('/')
        child = self._get_or_add_top_level(tag_elements[0])
            
        for tag_element in tag_elements[1:]:
            child = self._get_or_add_child(child, tag_element)  
    
    def _get_tag_from_item(self, item):
        parent = item
        parent_names = []
        while parent:
            parent_names.append(str(parent.text(0)))
            parent = parent.parent()
        parent_names.reverse()
        name_clicked = ""
        for string in parent_names:
            if name_clicked != "":
                name_clicked += '/'
            name_clicked += string
        return name_clicked
    
    def _contextMenu(self, point):
        """
        Context Menu (right click on the treeWidget)
        """
        
        item = self.tree_widget.itemAt(point)
        name_clicked = self._get_tag_from_item(item)
        
        
        def add_tag():
            dialog = QtGui.QInputDialog()
            dialog.setTextValue(name_clicked)
            if name_clicked != "":
                proposition = name_clicked + '/'
            else:
                proposition = name_clicked
            (tag, confirm) = dialog.getText(QtGui.QWidget(), \
                                     "new tag", \
                                     "enter tag name", \
                                     0, \
                                     proposition)
            tag = str(tag)
            if tag.endswith("/"):
                raise ValueError("""tag should not end with /""")
            if confirm and tag != "":
                try:
                    Tag.objects.get(name = tag)
                except Tag.DoesNotExist:
                    Tag.objects.create(name = tag)
                    self.add_item(tag)
                    print tag
                    self.select(tag)
                else:
                    box = QtGui.QMessageBox()
                    box.setText("tag " + tag + " allready exists")
                    box.exec_()

        menu = QtGui.QMenu(self)
        action_add_tag = QtGui.QAction("add tag...", self)
        action_add_tag.triggered.connect(add_tag)
        menu.addAction(action_add_tag)
        self._exec_menu_at_right_place(menu, point)