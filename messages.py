import textwrap
import libtcod.libtcodpy as libtcod

class Messages:
   def __init__(self,max_width,max_rows=1):
      self.game_msgs = []
      self.max_rows = max_rows
      self.max_width = max_width
 
   def add(self, new_msg, color = libtcod.white):
       #split the message if necessary, among multiple lines
       new_msg_lines = textwrap.wrap(new_msg, self.max_width)
    
       for line in new_msg_lines:
           #if the buffer is full, remove the first line to make room for the new one
           if len(self.game_msgs) == self.max_rows:
               del self.game_msgs[0]
    
           #add the new line as a tuple, with the text and the color
           self.game_msgs.append( (line, color) )

   def draw(self,panel,x):
      y = 1
      for (line, color) in self.game_msgs:
         libtcod.console_set_default_foreground(panel, color)
         libtcod.console_print_ex(panel, x, y, libtcod.BKGND_NONE, libtcod.LEFT,line)
         y += 1
