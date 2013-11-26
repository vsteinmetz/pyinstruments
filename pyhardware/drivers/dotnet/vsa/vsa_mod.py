from curve import Curve
from pyhardware.utils.gui_fetch_utils import FetcherMixin
from pyhardware.utils.guiwrappersutils import GuiWrapper

from pandas import Series
import clr
import sys
from numpy import *
#sys.path.append('C:\\Program Files\\Agilent\\89600 Software 15.0\\89600 VSA Software\\Interfaces') # if people complain about this, it should be a persistentConfig...
sys.path.append('C:\\Program Files\\Agilent\\89600 Software 16.0\\89600 VSA Software\\Interfaces') # if people complain about this, it should be a persistentConfig...
clr.AddReference("Agilent.SA.Vsa.Interfaces") ## no .dll
import Agilent.SA.Vsa as Vsa
from Agilent.SA.Vsa import ApplicationFactory,TraceDataSelect


class Vsa(GuiWrapper, FetcherMixin):
    _fields = ["active_label"]
    def __init__(self):
        print "trying to connect to an existing vsa instance"
        self.app = ApplicationFactory.Create()
        if self.app==None:
            print "no vsa running, launching one"
            self.app = ApplicationFactory.Create(True,None,None,-1) 
            # creating new one
        GuiWrapper.__init__(self)
        self.app.IsVisible = True
        self._active_label = 'A'
    
    def _setupUi(self, widget):
        """sets up the graphical user interface"""
        
        widget._setup_vertical_layout()
        widget._setup_horizontal_layout()
        widget._setup_vertical_layout()
        for field in self._fields:
            if field == 'trace_idx':
                widget._exit_layout()
                widget._setup_vertical_layout()
            choices = None
            widget._setup_gui_element(field, choices)
        widget._exit_layout()
        widget._exit_layout()
        self._setup_fetch_buttons(widget)
    
    @property
    def active_label(self):
        return self._active_label
    
    @active_label.setter
    def active_label(self, val):
        self._active_label = val
    
    def wait_done(self, meas_number=0):
        while(not self.meas_done(meas_number)):
            pass

    def pause(self, meas_number=0):
        self.measurement(meas_number).Pause()
        
    def resume(self, meas_number=0):
        self.measurement(meas_number).Resume()

    def set_average(self, n, meas_number=0):
        self.measurement(meas_number).Average.Count = n

    def measurement(self, meas_number=0):
        """returns the list of measurements"""
        return self.app.Measurements[meas_number]
    
    def restart(self, meas_number=0):
        """equivalent to restart button"""
        self.app.Measurements[meas_number].Restart()
    
    def wait_average(self, count):
        while self.current_average()<count:
            pass

    
    def current_average(self, label="A"):
        return self._trace_(label).MeasurementData.State.Value("CurrentNumAverages", 1)
    
    def meas_done(self, meas_number=0):
        """returns True if the average is complete 
        (obviously this doesn't apply on continuous measurements...)"""
        
        status = self.app.Measurements[meas_number].Status.Value
        return  (status & (0b1<<2))==0
    
    
    def _trace_(self, label):
        tr = self.app.Display.Traces
        for i in tr:
            if i.Label==label:
                return i
        raise ValueError("no trace with label "+ str(label))
        
    def get_trace(self, label='A', name=None):      
        tr = self._trace_(label)
        trData = tr.MeasurementData
        X = list(tr.DoubleData(TraceDataSelect.X,True))
        Y = list(tr.DoubleData(TraceDataSelect.Y,True))
        
        if name == None:
            name = tr.DataName
        else:
            name = name + "_" + tr.DataName
        res = Series(Y, index=X)
        meas = self.app.Measurements[tr.MeasurementIndex]
        curve = Curve()
        curve.set_data(res)
        curve.set_params(**self.params_from_meas(meas))
        curve.set_params(trace_label=label) 
        return curve
        
    def _get_curve(self):
        return self.get_trace(self.active_label)
        
    def params_from_meas(self, meas):
        dic = dict()
        dic["name"] = "vsa_curve"
        dic["curve_type"] = 'VsaCurve'
        dic["averaging"] = meas.Average.Count
        dic["center_freq"] = meas.Frequency.Center
        dic["start_freq"] = meas.Frequency.StartFrequency
        dic["stop_freq"] = meas.Frequency.StopFrequency
        dic["span"] = meas.Frequency.Span
        dic["bandwidth"] = meas.Frequency.ResBW
        dic["sweep_time"] = meas.Time.Length
        #dic["detector_type"] = self.detector_types[self.detector_type]
        dic["instrument_type"] = "Vsa"
        dic["instrument_logical_name"] = "vsa"
        return dic
"""
class _data:
    def __call__(self,list_of_names = ["Main Time1","Main Time2"],measurement = 0):   
            cols = dict()
            for i in list_of_names:
                trData = app.Measurements[measurement].MeasurementData(i)
                n = trData.Points
                start = trData.XStart
                stop = start + n*trData.XDelta
                X = linspace(start,stop,n,endpoint = False)
                #X = list(tr.DoubleData(TraceDataSelect.X,True))
                Y = list(trData.DoubleData)
                if trData.IsComplex:
                    Y = array(Y[::2])+1j*array(Y[1::2])
                cols[i] = Series(Y,index = X,name = i)
                set_meta_from_meas(cols[i],app.Measurements[measurement])
            return DataFrame(cols)
    
    def available(self,measurement = 0):
        return list(app.Display.Traces.DataNames)
"""          