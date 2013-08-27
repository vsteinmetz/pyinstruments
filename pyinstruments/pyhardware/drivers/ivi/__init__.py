"""
drivers using the ivi interop, including the sessionFactory and config_store
to instantiate and initialize the driver. These drivers are automatically
IVI-compliant.
"""

from pyinstruments.pyhardware.drivers.ivi.ividriver import IviDriver, \
                                                            add_fields

from pyinstruments.pyhardware.drivers.ivi.scope import IviScopeDriver
from pyinstruments.pyhardware.drivers.ivi.specan import IviSpecAnDriver

from PyQt4 import QtCore, QtGui


class IviNADriver(IviDriver):
    specialized_name = ''

class IviFGenDriver(IviDriver):
    specialized_name = 'IviFgen'