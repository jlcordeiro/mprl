
class Object(object):
   def __init__(self,x,y):
      self.x = x
      self.y = y

class Player(Object):
   def __init__(self,x,y):
      super(Player, self).__init__(x,y)
