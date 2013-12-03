from objects import ObjectView
import libtcodpy as libtcod

class Potion(ObjectView):
   def __init__(self,model,colour):
      super(Potion, self).__init__(model, '!', colour)

class HealingPotion(Potion):
   def __init__(self,model):
      super(HealingPotion, self).__init__(model,libtcod.violet)

class LightningBolt(Potion):
   def __init__(self,model):
      super(LightningBolt, self).__init__(model,libtcod.light_yellow)

class ConfusionScroll(Potion):
   def __init__(self,model):
      super(ConfusionScroll, self).__init__(model,libtcod.light_green)

#TODO" Fireball
