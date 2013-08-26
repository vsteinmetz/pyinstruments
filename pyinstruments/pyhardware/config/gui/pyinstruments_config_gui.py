"""
This module is here to allow GUI interaction with the config file
"""

from pyinstruments.pyhardware.config.gui.pytreewidget import PyTreeWidget
from pyinstruments.pyhardware.config.pyinstruments_config import PyInstrumentsConfig
import pyinstruments.pyhardware.config.connected_instruments as con
#from pyinstruments.pyhardware.factories import driver_factory, instrument_factory
#from pyinstruments.pyhardware.factories.factories_utils import \
 #                                       list_all_child_classes
from pyinstruments.pyhardware.drivers import Driver
from pyinstruments.pyhardware.drivers.ivi import IviDriver
from pyinstruments.pyhardware.drivers import VisaDriver, SerialDriver
from pyinstruments.pyhardware import instrument
from pyinstruments.utils.class_utils import list_all_child_classes
from pyivi import software_modules
#from pyinstruments.pyhardware.drivers.ivi_interop.ividotnet.config_store_utils \
#                                    import CONFIG_STORE
                                            
from PyQt4 import QtCore, QtGui
import os

class CentralWidgetInstruments(QtGui.QWidget):
    def __init__(self, parent = None):
        super(CentralWidgetInstruments, self).__init__(parent)
        self.lay = QtGui.QHBoxLayout()
        self.setLayout(self.lay)


class PyInstrumentsWindow(QtGui.QMainWindow):
    def __init__(self, parent = None):
        """
        creates the window and associates it with the config object
        """
        
        super(PyInstrumentsWindow, self).__init__(parent)
        self.menubar = QtGui.QMenuBar(self)
        #self.menubar.setGeometry(QtCore.QRect(0, 0, 401, 21))
        self.menubar.setObjectName("menubar")
        
        self.menu_action = QtGui.QAction(self)
        self.menuFile = QtGui.QMenu(self.menubar)
        self.menu_action.setMenu(self.menuFile)
