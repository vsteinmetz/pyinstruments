"""module to interface the TDS2024b scope (using VISA interface)"""

from pyhardware.drivers.visa import VisaDriver
from pyhardware.utils.guiwrappersutils import GuiWrapper
from pyhardware.utils.gui_fetch_utils import FetcherMixin
from curve import Curve
from pyivi.ivicom.iviscope import ShortCutScope


from pandas import Series
import pandas
import visa
import numpy

class TDS2024B(VisaDriver,  GuiWrapper, FetcherMixin):
    _supported_models = ["TDS 2024B"]
    _fields = ShortCutScope._fields + ['channel_idx'] + ["sample_modes", "acquisition_types", "ch_couplings"]

    def __init__(self,*args,**keys):
        super(TDS2024B, self).__init__(*args,**keys)
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
    
    def autoset(self):
        self.write("AUTOSet EXECute")

    @property
    def record_length(self):
        return int(self.ask("HORizontal:RECOrdlength?"))

    @record_length.setter
    def record_length(self,length=2500):
        #self.write("HORizontal:RECOrdlength "+str(length))
        #command not available
        pass
    
#    @property
#    def sample_rate(self):
#        return float(self.ask("HORizontal:MAIn:SAMPLERate?"))
#    @sample_rate.setter
#    def sample_rate(self,val):
#        self.write("HORizontal:MAIn:SAMPLERate "+str(val))

    @property
    def number_of_averages(self):
        return int(self.ask("ACQuire:NUMAVg?"))
    @number_of_averages.setter
    def number_of_averages(self,val=2):
        self.write("ACQuire:NUMAVg "+str(val))

    @property
    def acquisition_type(self):
        return self.ask("ACQuire:MODe?")
    @acquisition_type.setter
    def acquisition_type(self,val='SAMple'):
        self.write("ACQuire:MODe "+val)

    @property
    def ch_coupling(self):
        return self.ask("CH"+str(self.channel_idx)+":COUPling?")
    @ch_coupling.setter
    def ch_coupling(self,val='DC'):
        self.write("CH"+str(self.channel_idx)+":COUPling "+str(val))

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
        bw = self.ask("CH"+str(self.channel_idx)+":BANdwidth?")
        if bw == 'OFF':
            return 1e9
        else:
            return float(bw)
    
    @ch_input_frequency_max.setter
    def ch_input_frequency_max(self,val=1e9):
        self.write("CH"+str(self.channel_idx)+":BANdwidth "+str(val))

    #keeping easy_waveform only for compatibility purposes
    def easy_waveform(self,ch = 1): 
        #set encoding to one byte per datapoint
        self.write("DATa:WIDth 1")
        #binary data encoding with 
        #positive integer, most significant byte first
        #self.write("DATa:ENCdg ASCIi")
        # or RPBinary for faster data transfer
        self.write("DATa:ENCdg RPBinary")
        #transfer from first to last (2500th) datapoints
        self.write("DATa:STARt 1") 
        self.write("DATa:STOP 2500")
        #activate and select channel to read out
        self.write("SELect:CH%i ON" %ch)
        self.write("DATa:SOUrce CH%i" %ch )
        #set Y format
        self.write("WFMPre:PT_Fmt Y")
        
        #extract wafeform scaling parameters
        YZEro = float(self.ask("WFMPRe:YZEro?"))
        YMUlt = float(self.ask("WFMPRe:YMUlt?"))
        YOFf = float(self.ask("WFMPRe:YOFf?"))
        XZEro = float(self.ask("WFMPRe:XZEro?"))
        XINcr = float(self.ask("WFMPRe:XINcr?"))
        PT_OFf = float(self.ask("WFMPRe:PT_OFf?"))
        NR_Pt = int(self.ask("WFMPRe:NR_Pt?"))
        
        #read wafeform preamble 
        preamble = self.ask("WFMPRe?")
        print preamble
        
        #start data transfer
        rawdata = map(ord,tuple(self.ask("CURVe?")[-NR_Pt:]))

        #scale obtained data
        tcol = XZEro+XINcr*(Series(range(NR_Pt))-PT_OFf)
        trace = YZEro + YMUlt*(Series(rawdata,index=tcol)-YOFf)
        return trace
    
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
        points = 2500 #self.record_length
        self.write("DATa:STOP "+str(points))
        #activate and select channel to read out
        self.write("SELect:CH%i ON" %self.channel_idx)
        self.write("DATa:SOUrce CH%i" %self.channel_idx )
        #set Y format
        self.write("WFMOutpre:PT_Fmt Y")
        #extract wafeform scaling parameters
        YZEro = float(self.ask("WFMPRe:YZEro?"))
        YMUlt = float(self.ask("WFMPRe:YMUlt?"))
        YOFf = float(self.ask("WFMPRe:YOFf?"))
        XZEro = float(self.ask("WFMPRe:XZEro?"))
        XINcr = float(self.ask("WFMPRe:XINcr?"))
        PT_OFf = float(self.ask("WFMPRe:PT_OFf?"))
        NR_Pt = int(self.ask("WFMPRe:NR_Pt?"))
        #read wafeform preamble 
        #preamble = self.ask("WFMPRe?")
        
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
        meta["coupling"] = self.ch_coupling
        meta["full_range"] = self.ch_range
        meta["input_freq_max"] = self.ch_input_frequency_max
        meta["channel"] = "CH"+str(self.channel_idx)
        meta["curve_type"] = "ScopeCurve"
        meta["instrument_logical_name"] = self.logical_name
        
        curve = Curve()
        curve.set_data(pandas.Series(x_y[1], index = x_y[0]))
        curve.set_params(**meta)
        return curve

 
if __name__ == "__main__":
    ea = TDS2024B(sys.argv[1])
    