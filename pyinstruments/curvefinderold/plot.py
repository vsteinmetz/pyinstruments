"""
Utility module to directly save arrays in db...
"""

from models import CurveDB
from pandas import Series

def curve(*args, **kwds):
    """
    returns a curve with the array provided
    arguments:
        x, y or y only
    """
    if len(args)==0:
        raise TypeError('at least one argument required')
    
    if len(args)==2:
        x, y = args
    if len(args)==1:
        y = args[0]
        x = range(len(y))
    curve = CurveDB(data=Series(y, index=x))
    return curve


def plot(*args, **kwds):
    """
    saves a curve with the array provided
    arguments:
        x, y or y only
    """
    cur = curve(*args, **kwds)
    cur.save()
    cur.tags_txt = ["plot"]
    cur.save()