"""
Module used to store and retrieve usefull information in a jsonable file
"""

import json
import os

class PyInstrumentsConfig(dict):
    """
    Container class to store the configuration informations
    """
    
    def __init__(self):
        self.path = os.path.join(os.environ["HOMEDRIVE"], \
                                 os.environ["HOMEPATH"], \
                                 ".pyinstrument")
        try:
            self.load()
        except IOError:
            super(PyInstrumentsConfig, self).__init__()

    def load(self):
        """load the content from the config file on disk"""
        with open(self.path) as load_file:
            super(PyInstrumentsConfig, self).__init__(json.load(load_file))

    def save(self):
        """Saves the content from the config file on disk"""        
        json.dump(self, open(self.path, 'w'), indent = 0)

    def add_instrument(self, tag = "DEV", address = None, model = None, simulate = False):
        """adds an instrument with the given address and model in the internal
        config file of the module
        """
        
        pic = PyInstrumentsConfig()
        main_tag = tag
        n = 1
        while(tag in pic.keys()):
            tag = main_tag + str(n)
            n += 1
        pic[tag] = {"address" : address, "model" : model, "simulate" : simulate}
        pic.save()
        
    def remove(self, tag):
        del self[tag]
        self.save()
        
