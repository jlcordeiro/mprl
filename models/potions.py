from objects import ObjectModel

class Potion(ObjectModel):
   def __init__(self,x,y):
      super(Potion, self).__init__(x,y,False)
