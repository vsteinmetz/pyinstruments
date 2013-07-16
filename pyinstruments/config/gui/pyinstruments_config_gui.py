"""
This module is here to allow GUI interaction with the config file
"""

from pyinstruments.config.gui.pytreewidget import PyTreeWidget
from pyinstruments.config.pyinstruments_config import PyInstrumentsConfig
import pyinstruments.config.connected_instruments as con
from pyinstruments.factories import driver_factory
from pyinstruments import instrument

from PyQt4 import QtCore, QtGui
import os

class PyInstrumentsConfigGui(QtGui.QMainWindow):
    """
    Main gui class
    """
    
    def __init__(self, parent = None):
        """
        creates the window and associates it with the config object
        """
        
        super(PyInstrumentsConfigGui, self).__init__(parent)
        self.setupUi(self)
        self.show()
        self.loaded_drivers = dict()

        QtCore.QObject.connect(self.actionRefresh, \
                               QtCore.SIGNAL('triggered()'), \
                               self.refresh)
        QtCore.QObject.connect(self.actionAutoDetect, \
                               QtCore.SIGNAL('triggered()'), \
                               self.auto_detect)
        QtCore.QObject.connect(self.actionRemoveAll, \
                               QtCore.SIGNAL('triggered()'), \
                               self.remove_all)
        QtCore.QObject.connect(self.actionQueryModels, \
                               QtCore.SIGNAL('triggered()'), \
                               self.query_models)
        self.treeWidget.itemChanged.connect(self.item_changed) 
        self.treeWidget.setColumnWidth(0, 100)
        self.treeWidget.setColumnWidth(1, 100)
        self.treeWidget.setColumnWidth(2, 100)
        self.treeWidget.setColumnWidth(3, 100)
        self.refresh()
       
    def dummy(self):
        for i in range(10):
            print con.existing_addresses()
         
    def setupUi(self, MainWindow):
        """sets up the GUI"""
        
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(405, 400)
        self.treeWidget = PyTreeWidget(["logical_name", \
                                        "address", \
                                        "model", \
                                        "simulate"])
        self.treeWidget.setGeometry(QtCore.QRect(0, 0, 401, 400))
        self.treeWidget.setIndentation(20)
        self.treeWidget.setObjectName("treeWidget")
        self.treeWidget.header().setDefaultSectionSize(500)
        self.setCentralWidget(self.treeWidget)        
        
        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 401, 21))
        self.menubar.setObjectName("menubar")
        self.menuFile = QtGui.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.actionRefresh = QtGui.QAction(MainWindow)
        self.actionRefresh.setObjectName("actionRefresh")
        self.actionRemoveAll = QtGui.QAction(MainWindow)
        self.actionRemoveAll.setObjectName("actionRemoveAll")
        
        self.actionQueryModels = QtGui.QAction(MainWindow)
        self.actionQueryModels.setObjectName("actionQueryModels")
        self.menuFile.addAction(self.actionQueryModels)
        
        self.actionAutoDetect = QtGui.QAction(MainWindow)
        self.actionAutoDetect.setObjectName("actionAutoDetect")
        self.menuFile.addAction(self.actionAutoDetect)
        
        self.actionHelp = QtGui.QAction(MainWindow)
        self.actionHelp.setObjectName("actionHelp")
        self.menuFile.addAction(self.actionRefresh)
        self.menuFile.addAction(self.actionRemoveAll)
        self.menubar.addAction(self.menuFile.menuAction())
        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)  
        self.setWindowIcon(\
                        QtGui.QIcon(os.path.split(__file__)[0] +"/USB.jpg")) 
        
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
        
    
    def _refresh(self, full = False):
        """
        refreshes the gui, if full, sets also the color of the addess field
        """
        
        pic = PyInstrumentsConfig()
        self.treeWidget.blockSignals(True)
        self.treeWidget.remove_all_items()
        for tag, instr in pic.iteritems():
            widgetItem = self.treeWidget.add_item("", \
                                                  "", \
                                                  "", \
                                                  False)
            widgetItem.set_values(tag, \
                                  instr["address"], \
                                  instr["model"], \
                                  instr["simulate"])
            
            if(driver_factory(instr["model"]) is None):
                widgetItem.set_color(2, "red")
            else:
                widgetItem.set_color(2, "green")
            
            
            if(instr["address"] in con.existing_addresses(full)):
                widgetItem.set_color(1, "green")
            else:
                widgetItem.set_color(1, "red")
                    
        self.treeWidget.blockSignals(False) 
    
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

    
    def contextMenuEvent(self, event):
        """
        Context Menu (right click on the treeWidget)
        """
        
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
            
            pic.add_instrument()
            self.refresh()
            
        menu = QtGui.QMenu(self)
        actionAddDevice = QtGui.QAction("add device", self)
        actionAddDevice.triggered.connect(add)
        menu.addAction(actionAddDevice)
        items = self.treeWidget.selectedItems()
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
            
            instr = pic[logical_name]
            if(driver_factory(instr["model"]) is not None):
                if instr["simulate"] or \
                        instr["address"] in con.get_surrounding_instruments():
                    try:
                        instrument_driver = instrument(logical_name)
                    except BaseException as e:
                        print e.message
                    else:
                        try:
                            items = instrument_driver.menu_items()
                        except AttributeError:
                            items = []
                        for menu_i in items:
                            custom_action = QtGui.QAction(menu_i.text, self)
                            log_n = logical_name
                            action = menu_i.action
                            def run_custom(dummy, action = action):
                                action()
                            custom_action.triggered.connect(run_custom)
                            menu.addAction(custom_action)

        menu.exec_(event.globalPos()) 
        
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
        for itm in self.treeWidget:
            pic[itm.val("logical_name")] = {"address" : itm.val("address"), \
                                            "model" : itm.val("model"), \
                                            "simulate" : itm.val("simulate")}
        pic.save()
    
    def item_changed(self):
        """an item changed in the gui"""
        
        self.get_from_gui()
        self.fast_refresh()
        self.get_from_gui()