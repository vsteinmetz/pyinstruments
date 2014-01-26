from pyhardware.drivers.visa import VisaDriver

import visa
### quick and dirty for now, waiting for answers to the question :
#http://stackoverflow.com/questions/13840997/python-instrument-drivers


class AFG(VisaDriver):
    _supported_models = ["AFG3102", "AFG3022B"]    
    def __init__(self, *args,**kwds):
        super(AFG, self).__init__(*args, **kwds)
        self.waveforms = list(["SINusoid","SQUare","PULse","RAMP","PRNoise","DC","SINC","GAUSsian","LORentz","ERISe","EDECay","HAVersine"])
        self.channel_idx = 1
        self.amplitudelock = False
        self.frequencylock = False
        self.phaseinit()

    def recall(self, num='0'):
        self.write("*RCL "+str(num))

    def save(self,num='0'):
        self.write("*SAV " + str(num))

    @property
    def output_enabled(self):
        return self.ask("OUTPut%d:STATe?"%self.channel_idx)=='1'
    @output_enabled.setter
    def output_enabled(self,val):
        if val:
            self.write("OUTPut%d:STATe ON"%self.channel_idx)
        else:
            self.write("OUTPut%d:STATe OFF"%self.channel_idx)
    
    @property
    def am(self):
        return self.ask("SOURCe%d:AM:STATe?"%self.channel_idx)=='1'
    @am.setter
    def am(self,val):
        if val:
            self.write("SOURCe%d:AM:STATe ON"%self.channel_idx)
        else:
            self.write("SOURCe%d:AM:STATe OFF"%self.channel_idx)
    
    @property
    def fm(self):
        return self.ask("SOURCe%d:FM:STATe?"%self.channel_idx)=='1'
    @fm.setter
    def fm(self,val):
        if val:
            self.write("SOURCe%d:FM:STATe ON"%self.channel_idx)
        else:
            self.write("SOURCe%d:FM:STATe OFF"%self.channel_idx)
    
    @property
    def pm(self):
        return self.ask("SOURCe%d:PM:STATe?"%self.channel_idx)=='1'
    @pm.setter
    def pm(self,val):
        if val:
            self.write("SOURCe%d:PM:STATe ON"%self.channel_idx)
        else:
            self.write("SOURCe%d:PM:STATe OFF"%self.channel_idx)
          
    @property
    def pwm(self):
        return self.ask("SOURCe%d:PWM:STATe?"%self.channel_idx)=='1'
    @pwm.setter
    def pwm(self,val):
        if val:
            self.write("SOURCe%d:PWM:STATe ON"%self.channel_idx)
        else:
            self.write("SOURCe%d:PWM:STATe OFF"%self.channel_idx)

    def calibrate():
        return (int (self.ask("*CAL?")) == 0)

    def phaseinit(self):
        self.write("SOURce%d:PHASe:INITiate"%self.channel_idx)

    @property
    def waveform(self):
        return self.ask("SOURce%d:FUNCtion:SHAPe?"%self.channel_idx)
    @waveform.setter
    def waveform(self,val="SIN"):
        self.write("SOURce%d:FUNCtion:SHAPe %s"%(self.channel_idx,val)) 
    
    @property
    def duty_cycle_high(self):
        return float(self.ask("SOURce%d:FUNCtion:RAMP:SYMMetry?"%self.channel_idx))
    @duty_cycle_high.setter
    def duty_cycle_high(self,val=50.0):
        self.write("SOURce%d:FUNCtion:RAMP:SYMMetry %f"%(self.channel_idx,val))

    @property
    def impedance(self):
        return float(self.ask("OUTPut%d:IMPedance?"%self.channel_idx))
    @impedance.setter
    def impedance(self,val=50):
        self.write("OUTPut%d:IMPedance %fOHM"%(self.channel_idx,val))

    @property
    def polarity(self):
        return self.ask("OUTPut%d:POLarity?"%self.channel_idx)
    @polarity.setter
    def polarity(self,val="NORMal"):
        self.write("OUTPut%d:POLarity %s"%(self.channel_idx,val))

    @property
    def triggerout(self):
        return self.ask("OUTPut:TRIGger:MODE?")
    @triggerout.setter
    def triggerout(self,val="TRIGger"):
        self.write("OUTPut:TRIGger:MODE %s"%val)

    @property
    def roscillator(self):
        return self.ask("SOURce:ROSCillator:SOURce?")
    @roscillator.setter
    def roscillator(self,val="EXT"):
        self.write("SOURce:ROSCillator:SOURce %s"%val)

    "locks voltages of both channels to each other"
    @property
    def amplitudelock(self):
        """
        locks voltages of both channels to each other
        """
        return self.ask("SOURCe%d:VOLTage:CONCurrent:STATe?"%self.channel_idx)=='1'
    @amplitudelock.setter
    def amplitudelock(self,val):
        """
        locks voltages of both channels to each other
        """
        if val:
            self.write("SOURCe%d:VOLTage:CONCurrent:STATe ON"%self.channel_idx)
        else:
            self.write("SOURCe%d:VOLTage:CONCurrent:STATe OFF"%self.channel_idx)

    @property
    def frequencylock(self):
        """
        locks frequencies of both channels to each other
        """
        return self.ask("SOURCe%d:FREQuency:CONCurrent:STATe?"%self.channel_idx)=='1'
    @frequencylock.setter
    def frequencylock(self,val):
        """
        locks frequencies of both channels to each other
        """
        if val:
            self.write("SOURCe%d:FREQuency:CONCurrent:STATe ON"%self.channel_idx)
        else:
            self.write("SOURCe%d:FREQuency:CONCurrent:STATe OFF"%self.channel_idx)

#numerical values
    @property
    def amplitude(self):
        """
        defines the signal amplitude in Vpp 
        """
        return float(self.ask("SOURce%d:VOLTage:LEVel:IMMediate:AMPLitude?"%self.channel_idx))
    @amplitude.setter
    def amplitude(self,val=0):
        """
        defines the signal amplitude in Vpp 
        """
        self.write("SOURce%d:VOLTage:LEVel:IMMediate:AMPLitude %fVPP"%(self.channel_idx,val))

    @property
    def frequency(self):
        return float(self.ask("SOURCe%d:FREQuency:FIXed?"%self.channel_idx))
    @frequency.setter
    def frequency(self,val=0):
        self.write("SOURCe%d:FREQuency:FIXed %fHz"%(self.channel_idx,val))

    @property
    def phase(self):
        return float(self.ask("SOURce%d:PHASe:ADJust?"%self.channel_idx))
    @phase.setter
    def phase(self,val=0):
        self.write("SOURce%d:PHASe:ADJust %f"%(self.channel_idx,val))

    @property
    def offset(self):
        return float(self.ask("SOURce%d:VOLTage:LEVel:IMMediate:OFFSet?"%self.channel_idx))
    @offset.setter
    def offset(self,val=0):
        self.write("SOURce%d:VOLTage:LEVel:IMMediate:OFFSet %fV"%(self.channel_idx,val))

        
#
#""" BLANK to fill in new properties
#    @property
#    def (self):
#        return float(self.ask("%d?"%self.channel_idx))
#    @.setter
#    def (self,val=0):
#        self.write("%d"%self.channel_idx%val)
#

#"""
