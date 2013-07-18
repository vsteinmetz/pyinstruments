class DotNetIntermediateCollection:
    """This class emulates (almost) all the methods available 
    for a dictionnary to access the collection in the driver
    """
    def __init__(self, driver_col, wrapper_class):
        self.driver_col = driver_col
        self.wrapper_class = wrapper_class
        self._values = dict() 
        ## returns the same element if the element was already asked for
    
    def __getitem__(self, i):
        if i in self._values:
            return self._values[i]
        else:
            self._values[i] = self.wrapper_class(self.driver_col.get_Item(i))
        return self._values[i]
    
    def __iter__(self):
        for i in range(len(self)):
            name = self.driver_col.get_Name(i+1)
            if name in self._values:
                yield self._values[name]
            else:
                self._values[name] = self.wrapper_class(\
                                self.driver_col.get_Item(\
                                self.driver_col.get_Name(i+1)))
                yield self._values[name]

    def __len__(self):
        from System.Runtime.InteropServices import COMException
        try:
            return self.driver_col.get_Count()
        except COMException:
            for i in range(100):
                try:
                    self.driver_col.get_Name(i+1)
                except COMException:
                    return i
    
    def __repr__(self):
        return self.__str__()
    
    def __str__(self):
        return str(self.keys())
             

    def keys(self):
        """see dict.keys()"""
        return tuple([str(self.driver_col.get_Name(i+1))\
                       for i in range(len(self))])

    def values(self):
        """see dict.values()"""
        return tuple([v for v in self])
            
    def iteritems(self):
        """see dict.iteritems()"""
        return zip(self.keys(), self.values())
        
    def __delitem__(self):
        raise NotImplementedError(\
                "cannot delete an item from a driver collection")
        
    def __setitem__(self):
        raise NotImplementedError(\
                "cannot set an item from a driver collection")