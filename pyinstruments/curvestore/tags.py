from pyinstruments.curvestore.models import Tag, top_level_tags

class HierarchicalTag(object): 
    def __init__(self, name, parent=None): 
        self.name = name
#        self.state = state 
#        self.description = description

        self.parent = parent 
        self.children = [] 

        self.setParent(parent)

    def add_child(self, name):
        if self.fullname == "":
            tag, new = Tag.objects.get_or_create(name=name)
        else:
            tag, new = self.model_tag().add_child(name)
        if new:
            HierarchicalTag(name, parent=self)
        else:
            raise ValueError('A tag with name '+ name + ' already exists there')
        
    def remove(self):
        self.model_tag().remove()
#        self.parent.children.remove()
        

    def rename(self, new_name):
        self.model_tag().set_shortname(new_name)
        self.name = new_name

    def move(self, new_parent):
        self.model_tag().move(new_parent.fullname)  
        self.parent.children.remove(self)
        self.setParent(new_parent)

    def __repr__(self):
        return 'HTag:' + self.fullname

    @property
    def fullname(self):
        node = self
        l = []
        while node.parent:
            l.append(node.name)
            node = node.parent
        l.reverse()
        fullname = ''
        for name in l:
            fullname+= '/' + name
        return str(fullname[1:])
        
    def model_tag(self):
        return Tag.objects.get(name=self.fullname)
        
    def build_children_from_model(self):
        if self.fullname=='':
            model_childs = top_level_tags()
        else:
            model_childs = self.model_tag().childs()
        
        self.remove_all_children()
        for model_child in model_childs:
            node = HierarchicalTag(model_child.shortname, parent=self)
            node.build_children_from_model()
            
    def setParent(self, parent): 
        if parent != None: 
            self.parent = parent 
            self.parent.appendChild(self)
        else: 
            self.parent = None

    def appendChild(self, child): 
        self.children.append(child) 

    def childAtRow(self, row): 
        return self.children[row] 

    def rowOfChild(self, child):       
        for i, item in enumerate(self.children): 
            if item == child: 
                return i 
        return -1
    
    def remove_all_children(self):
        """
        recursively removes all children
        """
        
        to_remove = []
        for ch in self.children:
            ch.remove_all_children()
        self.children = []

    def removeChild(self, row): 
        value = self.children[row] 
        self.children.remove(value) 
        return True 

    def __len__(self): 
        return len(self.children)
    
ROOT = HierarchicalTag("")
