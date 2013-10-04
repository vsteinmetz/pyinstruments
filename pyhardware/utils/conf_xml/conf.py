##================================================
## manipulations of the xml file C:\ProgramData\IVI Foundation\IVI\IviConfigurationStore.xml
## via the Ivi.ConfigServer.Interop assembly
##================================================
import os
import sys
import clr
import xml.etree.ElementTree as ET
conf_file = os.path.join(os.path.split(__file__)[0],"conf.xml")

class myElement(object):
    def __init__(self,element):
        self._element = element
        
    def __getattr__(self,name):
        if name in dir(super(myElement,self)):
            return super(myElement,self).__getattr__(name)
        ret = self._element.get(name)
        if ret is not None:
            return ret
        for ch in self._element.getchildren():
            if ch.tag == name:
                return myElement(ch)
        raise AttributeError("no attribute " + str(name))
    def __dir__(self):
        return map(lambda x:x.tag,self._element.getchildren()) + self._element.attrib.keys() + dir(super(myElement,self))
    
    def remove(self,tag):
        self._element.remove(self[tag]._element)
        

    def remove_all(self):
        for i in range(len(self._element.getchildren())):
            self._element.remove(self._element.getchildren()[0])

    def sub(self,tag,**kwds):
        """assigns a subelement with the specified tag and attributes as specified in kwds (ex: wrapper = "NA.NA")"""
 #       kwds = all_to_str(kwds)
        ET.SubElement(self._element, self.next_available_tag(tag), kwds)
        return self[tag]
    
    def set(self,**kwds):
        """set (multiple) attribute name-value pairs according to kwds arguments"""
  #      kwds = all_to_str(kwds)
        for k,v in zip(kwds.keys(),kwds.values()):
            self._element.set(k,v)


    def __setitem__(self,k,v):
        self.set(**{k:v})
    
    def __setattr__(self,k,v):
        try:
            attribs = super(myElement,self).__getattribute__("_element").attrib.keys()
        except AttributeError:
            return super(myElement,self).__setattr__(k,v)
        for at in attribs:
            if k == at:
                self[k] = v
        return super(myElement,self).__setattr__(k,v)
    
    @property
    def tag(self):
        return self._element.tag

    def __getitem__(self,i):
        for ch in self._element.getchildren():
            if ch.tag == i:
                return myElement(ch)
        return self._element.attrib[i]
    
    def __iter__(self):
        for i in self._element.getchildren():
            yield myElement(i)
        
    def next_available_tag(self,tag):
        new_tag = tag
        n = 1
        while new_tag in [t.tag for t in self]:
            new_tag = tag + str(n)
            n+=1
        return new_tag
        
            
def default_file(__file__):
    """use this function with argument __file__ to obtained a filename conf.xml
     in the same directory as the source file"""
    return os.path.join(os.path.split(__file__)[0],"conf.xml")

class conf(myElement):
    default_tag = "DEV"
    def serialize(self):
        self._tree.write(self.filename)
    def deserialize(self):
        self._tree = ET.parse(self.filename)
        
    
    
    def _rebuild_tree_from_scratch(self):
        root = ET.Element("root")
        self._tree = ET.ElementTree(root)
        
    
    def __init__(self,filename):
        self.filename = filename
        if os.path.exists(filename):
            try:
                self.deserialize()
            except ET.ParseError:
                print "could not parse the conf.xml file, probably because the file was closed prematurely"
                self._rebuild_tree_from_scratch()
        else:
            print "not file conf.xml found, is it the first time you import the module?"
            self._rebuild_tree_from_scratch()
        self._element = self._tree.getroot()
