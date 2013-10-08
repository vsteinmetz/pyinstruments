from pyinstruments.curvestore.curve_create_widget import CurveCreateWidget
from pyinstruments.curvefinder.gui.curve_display_widget.id_display_widget import IdDisplayWidget


from PyQt4 import QtCore, QtGui

class CurveAlterWidget(CurveCreateWidget):
    curve_saved = QtCore.pyqtSignal()
    delete_done = QtCore.pyqtSignal()
    def __init__(self, parent=None):
        super(CurveAlterWidget, self).__init__(parent=parent)
        self.id_widget = IdDisplayWidget()
        self.h_lay1.insertWidget(0, self.id_widget)
        self.save_button.deleteLater()
        self.save_button = self.id_widget.save_button
        
        self.curve_modified.connect(
                            self.save_button.show)

#        self.setLayout(self.h_lay1)
        
        self.id_widget.save_pressed.connect(
                                    self.save_button.hide)
        self.id_widget.save_pressed.connect(self.save)
        self.id_widget.delete_done.connect(self.delete_done)
        self.current_curve = None
    
    def save(self):
        if self.current_curve!=None:
            self.save_curve(self.current_curve)
            self.curve_saved.emit()
            
    def display_curve(self, curve):
        self.current_curve = curve
        self.id_widget.display_curve(curve)
        self.dump_in_gui(curve)