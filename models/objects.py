
last_uid = 0

def get_uid():
   global last_uid
   last_uid += 1
   return last_uid

class ObjectModel(object):
   def __init__(self,name,x,y,blocks):
      self.x = x
      self.y = y
      self.name = name
      self.blocks = blocks

      self.uid = str(get_uid())

