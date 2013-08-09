"""
Some utilities to list drivers are listed here
"""

from collections import OrderedDict

def class_to_str(cls):
    """serializes the class name + module name"""
    return cls.__module__ + "." + cls.__name__

def _list_all_child_classes(parent, dictionnary):
    """function to be called in the recursive loop (private)"""
    depth = []
    for i, cls in enumerate(parent.__subclasses__()):
        depth.append(_list_all_child_classes(cls, dictionnary))
    #for i,cl in enumerate(parent.__subclasses__()):
        dictionnary[""*depth[i] + class_to_str(cls)] = cls
    if len(depth)>0:
        maxdepth = max(depth) + 1
    else:
        maxdepth = 0
    return maxdepth


def list_all_child_classes(parent):
    """returns an ordered dictionnary d with d[class_name] = class.
    The classes are ordered in a depth-first-search way"""
    dictionnary = OrderedDict()
    _list_all_child_classes(parent, dictionnary)
    #d = invert_leading_spaces(d)
    return dictionnary