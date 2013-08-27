from pyinstruments.pyhardware.drivers.ivi import IviDriver, \
                                                 add_fields
from pyinstruments.utils.guiwrappersutils import GuiWrapper
from pyivi.ivicom.ivispecan import ShortCutSpecAn

                
class IviSpecAnDriver(IviDriver, GuiWrapper):
    specialized_name = 'IviSpecAn'
    _fields = []
    def __init__(self, pyividriver):
        super(IviSpecAnDriver, self).__init__(pyividriver)
        GuiWrapper.__init__(self)

    
    def _setupUi(self, widget):
        """sets up the graphical user interface"""
        
        widget._setup_vertical_layout()
        for field in self._fields:
            choices = None
            if hasattr(self.driver.sc, field + 's'):
                choices = self.driver.sc.__getattribute__(field + 's')
            widget._setup_gui_element(field, choices)
        widget._exit_layout()
        

add_fields(IviSpecAnDriver, [field[0] for field in ShortCutSpecAn._fields])
#add_fields(IviScopeDriver, ['channel_idx'])
#add_fields(IviScopeDriver, [field[0] for field in ShortCutScope._channel_related_fields])
    