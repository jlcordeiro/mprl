from objects import ObjectModel

class Potion(ObjectModel):
   def __init__(self,x,y,use_function=None):
      super(Potion, self).__init__(x,y,False)
      self.use_function = use_function
