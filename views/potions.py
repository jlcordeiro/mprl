from objects import ObjectView
import libtcodpy as libtcod

class Potion(ObjectView):
   def __init__(self,model,colour):
      super(Potion, self).__init__(model, '!', colour)

class HealingPotion(Potion):
   def __init__(self,model):
      super(HealingPotion, self).__init__(model,libtcod.violet)

