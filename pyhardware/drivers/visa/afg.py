from pyhardware.drivers import VisaDriver


import visa
### quick and dirty for now, waiting for answers to the question :
#http://stackoverflow.com/questions/13840997/python-instrument-drivers


class AFG3102(VisaDriver):
    _supported_models = ["AFG3102", "AFG3022B"]    
    def __init__(self, *args,**kwds):
        super(AFG3102, self).__init__(*args, **kwds)
    #    self.instr = visa.instrument(adr)
        self._activeCh = 1
        
        #ArbSigGenTwoCh.__init__(self)
        #ArbSigGen.__init__(self)
        #MultiChannel.__init__(self)
        #self.setChParam("V","SOURCE%d:VOLTAGE:AMPLITUDE",1,V,[0,5])
        #self.setChParam("f","SOURCE%d:FREQUENCY",1,Hz,[0,100e6])
        #self.setChParam("phi","SOURCE%d:PHASE:ADJUST",0,deg,[-360,360])
    
 #   def ask(self,s):
  #      return self.instr.ask(s)   

  #  def write(self,s):
  #      return self.instr.write(s)   
    
    def output1(self,on = True):
        if all_on_off:
            self.write("OUTPUT1 ON")
        else:
            self.write("OUTPUT1 OFF")
            
    def output2(self,on = True):
        if all_on_off:
            self.write("OUTPUT2 ON")
        else:
            self.write("OUTPUT2 OFF")
    
    def output(self,all_on_off = True,ch1 = None,ch2 = None):        
        ret = False
        if ch1 is not None:
            self.output1(ch1)
            ret = True
        if ch2 is not None:
            self.output1(ch2)
            ret = True
        if ret:
            return
        
        if all_on_off:
            self.write("OUTPUT1 ON")
            self.write("OUTPUT2 ON")
        else:
            self.write("OUTPUT1 OFF")
            self.write("OUTPUT2 OFF")
        
    
    def trig(self):
        self.write("*TRG")
    
    def recall(self,num):
        self.write("*RCL " + str(num))


    def save(self,num):
        self.write("*SAV " + str(num))
    
    def getChannel(self):
        return self._activeCh
    
    def setChannel(self,ch):
        self._activeCh = ch
    
    def setVoltage(self,V):
        V=float(V)
        self.write("Source" + str(self._activeCh) + ":VOLTage:AMPL " + str(V))
        
    def setFrequency(self, f):
        f=float(f)
        self.write("Source" + str(self._activeCh) +":FREQ " + str(f))
        
    def setPhase(self, phi):
        phi=float(phi)
        self.write("Source" + str(self._activeCh) +"PHAS:ADJ " + str(phi))
        
    def setVoltageLow(self,V):
        self.write("Source" + str(self._activeCh) +"VOLTage:LOW " + str(V))  
        
    def setSine(self,V=0.2,f=1e6,phi=0):
        self.write("SOURCE%d:FUNCTION SIN"%self.getChannel())
        self.setVoltage(V)
        self.setFrequency(f)
        self.setPhase(phi)
        
        
    def setOffset(self,offset = 0.0,ch = 1):
        self.write("SOUR" + str(ch) + ":VOLTage:OFFS " + str(offset))

        
    def setRamp(self,V=0.2,f=1e6,phi=0):
        self.write("SOURCE%d:FUNCTION RAMP"%self.getChannel())
        self.setVoltage(V)
        self.setFrequency(f)
        self.setPhase(phi)
        
    def setSquare(self,V=0.2,f=1e6,phi=0):
        self.write("SOURCE%d:FUNCTION SQUARE"%self.getChannel())
        self.setVoltage(V)
        self.setFrequency(f)
        self.setPhase(phi)
        
    def initPhase(self): #initialize phase lock between channels
        self.write("SOUR1:PHAS:INIT")
                
    def getFrequency(self):
        print self.ask("SOURCE%d:FREQUENCY?"%self.getChannel())
        
    def getPhase(self):
        print self.ask("SOURCE%d:PHASE?"%self.getChannel())
        
    def getOffset(self):
        return float( self.ask("SOURCE%d:VOLTage:OFFSet?"%self.getChannel()) )

    def write_waveform(self,waveform):
        """waveform should be a numpy array of floats between 0 and 1"""
        waveform_data = "#" + repr(len(repr(waveform.size*2))) + repr(waveform.size*2) + str((waveform*2**14).astype('>i2').data)
        self.write("TRACE:DATA EMEMORY,"+waveform_data)
        self.write("TRAC:COPY USER1,EMEM")
        self.write("FUNCTION USER1")