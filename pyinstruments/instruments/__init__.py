"""
Package containing the higher level instrument control classes. Theses classes
assume that the lower-level drivers are IVI-compliant and provide user-
friendly functionalities like Graphical User Interfaces.

Defining one's own instrument wrapper is rather simple. Just use the decorator
pyinstruments.use_for_ivi to register the class as the default wrapper.
"""

class MenuItem(object):
    """If an instrument has a function self.menu_items() that return a list \
    of instances of MenuItem, the corresonding items will appear in the 
    PyInstrumentsConfigGui
    """
    
    def __init__(self,text,action):
        """text is the text that will appear in the menuItem
        action is the function to execute upon click on the menuItem.
        The function should take the wrapper_class instance as first (and only) argument"""
        self.text = text
        self.action = action
        
from pyinstruments.instruments.ivi_scope_gui import IviScopeGui
from pyinstruments.instruments.ivi_spec_an_gui import IviSpecAnGui
from pyinstruments.instruments.ivi_na_gui import IviNaGui