from objects import ObjectController
from messages import *
import views.potions
import models.potions

class Item(ObjectController):
   def __init__(self,x,y,use_function=None):
      raise NotImplementedError( "not_implemented" )

   @property
   def who_is_affected(self):
      return self.affects

   def cast(self, player, monsters):
      raise NotImplementedError( "not_implemented" )

class HealingPotion(Item):
   def __init__(self,x,y):
      self.model = models.potions.Potion(x,y)
      self.view = views.potions.HealingPotion(self.model)
      self.use_function = None
      self.range = 0
      self.affects = 'owner'

   def cast(self, player, monsters):
      messages = MessagesBorg()
      messages.add('Your wounds start to feel better!', libtcod.light_violet)
      player.heal(HEAL_AMOUNT)
      return True

class LightningBolt(Item):
   def __init__(self,x,y):
      self.model = models.potions.Potion(x,y)
      self.view = views.potions.LightningBolt(self.model)
      self.range = LIGHTNING_RANGE
      self.affects = 'closest'

   def cast(self, player, monsters):
      messages = MessagesBorg()

      if len(monsters) < 1:
         messages.add('No enemy is close enough to strike.', libtcod.red)
         return 'cancelled'

      for monster in monsters:
         messages.add('A lighting bolt strikes the ' + monster.name + ' with a loud thunder! The damage is '
              + str(LIGHTNING_DAMAGE) + ' hit points.', libtcod.light_blue)
         monster.take_damage(LIGHTNING_DAMAGE)

      return True

class ConfusionScroll(Item):
   def __init__(self,x,y):
      self.model = models.potions.Potion(x,y)
      self.view = views.potions.ConfusionScroll(self.model)
      self.range = CONFUSE_RANGE
      self.affects = 'closest'

   def cast(self, player, monsters):
      messages = MessagesBorg()

      if len(monsters) < 1:
         messages.add('No enemy is close enough to confuse.', libtcod.red)
         return 'cancelled'

      for monster in monsters:
         messages.add('The eyes of the ' + monster.name + ' look vacant, as he starts to stumble around!', libtcod.light_green)
         monster.confuse()

      return True
