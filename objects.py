import libtcodpy as libtcod

class ObjectModel():
   def __init__(self,x,y):
      self.x = x
      self.y = y

class ObjectView():
   def __init__(self,model,char,colour):
      self.model = model
      self.char = char
      self.colour = colour

   def draw(self,console):
      #set the colour and then draw the character that represents this object at its position
      libtcod.console_set_default_foreground(console, self.colour)
      libtcod.console_put_char(console, self.model.x, self.model.y, self.char, libtcod.BKGND_NONE)

   def clear(self,console):
      #erase the character that represents this object
      libtcod.console_put_char(console, self.model.x, self.model.y, ' ', libtcod.BKGND_NONE)

class ObjectController(object):
   def __init__(self,x,y,char,colour):
      self.model = ObjectModel(x,y)
      self.view = ObjectView(self.model,char,colour)

   def move(self,dx,dy):
      self.model.x += dx
      self.model.y += dy

class Player(ObjectController):
   def __init__(self,x,y):
      super(Player, self).__init__(x,y,'@',libtcod.white)

   def get_position(self):
      return (self.model.x,self.model.y)
