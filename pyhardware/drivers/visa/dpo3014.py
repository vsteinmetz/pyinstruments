"""module to interface the DPO3014 scope (using VISA interface)"""

from pyhardware.drivers.visa import VisaDriver
from pyhardware.utils.guiwrappersutils import GuiWrapper
from pyhardware.utils.gui_fetch_utils import FetcherMixin
from curve import Curve
from pyivi.ivicom.iviscope import ShortCutScope


from pandas import Series
import pandas
import visa
import numpy

class DPO3014(VisaDriver,  GuiWrapper, FetcherMixin):
    _supported_models = ["DPO3014"]
    _fields = ShortCutScope._fields + ['channel_idx'] + ["sample_modes", "acquisition_types", "ch_couplings"]
    def __init__(self,*args,**keys):
        super(DPO3014, self).__init__(*args,**keys)
        GuiWrapper.__init__(self)
        self.channel_idx = 1
    
    
    def _setupUi(self, widget):
        """sets up the graphical user interface"""
        
        widget._setup_vertical_layout()
        widget._setup_horizontal_layout()
        widget._setup_vertical_layout()
        for field in self._fields:
            if field=='channel_idx':
                widget._exit_layout()
                widget._setup_vertical_layout()
            choices = None
            if hasattr(self, field + 's'):
                choices = self.__getattribute__(field + 's')
            widget._setup_gui_element(field, choices)
        widget._exit_layout()
        widget._exit_layout()
        self._setup_fetch_buttons(widget)
    
    def recall(self, filename='1'):
        self.write("RECAll:SETUp "+str(filename))
    
    def acquire(self):
        self.write("ACQuire:STATE RUN")

    @property
    def record_length(self):
        return int(self.ask("HORizontal:RECOrdlength?"))
    @record_length.setter
    def record_length(self,length=100000):
        self.write("HORizontal:RECOrdlength "+str(length))

    @property
    def sample_rate(self):
        return float(self.ask("HORizontal:MAIn:SAMPLERate?"))
    @sample_rate.setter
    def sample_rate(self,val):
        self.write("HORizontal:MAIn:SAMPLERate "+str(val))

    @property
    def number_of_averages(self):
        return int(self.ask("ACQuire:NUMACq?"))
    @number_of_averages.setter
    def number_of_averages(self,val=2):
        self.write("ACQuire:NUMACq "+str(val))

    @property
    def acquisition_type(self):
        return self.ask("ACQuire:MODe?")
    @acquisition_type.setter
    def acquisition_type(self,val='SAMple'):
        self.write("ACQuire:MODe "+val)

    @property
    def ch_input_impedance(self):
        v=self.ask("CH"+str(self.channel_idx)+":IMPedance?")
        if v=='FIFTY':
            return 50
        elif v=='MEG':
            return 1e6
        else:
            return 0
        
    @ch_input_impedance.setter
    def ch_input_impedance(self,val):
        self.write("CH"+str(self.channel_idx)+":IMPedance "+str(val))

    @property
    def ch_coupling(self):
        return self.ask("CH"+str(self.channel_idx)+":COUPling?")
    @ch_coupling.setter
    def ch_coupling(self,val='DC'):
        self.write("CH"+str(self.channel_idx)+":COUPling "+str(val))

    @property
    def ch_offset(self):
        return float(self.ask("CH"+str(self.channel_idx)+":OFFSet?"))
    @ch_offset.setter
    def ch_offset(self,val=0):
        self.write("CH"+str(self.channel_idx)+":OFFSet "+str(val))

    @property
    def ch_range(self):
        return float(self.ask("CH"+str(self.channel_idx)+":VOLts?"))
    @ch_range.setter
    def ch_range(self,val=1.0):
        self.write("CH"+str(self.channel_idx)+":VOLts "+str(val))

    @property
    def time_per_record(self):
        return 10*float(self.ask("HORizontal:MAIn:SCAle?"))
    @time_per_record.setter
    def time_per_record(self,val=0.1):
        self.write("HORizontal:MAIn:SCAle "+str(val/10))
    
    
    @property
    def ch_input_frequency_max(self):
        return float(self.ask("CH"+str(self.channel_idx)+":BANdwidth?"))
    
    @ch_input_frequency_max.setter
    def ch_input_frequency_max(self,val=1e9):
        self.write("CH"+str(self.channel_idx)+":BANdwidth "+str(val))
    
    def fetch(self): 
        #set encoding to one byte per datapoint
        self.write("DATa:WIDth 1")
        #binary data encoding with 
        #positive integer, most significant byte first
        #self.write("DATa:ENCdg ASCIi")
        # or RPBinary for faster data transfer
        self.write("DATa:ENCdg RPBinary")
        #transfer from first to last (2500th) datapoints
        self.write("DATa:STARt 1") 
        points = self.record_length
        self.write("DATa:STOP "+str(points))
        #activate and select channel to read out
        self.write("SELect:CH%i ON" %self.channel_idx)
        self.write("DATa:SOUrce CH%i" %self.channel_idx )
        #set Y format
        self.write("WFMOutpre:PT_Fmt Y")
        
        #extract wafeform scaling parameters
        YZEro = float(self.ask("WFMOutpre:YZEro?"))
        YMUlt = float(self.ask("WFMOutpre:YMUlt?"))
        YOFf = float(self.ask("WFMOutpre:YOFf?"))
        XZEro = float(self.ask("WFMOutpre:XZEro?"))
        XINcr = float(self.ask("WFMOutpre:XINcr?"))
        PT_OFf = float(self.ask("WFMOutpre:PT_OFf?"))
        NR_Pt = int(self.ask("WFMOutpre:NR_Pt?"))
        
        #read wafeform preamble 
        #preamble = self.ask("WFMOutpre?")
        #print preamble
        
        #start data transfer
        #rawdata = map(ord,tuple(self.ask("CURVe?")[-NR_Pt:]))
        tr=self.ask("CURVe?")
        offsetByte =  int(tr[1])+2
        rawdata = numpy.frombuffer(tr,dtype = "B",offset = offsetByte)
        #scale obtained data
        #tcol = XZEro+XINcr*(Series(range(NR_Pt))-PT_OFf)
        #trace = YZEro + YMUlt*(Series(rawdata,index=tcol)-YOFf)
        tcol = XZEro+XINcr*(numpy.array(range(NR_Pt),dtype=float)-PT_OFf)
        trace = YZEro + YMUlt*(rawdata-YOFf)
        return tcol, trace

    def _get_curve(self):
        x_y = self.fetch()
        meta = dict()
        
        meta["name"] = "scope_curve"
        meta["acquisition_type"] = self.acquisition_type
        meta["averaging"] = self.number_of_averages
        meta["time_per_record"] = self.time_per_record
        meta["record_length"] = self.record_length
        meta["sample_rate"] = self.sample_rate
        meta["coupling"] = self.ch_coupling
        meta["full_range"] = self.ch_range
        meta["offset"] = self.ch_offset
        meta["input_freq_max"] = self.ch_input_frequency_max
        meta["input_impedance"] = self.ch_input_impedance
        meta["channel"] = "CH"+str(self.channel_idx)
        meta["curve_type"] = "ScopeCurve"
        meta["instrument_logical_name"] = self.logical_name
        
        curve = Curve()
        curve.set_data(pandas.Series(x_y[1], index = x_y[0]))
        curve.set_params(**meta)
        return curve
    
#add_fields(DPO3014, ShortCutScope._fields)
#add_fields(DPO3014, ['channel_idx'])
#add_fields(DPO3014, ShortCutScope._ch_fields)
#add_fields(DPO3014, ["sample_modes",
#                        "acquisition_types",
#                        "ch_couplings"], add_ref=False)
    
if __name__ == "__main__":
    ea = DPO3014(sys.argv[1])
    