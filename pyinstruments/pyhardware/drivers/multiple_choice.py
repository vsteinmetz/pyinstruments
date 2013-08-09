class MultipleChoice(object):
    """
    a class to choose amongst multiple choices
    """
    
    def __init__(self, parent, attr_name, **kwds):
        for key, value in kwds.iteritems():
            setattr(self, key, value)
            
        self.choices = kwds