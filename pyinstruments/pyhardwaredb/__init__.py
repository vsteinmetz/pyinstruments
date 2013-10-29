"""
This minimal package simply combines pyinstruments and datastore to provide
instruments that are allowed to store their curves in the datastore.
"""


#_APP = __qapplication()

import dbinstruments
from pyhardware import instrument, gui
from pyinstruments.datastore.settings import DATABASE_FILE as _DB_FILE
import pyhardware
pyhardware._TITLE = 'pyhardwaredb: ' + _DB_FILE

#_APP.exec_()