#        self.menuFile.setObjectName("menuFile")
        self.setMenuBar(self.menubar)
        self.menubar.addAction(self.menu_action)
        self.statusbar = QtGui.QStatusBar(self)
        self.statusbar.setObjectName("statusbar")
        self.setStatusBar(self.statusbar)
        self.actionRefresh = QtGui.QAction(self)
        self.actionRefresh.setObjectName("actionRefresh")
        self.actionRemoveAll = QtGui.QAction(self)
        self.actionRemoveAll.setObjectName("actionRemoveAll")
        
        self.actionQueryModels = QtGui.QAction(self)
        self.actionQueryModels.setObjectName("actionQueryModels")
        self.menuFile.addAction(self.actionQueryModels)
        
        self.actionAutoDetect = QtGui.QAction(self)
        self.actionAutoDetect.setObjectName("actionAutoDetect")
        self.menuFile.addAction(self.actionAutoDetect)
        
        self.actionHelp = QtGui.QAction(self)
        self.actionHelp.setObjectName("actionHelp")
        self.menuFile.addAction(self.actionRefresh)
        self.menuFile.addAction(self.actionRemoveAll)
        self.menubar.addAction(self.menuFile.menuAction())
        self.retranslateUi(self)
        QtCore.QMetaObject.connectSlotsByName(self)
        
        self.dev_list = PyInstrumentsConfigGui(self)
          
        self.setWindowIcon(\
                        QtGui.QIcon(os.path.split(__file__)[0] +"/usb.png"))
        
        QtCore.QObject.connect(self.actionRefresh, \
                               QtCore.SIGNAL('triggered()'), \
                               self.dev_list.refresh)
        QtCore.QObject.connect(self.actionAutoDetect, \
                               QtCore.SIGNAL('triggered()'), \
                               self.dev_list.auto_detect)
        QtCore.QObject.connect(self.actionRemoveAll, \
                               QtCore.SIGNAL('triggered()'), \
                               self.dev_list.remove_all)
        QtCore.QObject.connect(self.actionQueryModels, \
                               QtCore.SIGNAL('triggered()'), \
                               self.dev_list.query_models)

        self.central = CentralWidgetInstruments(self)
        self.setCentralWidget(self.central)
        
        
        
        self.addDockWidget(\
                QtCore.Qt.DockWidgetArea(QtCore.Qt.LeftDockWidgetArea),
                self.dev_list)
        
        self.statusbar.showMessage('running...')
        
    
    def sizeHint(self):
        return QtCore.QSize(900, 900)    
    
    def retranslateUi(self, MainWindow):
        """qt's stuffs..."""
        MainWindow.setWindowTitle(QtGui.QApplication.translate("MainWindow", \
                                            "pyinstruments GUI", \
                                             None, \
                                             QtGui.QApplication.UnicodeUTF8))
        self.menuFile.setTitle(QtGui.QApplication.translate( \
                                            "MainWindow", \
                                            "file", \
                                            None, \
                                            QtGui.QApplication.UnicodeUTF8))
        self.actionRefresh.setText( \
                                QtGui.QApplication.translate( \
                                    "MainWindow", \
                                    "Refresh", \
                                    None, \
                                    QtGui.QApplication.UnicodeUTF8)\
                                )
        self.actionRemoveAll.setText( \
                QtGui.QApplication.translate( \
                                "MainWindow", \
                                "remove all", \
                                None, \
                                QtGui.QApplication.UnicodeUTF8) \
                                    )
        self.actionAutoDetect.setText( \
                            QtGui.QApplication.translate( \
                                            "MainWindow", \
                                            "auto detect new hardware!", \
                                            None, \
                                            QtGui.QApplication.UnicodeUTF8) \
                                      )
        self.actionHelp.setText( \
                    QtGui.QApplication.translate( \
                                        "MainWindow", \
                                        "help...", \
                                        None, \
                                        QtGui.QApplication.UnicodeUTF8) \
                                )
        self.actionQueryModels.setText( \
                        QtGui.QApplication.translate( \
                                            "MainWindow", \
                                            "query models", \
                                            None, \
                                            QtGui.QApplication.UnicodeUTF8) \
                                       )

