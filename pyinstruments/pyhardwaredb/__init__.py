"""
This minimal package simply combines pyinstruments and datastore to provide
instruments that are allowed to store their curves in the datastore.
"""

from guidata import qapplication as __qapplication
_APP = __qapplication()

import dbinstruments
from pyhardware import instrument, gui




if __name__ == "__main__":
    GUI = gui()
    _APP.exec_()

