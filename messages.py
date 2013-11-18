import textwrap
import libtcodpy as libtcod
from config import *

class GameMessages:
   def __init__(self):
      self.msgs = []

   def add(self, new_msg, color = libtcod.white):
      #split the message if necessary, among multiple lines
      new_msg_lines = textwrap.wrap(new_msg, MSG_WIDTH)
       
      for line in new_msg_lines:
         #if the buffer is full, remove the first line to make room for the new one
         if len(self.msgs) == MSG_HEIGHT:
            del self.msgs[0]
                               
         #add the new line as a tuple, with the text and the color
         self.msgs.append( (line, color) )

   def get_all(self):
      return self.msgs

global_msgs = GameMessages()
