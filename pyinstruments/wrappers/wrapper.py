"""
Wrapper is used to expose all properties of an object at runtime
"""

class Wrapper(object):
    """
    Wrapper is used to expose all properties of an object at runtime. When 
    accessing an attribute, looks first in the Wrapper, if the attribute is 
    not found, looks in the wrapped object.
    """
    
    _direct_from_wrapped = "__all__"
    
    def __init__(self, wrapped):
        self._wrapped = wrapped
        
    
    def __getattr__(self, name):
        try:
            return super(Wrapper, self).__getattr__(name)
        except AttributeError:
            pass
        
        direct = super(Wrapper, self).__getattribute__(\
                                            "_direct_from_wrapped")
        if direct == "__all__" or name in direct:
            try:
                return getattr(super(Wrapper,\
                                     self).__getattribute__("_wrapped"),name)
            except AttributeError:
                raise AttributeError("Attribute " + name + " was found \
neither in the wrapped object, nor in the object itself")
    
    def __setattr__(self, name, val):
        direct = super(Wrapper, self).__getattribute__(\
                                                "_direct_from_wrapped")
        try:
            wrapped = super(Wrapper, self).__getattribute__("_wrapped")
        except AttributeError:
            return super(Wrapper, self).__setattr__(name, val)
        if direct == "__all__":
            direct = dir(wrapped)
        if name in direct:
            wrapped.__setattr__(name, val)
        else:
            return super(Wrapper, self).__setattr__(name, val)
        
    def __dir__(self):
        direct = []
        if "__all__" == self._direct_from_wrapped:
            direct = dir(self._wrapped)
        else:
            direct = self._direct_from_wrapped
        the_list = dir(super(Wrapper, self)) + direct
        return the_list