from PyQt4 import QtCore,QtGui
from PyQt4.QtGui import QVBoxLayout
import os

def graphical_exception(func):
    """a wrapper to display the exception in a pop up window rather than 
    lost in the console"""
    def new_func(*args,**kwds):
        try:
            return func(*args,**kwds)
        except BaseException as e:
            m = QtGui.QMessageBox()
            m.setText(str(e))
            m.exec_()
    return new_func

class GuiWrapperWidget(QtGui.QWidget):
    def __init__(self, driver, parent=None):
        self.driver = driver
        self._gui_elements = dict()
        self._callable_elements = []
        self._tab_widgets = []
        self._tab_widget_items = []
        
        super(GuiWrapperWidget,self).__init__(parent)
        self.lay = QtGui.QVBoxLayout()
        
        self.current_layout = self.lay
        self.setLayout(self.current_layout) 
        
    ##===============================================
    ##  Values updates
    ##===============================================
    def set_values_in_gui(self):
        for k,v in self._gui_elements.iteritems():
            v.value = self.driver._get_recursing_attribute(k)[-1] 
    
    @graphical_exception
    def get_values_from_gui(self,item_name_changed = None):
        item_name_changed = str(item_name_changed)
        if item_name_changed is not None:
            self.driver._set_recursing_attribute(item_name_changed, self._gui_elements[item_name_changed].value)
        else:
            for k,v in self._gui_elements.iteritems():
                self.driver._set_recursing_attribute(k, v.value)
                v.value = self.driver._get_recursing_attribute(k)[-1]
        #self.gui_widget.blockSignals(True)
        #self.set_values_in_gui()
        #self.gui_widget.blockSignals(False)
        self.driver.value_changed.emit()
    
    ##=======================================
    ## gui construction utilities
    ##=======================================
    def _setup_tabs_for_collection(self, collection_name, \
                                   n_max = 5):
        """
        creates a QTabWidget in the widget with the elements found in the 
        collection self.driver.collection_name. Truncates the number of 
        elements at n_max.
        """
        
        self._tab_widgets.append(QtGui.QTabWidget())
        self.add_below(self._tab_widgets[-1])
        n = 0
        for name,item in self.driver.__getattr__(collection_name).iteritems():
            n+=1
            if n>n_max:
                break
            self._tab_widget_items.append(item._create_widget())
            self._tab_widgets[-1].addTab(self._tab_widget_items[-1], name)
    
    def _setup_horizontal_layout(self):
        self.setup_layout(QtGui.QHBoxLayout())
        
    def _setup_vertical_layout(self):
        self.setup_layout(QtGui.QVBoxLayout())
        
    def _exit_layout(self):
        self.parent_layout()
    
    def _setup_gui_element(self, property_name, enum=None):
        """sets up for you a graphical element by checking the type of 
        self.property_name. Will make a ComboBox if you provide a list
        enum. i.e: enum = [(0,"AC"),(1,"DC"),(2,"GND")}
        in case there is a point in the property_name, will look into 
        the attribute (e.g. property_name = "Average.NumberOfSweeps").
        """
        
        try:
            obj,attr_name,val = self.driver._get_recursing_attribute(property_name)
        except AttributeError:
            print "Attribute " + property_name + " was not found in the driver. The corresponding element will be dropped from the GUI"
            return
        
        if enum:
            obj = EnumItem(property_name, enum)
            self.add_below(obj)
            self._gui_elements[property_name] = obj
            obj.value_changed.connect(self.get_values_from_gui)
            return
        
        if isinstance(val,basestring):
            obj = StringItem(property_name)
            self.add_below(obj)
            self._gui_elements[property_name] = obj
            obj.value_changed.connect(self.get_values_from_gui)
             
        if isinstance(val,float):
            obj = DoubleItem(property_name)
            self.add_below(obj)
            self._gui_elements[property_name] = obj
            obj.value_changed.connect(self.get_values_from_gui)
            return
        
        if isinstance(val,bool):
            obj = BoolItem(property_name)
            self.add_below(obj)
            self._gui_elements[property_name] = obj
            obj.value_changed.connect(self.get_values_from_gui)
            return
            
        if isinstance(val,int):
            obj = IntItem(property_name)
            self.add_below(obj)
            self._gui_elements[property_name] = obj
            obj.value_changed.connect(self.get_values_from_gui)
            return    
            
        if callable(val):
            obj = ButtonItem(property_name)
            self.add_below(obj)
            self._gui_elements[property_name] = obj
            new_func = graphical_exception(val)
            self._callable_elements.append(new_func)
            obj.pressed.connect(graphical_exception(new_func))
