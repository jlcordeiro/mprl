import math
import random
import libtcodpy as libtcod
from messages import *
import controllers.objects

import views.potions
import views.creatures
import models.potions
import models.creatures

def move_towards_creature(one, other, method_check_blocks):
   (x1, y1) = one.position
   (x2, y2) = other.position

   #return the distance to another object
   distance = one.distance_to(other)
    
   #normalize it to length 1 (preserving direction), then round it and
   #convert to integer so the movement is restricted to the map grid
   dx = int(round((x2 - x1) / distance))
   dy = int(round((y2 - y1) / distance))

   if method_check_blocks((x1+dx,y1+dy)) == False:
      one.move(dx, dy)
 
def take_turn( monster, player, method_check_blocks ):
   if monster.died:
      return

   messages = MessagesBorg()
   if monster.confused_turns > 0:
      messages.add('The ' + monster.name + ' is confused!', libtcod.red)

      (xi, yi) = monster.position
      final_pos = ( xi+random.randint(-1, 1), yi+random.randint(-1, 1))

      if method_check_blocks( final_pos ) == False:
         owner.move(dx, dy)

      monster.confused_turns -= 1
      
      if monster.confused_turns == 0:
         messages.add('The ' + self.name + ' is no longer confused!', libtcod.red)

   else:
      #move towards player if far away
      if monster.distance_to(player) >= 2:
         move_towards_creature(monster,player,method_check_blocks)
      #close enough, attack! (if the player is still alive.)
      elif player.model.hp > 0:
         monster.attack(player)


class Item(controllers.objects.ObjectController):
   def __init__(self,x,y,use_function=None):
      raise NotImplementedError( "not_implemented" )

   def update(self, player, monsters):
      pass

   def use(self):
      self.use_function()
      return True

def closest_monster(fov_map,player,monsters,max_range):
   #find closest enemy, up to a maximum range, and in the player's FOV
   closest_enemy = None
   closest_dist = max_range + 1  #start with (slightly more than) maximum range

   for monster in monsters:
      x,y = monster.position
      if libtcod.map_is_in_fov(fov_map, x, y):
          #calculate distance between this object and the player
          dist = monster.distance_to(player)
          if dist < closest_dist:  #it's closer, so remember it
             closest_enemy = monster
             closest_dist = dist
   return closest_enemy

def cast_heal(creature):
   messages = MessagesBorg()
   messages.add('Your wounds start to feel better!', libtcod.light_violet)
   creature.heal(HEAL_AMOUNT)

def cast_lightning(monster):
   messages = MessagesBorg()
   messages.add('A lighting bolt strikes the ' + monster.name + ' with a loud thunder! The damage is '
        + str(LIGHTNING_DAMAGE) + ' hit points.', libtcod.light_blue)
   monster.take_damage(LIGHTNING_DAMAGE)

def cast_confuse(monster):
   messages = MessagesBorg()
   messages.add('The eyes of the ' + monster.name + ' look vacant, as he starts to stumble around!', libtcod.light_green)
   monster.confuse()

class HealingPotion(Item):
   def __init__(self,x,y):
      self.model = models.potions.Potion(x,y)
      self.view = views.potions.HealingPotion(self.model)
      self.use_function = None

   def update(self, player, monsters):
      self.use_function = lambda: cast_heal(player)

class LightningBolt(Item):
   def __init__(self,x,y,fov_map):
      self.model = models.potions.Potion(x,y)
      self.view = views.potions.LightningBolt(self.model)
      self.use_function = None
      self.fov_map = fov_map

   def update(self, player, monsters):

      #find closest enemy (inside a maximum range) and damage it
      monster = closest_monster(self.fov_map,player,monsters,LIGHTNING_RANGE)
      if monster is None:
         messages.add('No enemy is close enough to strike.', libtcod.red)
         return 'cancelled'

      self.use_function = lambda: cast_lightning(monster)


class ConfusionScroll(Item):
   def __init__(self,x,y,fov_map):
      self.model = models.potions.Potion(x,y)
      self.view = views.potions.ConfusionScroll(self.model)
      self.use_function = None
      self.fov_map = fov_map

   def update(self, player, monsters):

      #find closest enemy (inside a maximum range) and damage it
      monster = closest_monster(self.fov_map,player,monsters,CONFUSE_RANGE)
      if monster is None:
         messages.add('No enemy is close enough to confuse.', libtcod.red)
         return 'cancelled'

      self.use_function = lambda: cast_confuse(monster)
