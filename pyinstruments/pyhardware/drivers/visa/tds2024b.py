"""module to interface the TDS2024b scope (using VISA interface)"""

from pyinstruments.pyhardware.drivers.visa import VisaDriver
from pandas import Series

import visa

class TDS2024B(VisaDriver):
    _supported_models = ["TDS 2024B"]

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
        self.write("WFRMPre:PT_Fmt Y")
        
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

 
if __name__ == "__main__":
    ea = TDS2024B(sys.argv[1])
    