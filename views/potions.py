from objects import ObjectView
import libtcodpy as libtcod

class Potion(ObjectView):
   def __init__(self,model):
      super(Potion, self).__init__(model, '!', libtcod.violet)

