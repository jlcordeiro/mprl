import math

class ObjectController(object):
   def __init__(self):
      raise NotImplementedError( "not_implemented" )
      
   def move(self,dx,dy):
      self.model.x += dx
      self.model.y += dy

   @property
   def position(self):
      return (self.model.x,self.model.y)

   @property
   def blocks(self):
      return self.model.blocks

   @property
   def name(self):
      return self.view.char

   def distance_to(self,obj2):
      (x1, y1) = self.position
      (x2, y2) = obj2.position

      #return the distance to another object
      (dx, dy) = ( x2 - x1, y2 - y1 )
      return math.sqrt(dx ** 2 + dy ** 2)

