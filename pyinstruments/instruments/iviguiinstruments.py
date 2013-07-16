"""
Instruments that offer the possibility to display a Graphical User Interface
"""

from pyinstruments.instruments import MenuItem

class IviGuiInstrument:
    """
    Instruments that offer the possibility to display a Graphical User Interface
    """
    
    #def gui(self):
     #   """should open a gui window"""

      #  raise NotImplementedError()
    
    def menu_items(self):
        """The objects of type MenuItem returned by this function allow the 
        PyInstrumentsConfigGui to know which menu items to add upon right click
        on an instrument that is handled by this class.
        """
        
        return [MenuItem("Graphical User Interface ...", self.gui)] 