class PyInstrumentsConfigGui(QtGui.QDockWidget):
    """
    Main gui class
    """
    
    def __init__(self, parent=None):
        """
        creates the window and associates it with the config object
        """
        
        super(PyInstrumentsConfigGui, self).__init__(parent)
        self.setupUi(self)
        self._instruments = []#dict()
        self.show()
        #self.loaded_drivers = dict()

        self.tree_widget.itemChanged.connect(self.item_changed) 
        self.tree_widget.setColumnWidth(0, 119)
        self.tree_widget.setColumnWidth(1, 119)
        self.tree_widget.setColumnWidth(2, 119)
        self.tree_widget.setColumnWidth(3, 40)
        self.tree_widget.setColumnWidth(4, 50)
        self.tree_widget.setColumnWidth(5, 50)
        self.refresh()
       
        self.tree_widget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.tree_widget.customContextMenuRequested.connect(self.contextMenu)
        self.tree_widget.button_pressed.connect(self.gui_pressed)
        
        
    def gui_pressed(self, widget_item):
        instr = instrument(widget_item.val('logical_name'))
        widget = instr.widget(parent=self)
        self.parent().central.lay.addWidget(widget)
        widget.show()
        self._instruments.append(instr)
        
    def setupUi(self, MainWindow):
        """sets up the GUI"""
        
        self.tree_widget = PyTreeWidget([("logical_name", "string"),
                                        ("address", "string"),
                                        ("model", "string"),
                                        ("simulate", "bool"),
                                        ("code", "text"),
                                        ("gui", "button")])
        #self.tree_widget.setGeometry(QtCore.QRect(0, 0, 401, 400))
        #self.tree_widget.setIndentation(20)
        self.tree_widget.setObjectName("tree_widget")
        #self.tree_widget.header().setDefaultSectionSize(500)
        
        self.setWidget(self.tree_widget)
        
    
        
    
    def _refresh(self, full = False):
        """
        refreshes the gui, if full, sets also the color of the address field
        """
        
        pic = PyInstrumentsConfig()
        self.tree_widget.blockSignals(True)
        self.tree_widget.remove_all_items()
        for tag, instr in pic.iteritems():
            widgetItem = self.tree_widget.add_item("",
                                                  "",
                                                  "",
                                                  "",
                                                  "",
                                                  "")
            try:
                widgetItem.set_values(tag, \
                                  instr["address"],
                                  instr["model"],
                                  instr["simulate"],
                                  instr["code"])
            except KeyError as e:
                print "error"
                print e
            if(instr["model"] in Driver.supported_models()):
                widgetItem.set_color(2, "green")
            else:
                widgetItem.set_color(2, "red")
            
            
            if(instr["address"] in con.existing_addresses(full)):
                widgetItem.set_color(1, "green")
            else:
                widgetItem.set_color(1, "red")
                    
        self.tree_widget.blockSignals(False) 
    
    def refresh(self):
        """
        refreshes the gui, including the color of the address field
        """
        
        self._refresh(full = True)     
    
    def fast_refresh(self):
        """
        refreshes the gui except for the color of the address field
        """
        
        self._refresh(full = False)

    def exec_menu_at_right_place(self, menu, point):
        p = QtCore.QPoint(point)
        p.setY(p.y() + menu.height())
        where = self.mapToGlobal(p)
        menu.exec_(where)     
        
    def contextMenuAdresses(self, point):     
        """
        context menu when address column right-clicked
        """
        
        def change_address(new_address):
            pic = PyInstrumentsConfig()
            itm = self.tree_widget.itemAt(point)
            pic[itm.val("logical_name")]["address"] =  new_address
            pic.save()
            self.refresh()
        
        class ChangeAddress(QtGui.QAction):
            def change_address_to_mine(self):
                change_address(str(self.text()))
        
            
        menu = QtGui.QMenu(self)
        addresses = con.existing_addresses(recheck = True)
        action_addresses = []
        for address in addresses:
            action = ChangeAddress(address, self)
            action_addresses.append(action)
            action.triggered.connect(action.change_address_to_mine)
            menu.addAction(action)
        

        self.exec_menu_at_right_place(menu, point)


   
        
    def contextMenuModels(self, point):
        """
        context menu when models column right-clicked
        """
        
        def change_model(new_model):
            pic = PyInstrumentsConfig()
            itm = self.tree_widget.itemAt(point)
            pic[itm.val("logical_name")]["model"] =  new_model
            pic.save()
            self.refresh()
        
        class ChangeModel(QtGui.QAction):
            def change_model_to_mine(self):
                change_model(str(self.text()))
        
        def add_model_in_menu(menu, model):
            model_action = ChangeModel(model, self)
            model_actions.append(model_action)
            model_action.triggered.connect( \
                            model_action.change_model_to_mine)
            menu.addAction(model_action)
        
        menu = QtGui.QMenu(self)
        ivi_menu = QtGui.QMenu("ivi", self)
        menu.addMenu(ivi_menu)
        ivi_drivers = list_all_child_classes(IviDriver)
        ivi_types_menu = []
        soft_modules = []
        modules_menu = []
        model_actions = []
        for driver in ivi_drivers.values():
            type_menu = QtGui.QMenu(driver.__name__)
            ivi_types_menu.append(type_menu)
            ivi_menu.addMenu(type_menu)
            for module in driver.supported_software_modules():
                #if module in map(lambda x: x.name, CONFIG_STORE):
                    soft_modules.append(module)
                    module_menu = QtGui.QMenu(module)
                    modules_menu.append(module_menu)
                    type_menu.addMenu(module_menu)
                    for model in software_modules[module].supported_instrument_models():
                        add_model_in_menu(module_menu, model)
                        
        
        serial_menu = QtGui.QMenu("serial", self)         
        menu.addMenu(serial_menu)          
        
        serial_drivers = list_all_child_classes(SerialDriver)
        serial_drivers_menu = []
        for driver in serial_drivers.values():
            driver_menu = QtGui.QMenu(driver.__name__)
            serial_drivers_menu.append(driver_menu)
            serial_menu.addMenu(driver_menu)
            for model in driver.supported_models():
                add_model_in_menu(driver_menu, model)
                
        visa_menu = QtGui.QMenu("visa", self)         
        menu.addMenu(visa_menu)          
        
        visa_drivers = list_all_child_classes(VisaDriver)
        visa_drivers_menu = []
        for driver in visa_drivers.values():
            driver_menu = QtGui.QMenu(driver.__name__)
            visa_drivers_menu.append(driver_menu)
            visa_menu.addMenu(driver_menu)
            for model in driver.supported_models():
                add_model_in_menu(driver_menu, model)
                
