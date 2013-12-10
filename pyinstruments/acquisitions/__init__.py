"""
A GraphicalTimer is supposed to be the only instance running in the process.
All output will be redirected to the screen and at the same time to a log file...
"""
from pyinstruments.datastore.settings import MEDIA_ROOT

from PyQt4 import QtCore, QtGui
import sys
import os

class Logger(object):
    def __init__(self, filename="Default.log", widget=None):
        self.terminal = sys.stdout
        self.log = open(filename, "a")
        self.widget = widget

    def write(self, message):
        #self.terminal.write(message)
        self.widget.append(message)
        self.log.write(message)
        self.log.flush()
        
    def flush(self):
        self.log.flush()

class GraphicalTimer(QtGui.QWidget):
    default_interval = 500
    def __init__(self, title=None, autostart=True):
        super(GraphicalTimer, self).__init__()
        self.button_start = QtGui.QPushButton("start")
        self.button_start.setStyleSheet("background-color: red")
        self.button_stop = QtGui.QPushButton("stop")
        self.button_stop.setStyleSheet("background-color: green")
        self.spinbox_interval = QtGui.QSpinBox()
        self.spinbox_interval.setMaximum(1000000000)
        self.textedit_logout = QtGui.QTextEdit()
        self.textedit_logerr = QtGui.QTextEdit()
        
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.run)
        
        if title is None:
            self.title = self.__class__.__name__
        else:
            self.title = title
            
        #http://stackoverflow.com/questions/4675728/redirect-stdout-to-a-file-in-python
        sys.stdout = Logger(os.path.join(MEDIA_ROOT, self.title + "_out.log"), self.textedit_logout)
        sys.stderr = Logger(os.path.join(MEDIA_ROOT, self.title + "_err.log"), self.textedit_logout)
        
        self.setup_ui()
        self.setup_signals()
        self.show()
        self.button_stop.hide()
        
        self.interval = self.default_interval
        if autostart:
            self.button_start.click()
        
        
    def run(self):
        print """please, overwrite this function"""    
        1/0
    def close(self):
        return False
    
    def setup_ui(self):
        self.setWindowTitle(self.title)
        self.vlay = QtGui.QVBoxLayout()
        self.lay = QtGui.QHBoxLayout()
        self.lay.addWidget(self.button_start)
        self.lay.addWidget(self.button_stop)
        self.lay.addWidget(self.spinbox_interval)
        
        
        self.vlay.addLayout(self.lay)
        self.vlay.addWidget(self.textedit_logout)
        #self.vlay.addWidget(self.textedit_logerr)
        self.setLayout(self.vlay)
        #set flags such that the window can't be closed
        self.setWindowFlags(QtCore.Qt.CustomizeWindowHint | QtCore.Qt.WindowTitleHint)
        
    def setup_signals(self):
        self.spinbox_interval.valueChanged.connect(self.set_interval)
        self.button_start.clicked.connect(self.start)
        self.button_stop.clicked.connect(self.stop)
        
    def start(self):
        self.button_start.hide()
        self.button_stop.show()
        self.timer.start()
    
    def stop(self):
        self.button_stop.hide()
        self.button_start.show()
        self.timer.stop()
    
    def set_interval(self, val):
        self.spinbox_interval.setValue(val)
        self.timer.setInterval(val)
    
    @property
    def interval(self):
        return self.spinbox_interval.value()
    
    @interval.setter
    def interval(self, val): 
        self.spinbox_interval.setValue(val)
        self.timer.setInterval(val)
    

class KeithleyMeasurement(GraphicalTimer):
    default_interval = 1000
    
    def run(self):
        try:
            import time
            time.sleep(0.5)
            print "keithley"
            
        except Exception as e:
            print e
            print "reinit keithley"
        1/0
        
if __name__ == '__main__':
    from guidata import qapplication
    APP = qapplication()
    GRT = KeithleyMeasurement()
    APP.exec_()