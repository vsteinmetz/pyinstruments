from pyhardware.utils.guiwrappersutils import graphical_exception

from PyQt4 import QtCore, QtGui
import os

class FetcherMixin(object):
    """
    Defines usefull functions to setup GUI for fetching curves.
    This is a very strategic class because by monkey patching it (and only it)
    the 'normal drivers' are transformed into 'db drivers' when the module
    pyinstruments.pyhardwaredb is imported.
    """
    
    def get_savefile(self):
        settings = QtCore.QSettings("pyinstruments", "pyinstruments")
        default_save_dir = str(settings.value("default_save_dir").toString())
        dialog = QtGui.QFileDialog(directory = default_save_dir)
        filename = str(dialog.getSaveFileName(filter = "*.h5"))
        if filename == "":
            return
        if not filename.endswith(".h5"):
            filename = filename + ".h5"
        settings.setValue("default_save_dir", os.path.dirname(filename))
        return filename

    def _save_curve(self, curve):
        filename = self.get_savefile()
        if not filename:
            return
        curve.save(filename)
    
    def save_curve(self):
        """Saves the curve by opening a FileDialog to find the location"""

        curve = self.get_curve()
        self._save_curve(curve)
    
    def _setup_fetch_buttons(self, widget):
        self.button_save = QtGui.QPushButton('save wfm...')
        self.button_save.pressed.connect(graphical_exception(self.save_curve))
        widget.current_layout.addWidget(self.button_save)
        
    def get_curve(self):
        return self._get_curve()
    
_THE_FETCHER_MIXIN_CLASS = FetcherMixin

def get_fetcher_mixin():
    global _THE_FETCHER_MIXIN_CLASS
    return _THE_FETCHER_MIXIN_CLASS