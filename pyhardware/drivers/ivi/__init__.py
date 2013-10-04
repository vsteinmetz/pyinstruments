"""
drivers using the ivi interop, including the sessionFactory and config_store
to instantiate and initialize the driver. These drivers are automatically
IVI-compliant.
"""

from pyhardware.drivers.ivi.ividriver import IviDriver, \
                                                            add_fields

from pyhardware.drivers.ivi.scope import IviScopeDriver
from pyhardware.drivers.ivi.specan import IviSpecAnDriver
from pyhardware.drivers.ivi.agna import IviAgNADriver

from PyQt4 import QtCore, QtGui




class IviFGenDriver(IviDriver):
    specialized_name = 'IviFgen'