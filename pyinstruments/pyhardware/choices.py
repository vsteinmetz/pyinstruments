#from model_utils import Choices #I don't want to import the whole django just for this
class Choices(list):
    def __init__(self, *args):
        self._choices = args
        for choice in args:
            setattr(self, choice, choice)
        super(Choices, self).__init__(zip(args, args))
        self._choice_dict = dict(self)

scope_acquisition_types = Choices("normal",
                           "peakDetect",
                           "hiRes",
                           "enveloppe",
                           "average")

spec_an_acquisition_types = Choices("ClearWrite", 
                                    "MaxHold", 
                                    "MinHold", 
                                    "Average")
spec_an_detector_types = Choices("Sample", 
                                "Off", 
                                "Neg", 
                                "Average", 
                                "Pos", 
                                "Qpe", 
                                "Rav",
                                "AverageAgain", 
                                "Norm", 
                                "Eav")

scope_couplings = Choices("AC",
                   "DC",
                   "GND")

na_formats = Choices("Real", 
                        "Polar", 
                        "LinMag", 
                        "GroupDelay", 
                        "Imag", 
                        "PPhase", 
                        "Smith", 
                        "UPhase",
                        "SLinear", 
                        "SLogarithmic",
                        "Complex")