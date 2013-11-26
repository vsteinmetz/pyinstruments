import clr
import sys
from numpy import *

try:
    from myPandas import Series,DataFrame
except ImportError:
    print "could not find the module myPandas customizing the class Series in pandas, will return pandas.Series instead"
    from pandas import Series,DataFrame
    def dummy(*args,**kwds):
        pass
    Series.set_meta = dummy

#sys.path.append('C:\\Program Files\\Agilent\\89600 Software 15.0\\89600 VSA Software\\Interfaces') # if people complain about this, it should be a persistentConfig...
sys.path.append('C:\\Program Files\\Agilent\\89600 Software 16.0\\89600 VSA Software\\Interfaces') # if people complain about this, it should be a persistentConfig...
clr.AddReference("Agilent.SA.Vsa.Interfaces") ## no .dll
import Agilent.SA.Vsa as Vsa
from Agilent.SA.Vsa import ApplicationFactory,TraceDataSelect
print "trying to connet to an existing vsa instance"
app = ApplicationFactory.Create()
if app == None:
    print "no vsa running, launching one"
    app = ApplicationFactory.Create(True,None,None,-1) # creating new one
app.IsVisible = True



        
def set_meta_from_meas(res,meas):
    res.meta.set("Time")
    res.meta.Time.set(Length = meas.Time.Length,
                      Points = meas.Time.Points,
                      IsGate = meas.Time.IsGate,
                      IsResolutionAuto = meas.Time.IsResolutionAuto,
                      GateDelay = meas.Time.GateDelay,
                      GateLength = meas.Time.GateLength)
    res.meta.set("Frequency")
    res.meta.Frequency.set(Center = meas.Frequency.Center,
                           GateWindow = meas.Frequency.GateWindow,
                           GateWindowIsMain = meas.Frequency.GateWindowIsMain,
                           InputSampleRate = meas.Frequency.InputSampleRate,
                           IsPointsAuto = meas.Frequency.IsPointsAuto,
                           IsResBWArbitrary = meas.Frequency.IsResBWArbitrary,
                           IsSignalTrack = meas.Frequency.IsSignalTrack,
                           IsStepAuto = meas.Frequency.IsStepAuto,
                           IsZoom = meas.Frequency.IsZoom,
                           Points = meas.Frequency.Points,
                           ResBW = meas.Frequency.ResBW,
                           ResBWCouple = meas.Frequency.ResBWCouple,
                           SampleRate = meas.Frequency.SampleRate,
                           SignalTrackChannel = meas.Frequency.SignalTrackChannel,
                           Span = meas.Frequency.Span,
                           StartFrequency = meas.Frequency.StartFrequency,
                           StepSize = meas.Frequency.StepSize,
                           StopFrequency = meas.Frequency.StopFrequency,
                           Window = meas.Frequency.Window)
    res.meta.set("Average")
    res.meta.Average.set(Count = meas.Average.Count,
                         IsFast = meas.Average.IsFast,
                         IsRepeat = meas.Average.IsRepeat,
                         IsUpdateRateCount = meas.Average.IsUpdateRateCount,
                         Style = meas.Average.Style,
                         UpdateRate = meas.Average.UpdateRate)        

                
                
     
    
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
            
class _on_screen:
    """you can access one of the following traces with quick[n],
     look at the other properties for more options"""

    def wait_done(self,meas_number = 0):
        while(not self.meas_done(meas_number)):
            pass

    def pause(self,meas_number = 0):
        self.measurement(meas_number).Pause()
        
    def resume(self,meas_number = 0):
        self.measurement(meas_number).Resume()

    def set_average(self,n,meas_number = 0):
        self.measurement(meas_number).Average.Count = n

    def measurement(self,meas_number = 0):
        """returns the list of measurements"""
        return app.Measurements[meas_number]
    
    def restart(self,meas_number = 0):
        """equivalent to restart button"""
        app.Measurements[meas_number].Restart()
    
    def wait_average(self,count):
        while self.current_average()<count:
            pass

    
    def current_average(self,label = "A"):
        return self._trace_(label).MeasurementData.State.Value("CurrentNumAverages",1)
    
    def meas_done(self,meas_number = 0):
        """returns True if the average is complete (obviously this doesn't apply on continuous measurements...)"""
        
        status = app.Measurements[meas_number].Status.Value
        return  (status & (0b1<<2)) == 0
    
    
    def _trace_(self,label):
        tr = app.Display.Traces
        for i in tr:
            if i.Label==label:
                return i
        raise ValueError("no trace with label "+ str(label))
        
    
    def get_trace(self,label,name = None):#,vector_if_possible = True):
        """label is A,B,C...
        returns a pandas Series containing nothing but the mere X values as index and Y values as values (only data seen on screen)"""
        tr = self._trace_(label)
        trData = tr.MeasurementData
        X = list(tr.DoubleData(TraceDataSelect.X,True))
        Y = list(tr.DoubleData(TraceDataSelect.Y,True))
        
        if name == None:
            name = tr.DataName
        else:
            name = name + "_" + tr.DataName
        res = Series(Y,index = X,name = name)
        meas = app.Measurements[tr.MeasurementIndex]
        set_meta_from_meas(res,meas)
        
        return res
    
            
    def traces(self):
        """returns the list of traces objects as displayed on the vsa screen"""
        return list(app.Display.Traces)
    
    def __call__(self,label = "all",name = None):#,vector_if_possible = True):
        """returns a pandas Series if you provide the label of the trace (A,B,C...)
        or a DataFrame containing all the displayed traces as columns. You can access them via trace["spectrum1"]...
        """
        if label=="all":
            cols = dict()
            for t in self.traces():
                if t.DataName != "No Data":
                    cols[t.DataName] = self.get_trace(t.Label,name)
            return DataFrame(cols)
        else:
            return self.get_trace(label,name)

on_screen = _on_screen()
data = _data()