#            obj.value_changed.connect(self.get_values_from_gui)

    
    
    ##=======================================
    ##   Layout manipulations
    ##=======================================
    @property
    def current_layout(self):
        return self._current_layout
        
    @current_layout.setter
    def current_layout(self, val):
        self._current_layout = val
        return val
    
    def setup_layout(self, layout):
        """layout is added to current layout and becomes the current layout"""
        layout.parent = self.current_layout
        self.current_layout.child_layout = layout
        self.current_layout.addLayout(layout)
        self.current_layout = layout
        
    def parent_layout(self):
        self.current_layout = self.current_layout.parent
        
    def add_below(self, widget):
        self.current_layout.addWidget(widget)
        
    def sizeHint(self):
        size = super(GuiWrapperWidget,self).sizeHint()
        if hasattr(self.driver, "_width_hint"):
            size.setWidth(self.driver._width_hint)
        if hasattr(self.driver, "_height_hint"):
            size.setHeight(self.driver._height_hint)
        return size

class GuiItem(QtGui.QWidget):
    def __init__(self,label,hide_label = False):
        super(GuiItem,self).__init__()
        self.label = label
        self._lay = QtGui.QHBoxLayout()
        self.setLayout(self._lay)
        if not hide_label:
            self._lay.addWidget(QtGui.QLabel(label))
        
    value_changed = QtCore.pyqtSignal(str)
    
    def emit(self):
        self.value_changed.emit(self.label)
        
class MyDoubleSpinBox(QtGui.QDoubleSpinBox):        
    def __init__(self):
        super(MyDoubleSpinBox,self).__init__()
        self.installEventFilter(self)
        
    
    def eventFilter(self,obj,event): ###see http://www.qtforum.org/article/22813/signal-and-qdoublespinbox-qspinbox.html
        if event.type() in [QtCore.QEvent.MouseButtonRelease,QtCore.QEvent.MouseButtonDblClick]:
            if (not self.lineEdit().rect().contains(event.pos())):
                self.editingFinished.emit()
        #if event.type() == QtCore.QEvent.KeyPress:
        #    if((event.key() == QtCore.Qt.Key_Return) or (event.key() == QtCore.Qt.Key_Enter)):
        #        self.sig_value_changed.emit()
        return super(MyDoubleSpinBox,self).eventFilter(obj,event)
#       return super(DoubleItem,self).eventFilter(obj,event)

class MySpinBox(QtGui.QSpinBox):        
    def __init__(self):
        super(MySpinBox,self).__init__()
        self.installEventFilter(self)
        
    
    def eventFilter(self,obj,event): ###see http://www.qtforum.org/article/22813/signal-and-qdoublespinbox-qspinbox.html
        if event.type() in [QtCore.QEvent.MouseButtonRelease,QtCore.QEvent.MouseButtonDblClick]:
            if (not self.lineEdit().rect().contains(event.pos())):
                self.editingFinished.emit()
        #if event.type() == QtCore.QEvent.KeyPress:
        #    if((event.key() == QtCore.Qt.Key_Return) or (event.key() == QtCore.Qt.Key_Enter)):
        #        self.sig_value_changed.emit()
        return super(MySpinBox,self).eventFilter(obj,event)
#       return super(DoubleItem,self).eventFilter(obj,event)

class DoubleItem(GuiItem):
    def __init__(self,label):
        super(DoubleItem,self).__init__(label)
        self._item = MyDoubleSpinBox()
        self._item.setMaximum(1e12)
        self._item.setMinimum(-1e12)
        self._lay.addWidget(self._item)
        self._item.editingFinished.connect(self.emit)

    @property
    def value(self):
        return self._item.value()
    
    @value.setter
    def value(self,val):
        self._item.setValue(val)
        
class IntItem(GuiItem):
    def __init__(self,label):
        super(IntItem,self).__init__(label)
        self._item = MySpinBox()
        self._item.setMaximum(int(2e9))
        self._item.setMinimum(int(-2e9))
        self._lay.addWidget(self._item)
        self._item.editingFinished.connect(self.emit)

    @property
    def value(self):
        return self._item.value()
    
    @value.setter
    def value(self,val):
        self._item.setValue(val)
        
