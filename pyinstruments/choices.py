from model_utils import Choices

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