from objects import ObjectModel

class Potion(ObjectModel):
   def __init__(self,x,y,range,affects):
      super(Potion, self).__init__(x,y,False)
      self.range = range
      self.affects = affects
