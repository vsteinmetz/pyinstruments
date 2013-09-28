from PyQt4 import QtCore, QtGui

class ParamsDisplayWidget(QtGui.QWidget):
    def __init__(self, parent=None):
        super(ParamsDisplayWidget, self).__init__(parent)
        self.lay = QtGui.QVBoxLayout()
        self.tree = QtGui.QTreeWidget()
        self.lay.addWidget(self.tree)
        self.setLayout(self.lay)
        self.tree.setHeaderLabels(["column name", "value"])
        self.tree.setColumnWidth(0,150)
        self.tree.setColumnWidth(1,150)
        
    def display_curve(self, curve):
        self.tree.clear()
        for name, val in curve.params.iteritems():
            self.tree.addTopLevelItem(QtGui.QTreeWidgetItem([name, str(val)]))
        

