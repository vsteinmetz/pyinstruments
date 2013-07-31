"""
Class GuiFetchable defines a bunch of useful methods for instruments that can be
used to query waveforms.
"""

from curve import Curve

import numpy
import pandas
from PyQt4 import QtCore,QtGui
import os

class GuiFetchable(object):
    """Defines a bunch of useful methods for instruments that can be
    used to query waveforms."""
    
    _next_name = "some_file"
    _next_dir_name = "some_dir"

    def FetchXY(self):
        raise NotImplementedError("This function should be implemented in the \
                                    wrapper class")

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

    def save_curve(self):
        """Saves the curve by opening a FileDialog to find the location"""

        filename = self.get_savefile()
        if not filename:
            return
        curve = self.get_curve()
        curve.save(filename)

#    def _setup_hdnavigator_widget(self, widget):
#        """sets up a nice widget that helps navigate in the folders"""
#
#
#        widget_nav = nav._create_widget()
#        self.widget_nav = widget_nav
#        widget.add_below(widget_nav)
#        p = widget_nav.palette()
#        p.setColor(widget_nav.backgroundRole(), QtCore.Qt.gray)
#        widget_nav.setPalette(p)
#        widget_nav.setAutoFillBackground(True)
    
    
    def _setup_fetch_utilities(self, widget):
        """sets up the gui to fetch the waveforms in widget"""
#        self._setup_hdnavigator_widget(widget)
        widget._setup_horizontal_layout()
        widget._setup_gui_element("plot_xy")
        widget._setup_gui_element("xy_to_clipboard")
        widget._setup_gui_element("save_curve")
        widget._exit_layout()
        
    def plot_xy(self):
        """uses pylab to plot X and Y"""
        import pylab
        data = self.FetchXY()
        pylab.plot(data[0], data[1])
        pylab.show()
    
    
    def xy_to_clipboard(self):
        """copies X Y columnwise in the clipboard"""
        data = self.FetchXY()
        import StringIO
        string = StringIO.StringIO()
        fmt = "%.9g"
        numpy.savetxt(string, data.transpose(), delimiter = "\t", fmt = fmt)
        
        from pyinstruments import _APP
        clip = _APP.clipboard()
        clip.setText(string.getvalue())
        

    
    