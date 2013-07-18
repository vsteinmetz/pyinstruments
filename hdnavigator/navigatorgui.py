"Make.today_dir""""This module provides a Graphical user interface for the HDnavigator"""
from navigator import Navigator
from guiwrappersutils import GuiWrapper,GuiWrapperWidget
from PyQt4 import QtGui,QtCore

class ToolTiper(object):
    def __init__(self,parent_widget):
        self.parent = parent_widget
        
    def make_tooltips(self):
        widget = self.parent
        if widget.driver.Next.dir == None:
            message = "this would bring you out of the root_path !"
        else:
            message = "Create \"" + widget.driver.Next.dir + "\" !"
        widget._gui_elements["Make.dir"].setToolTip(message)
        widget._gui_elements["Make.sub_dir"].setToolTip("Create \"" + widget.driver.Next.sub_dir + "\" !")
        widget._gui_elements["Make.today_dir"].setToolTip("Create \"" + widget.driver.Next.today_dir + "\" !")

class NavigatorGui(Navigator, GuiWrapper):
    def __init__(self):
        super(NavigatorGui,self).__init__()
        GuiWrapper.__init__(self)
        
    def _setupUi(self,widget):
        widget._setup_horizontal_layout()
        widget._setup_vertical_layout()
        widget._setup_gui_element("Default.root_path")
        widget._setup_gui_element("Default.dir")
        widget._setup_gui_element("Default.file")
        widget._exit_layout()
        widget._setup_vertical_layout()
        widget._setup_gui_element("Go.root_path")
        widget._setup_gui_element("Go.up")
        widget._setup_gui_element("Go.down")
        widget._setup_gui_element("Go.last_below")
        widget._exit_layout()
        widget._exit_layout()
        widget._setup_gui_element("Current.dir")
        widget._setup_horizontal_layout()
        widget._setup_gui_element("Make.dir")
        widget._setup_gui_element("Make.sub_dir")
        widget._setup_gui_element("Make.today_dir")
        widget._exit_layout()
        widget._setup_gui_element("next_file")
        
        widget.toolTiper = ToolTiper(widget)
        
        
        #widget.__class__.make_tooltips = make_tooltips
        self.value_changed.connect(widget.toolTiper.make_tooltips)
        
        
#    
        
   # def sizeHint(self):
   #     return QtCore.QSize(500,super(GuiWrapperWidget,self.gui_widget).sizeHint().height())
        
        
nav = NavigatorGui()        