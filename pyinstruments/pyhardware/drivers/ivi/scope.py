from pyinstruments.pyhardware.drivers.ivi import IviDriver, \
                                                 add_fields
from pyinstruments.utils.guiwrappersutils import GuiWrapper
from pyivi.ivicom.iviscope import ShortCutScope

                
class IviScopeDriver(IviDriver, GuiWrapper):
    specialized_name = 'IviScope'
    _fields = []
    def __init__(self, pyividriver):
        super(IviScopeDriver, self).__init__(pyividriver)
        GuiWrapper.__init__(self)
        self.channel_idxs = self.driver.sc.channel_idxs
    
    def _setupUi(self, widget):
        """sets up the graphical user interface"""
        
        widget._setup_horizontal_layout()
        widget._setup_vertical_layout()
        for field in self._fields:
            if field==None:
                widget._exit_layout()
                widget._setup_vertical_layout()
                continue
            choices = None
            if hasattr(self, field + 's'):
                choices = self.__getattribute__(field + 's')
            widget._setup_gui_element(field, choices)
        widget._exit_layout()
        

add_fields(IviScopeDriver, [field[0] for field in ShortCutScope._fields])
IviScopeDriver._fields.append(None)
add_fields(IviScopeDriver, ['channel_idx'])
add_fields(IviScopeDriver, [field[0] for field in ShortCutScope._channel_related_fields])
add_fields(IviScopeDriver, ["sample_modes",
                            "acquisition_types",
                            "ch_couplings"], add_ref=False)
