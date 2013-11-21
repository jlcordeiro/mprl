import libtcodpy as libtcod

class ObjectView(object):
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