class BoolItem(GuiItem):
    def __init__(self,label):
        super(BoolItem,self).__init__(label)
        self._item = QtGui.QCheckBox()
        self._lay.addWidget(self._item)
        self._item.stateChanged.connect(self.emit)

    @property
    def value(self):
        return self._item.checkState() != 0
    
    @value.setter
    def value(self,val):
        self._item.setChecked(val)
        return val
    
class EnumItem(GuiItem):
    def __init__(self, label, enum):
        super(EnumItem, self).__init__(label)
        self._item = QtGui.QComboBox()
        for number, string in enumerate(enum):
            self._item.addItem(string, number)
        self._lay.addWidget(self._item)
        self._item.currentIndexChanged.connect(self.emit)
        self.choices = enum
        self.choices_num = dict()
        for index, val in enumerate(self.choices):
            self.choices_num[index] = index

    @property
    def value(self):
        return self._item.itemData(self._item.currentIndex()).toInt()[0]
    
    @value.setter
    def value(self,val):
        self._item.setCurrentIndex(self.choices_num[val])
        return val
        
class StringItem(GuiItem):
    def __init__(self,label,**kwds):
        super(StringItem,self).__init__(label)
        self._item = QtGui.QLineEdit()
        self._lay.addWidget(self._item)
        self._item.editingFinished.connect(self.emit)

    @property
    def value(self):
        return str(self._item.text())
    
    @value.setter
    def value(self,val):
        self._item.setText(val)
        return val 

class ButtonItem(GuiItem):
    def __init__(self,label,**kwds):
        super(ButtonItem,self).__init__(label,hide_label = True)
        self._item = QtGui.QPushButton(label)
        self._lay.addWidget(self._item)
        self._item.pressed.connect(self.emit)


    pressed = QtCore.pyqtSignal()
    def emit(self):
        self.pressed.emit()
        self.value_changed.emit(self.label)
    @property
    def value(self):
        return 0
    
    @value.setter
    def value(self,val):
        return val 
                

class Emitter(QtCore.QObject):
    def __init__(self):
        super(Emitter,self).__init__()
    
    value_changed = QtCore.pyqtSignal()

class GuiWrapper(object):
    """basic class to handle GUI capabilities of the wrapper"""
    
    _gui_icon_file = "iconeScope.gif"
    def __init__(self,gui_title = "gui"):
        super(GuiWrapper,self).__init__()
        self._emitter = Emitter()
        self._gui_title = gui_title
        self._widget = None
    
    def set_width_hint(self, width):
        self._width_hint = width
    
    def set_height_hint(self, height):
        self._height_hint = height
    
    def __getattr__(self,attr):
        return self.__getattribute__(attr)
       
    def widget(self, parent=None):
        if self._widget:
            return self._widget
        widget = GuiWrapperWidget(self, parent)
        self._setupUi(widget)    
        widget.resize(widget.sizeHint())
        self.value_changed.connect(widget.set_values_in_gui)
        self.value_changed.emit()
        self._widget = widget
        return widget
    
    def _set_gui_title(self,title):
        self._gui_title = title  
        
    def gui(self):
        widget = self._create_widget()
        widget.show()
        return widget
   # def sizeHint(self):
   #     return super(GuiWrapperWidget,self.gui_widget).sizeHint()
    
    @property
    def value_changed(self):
        return self._emitter.value_changed
        
    def _setupUi(self,widget):
        """to be overwriten in the child class, should define the look of the widget"""
        pass
    
    
        
    def _get_recursing_attribute(self,attr):
        """gets an attribute recursively as in self.sub.attr"""
        pn = attr.split(".")
        obj2 = self
        for attr_name in pn:
            obj = obj2
            try:
                val = obj.__getattr__(attr_name)
            except AttributeError:
                val = obj.__getattribute__(attr_name)
            obj2 = val
        return (obj,attr_name,val)
    
    def _set_recursing_attribute(self,attr,val):
        obj,attr_name,attr_val = self._get_recursing_attribute(attr)
        try:
            obj.__setattr__(attr_name,val)
        except AttributeError:
            pass
        except TypeError:
            pass
    
        
        
#        QtCore.QObject.connect(self.actionQueryModels, QtCore.SIGNAL('triggered()'), self.query_models)
        