#        visa_drivers = list_all_child_classes(VisaDriver)
#        for driver in visa_driver.values():
#            driver_menu = QtGui.QMenu(driver.__name__)
#            model_action = ChangeModel(model, self)
#            model_actions.append(model_action)
#            model_action.triggered.connect( \
#                            model_action.change_model_to_mine)
#            module_menu.addAction(model_action)
        self.exec_menu_at_right_place(menu, point)
        
    def contextMenu(self, point):
        """
        Context Menu (right click on the tree_widget)
        """
        
        
        if self.tree_widget.itemAt(point) != None:
            if self.tree_widget.columnAt(point.x()) == 1:        
                return self.contextMenuAdresses(point)
            if self.tree_widget.columnAt(point.x()) == 2:
                return self.contextMenuModels(point)
        pic = PyInstrumentsConfig()
        
        def remove():
            """
            removes an item
            """
            
            pic.remove(logical_name)
            self.refresh()
            
        def add(): 
            """
            adds an item
            """
            
            tag = pic.add_instrument()
            self.refresh()
            
        menu = QtGui.QMenu(self)
        actionAddDevice = QtGui.QAction("add device", self)
        actionAddDevice.triggered.connect(add)
        menu.addAction(actionAddDevice)
        items = self.tree_widget.selectedItems()
        if len(items)>0:
            obj = items[0]
            logical_name = str(obj.text(0))
            address = str(obj.text(1))
            actionRemoveDevice = QtGui.QAction("remove " + \
                                               logical_name + \
                                               "?", \
                                            self)
            actionRemoveDevice.triggered.connect(remove)
            menu.addAction(actionRemoveDevice)
            
            def query_model():
                """
                physically queries model from the device
                """
                
                pic[logical_name]["model"] = con.get_model_name(address)
                pic.save()
                self.refresh()
                
            
            actionQueryModel = QtGui.QAction( \
                                              "query model at address " + \
                                              address, \
                                            self)
            actionQueryModel.triggered.connect(query_model)
            menu.addAction(actionQueryModel)
            menu.addSeparator()

            #### if some specific menu_items have to be added,
            ## they will be added here
            
            

        self.exec_menu_at_right_place(menu, point)


    def auto_detect(self):
        """
        autodetects all instruments
        """
        
        con.add_all_new_instruments()
        self.refresh()
        
        
    def remove_all(self):
        """
        removes all instruments
        """
        
        pic = PyInstrumentsConfig()
        pic.clear()
        pic.save()
        self.refresh()
        
    def query_models(self):
        """
        Physically queries all instruments models
        """
        
        con.query_models()
        self.refresh()
        
        
    def get_from_gui(self):
        """updates values from the gui"""
        
        pic = PyInstrumentsConfig()
        pic.clear()
        for itm in self.tree_widget:
            pic[itm.val("logical_name")] = {"address" : itm.val("address"),
                                            "model" : itm.val("model"),
                                            "simulate" : itm.val("simulate"),
                                            "code": itm.val("code")}
        pic.save()
    
    def item_changed(self):
        """an item changed in the gui"""

        self.get_from_gui()
        pic = PyInstrumentsConfig()
        self.fast_refresh()
        self.get_from_gui()