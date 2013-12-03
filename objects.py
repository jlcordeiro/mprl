import math
import random
import libtcodpy as libtcod
from messages import *
import views.potions
import views.creatures
import models.potions
import models.creatures

class ObjectController(object):
   def __init__(self):
      self.model = None
      self.view = None

   def move(self,dx,dy):
      self.model.x += dx
      self.model.y += dy

   def get_position(self):
      return (self.model.x,self.model.y)

   def blocks(self):
      return self.model.blocks

   @property
   def name(self):
      return self.view.char

class BasicMonsterAI():
   #AI for a basic monster.
   def take_turn(self,owner,player,method_check_blocks):
      #move towards player if far away
      if owner.distance_to_creature(player) >= 2:
         owner.move_towards_creature(player,method_check_blocks)
      #close enough, attack! (if the player is still alive.)
      elif player.model.hp > 0:
         owner.attack(player)

class ConfusedMonsterAI():
    #AI for a confused monster.
    def take_turn(self,owner,method_check_blocks):
      #move in a random direction
      (x, y) = owner.get_position()
      (dx, dy) = (random.randint(-1, 1), random.randint(-1, 1))
       
      if method_check_blocks((x+dx,y+dy)) == False:
         owner.move(dx, dy)

class CreatureController(ObjectController):
   #combat-related properties and methods (monster, player, NPC).
   def __init__(self):
      self.model = None
      self.view = None
      self.ai = None
      self.confused_ai = None
      self.confused_turns = 0

   def confuse(self):
      self.confused_turns = CONFUSE_NUM_TURNS 
      
   def take_turn( self, player, method_check_blocks ):
      messages = MessagesBorg()
      if self.confused_turns > 0 and self.confused_ai is not None:
         messages.add('The ' + self.name + ' is still confused!', libtcod.red)
         self.confused_ai.take_turn( self, method_check_blocks )
         self.confused_turns -= 1
         
         if self.confused_turns == 0:
            messages.add('The ' + self.name + ' is no longer confused!', libtcod.red)
            
      else:
         self.ai.take_turn(self, player, method_check_blocks)

   def move_towards_creature(self, other, method_check_blocks):
      (x, y) = self.get_position()
      (target_x, target_y) = other.get_position()

      #return the distance to another object
      (dx, dy) = (target_x - x, target_y - y)
      distance = math.sqrt(dx ** 2 + dy ** 2)
       
      #normalize it to length 1 (preserving direction), then round it and
      #convert to integer so the movement is restricted to the map grid
      dx = int(round(dx / distance))
      dy = int(round(dy / distance))

      if method_check_blocks((x+dx,y+dy)) == False:
         self.move(dx, dy)

   def distance_to_creature(self, other):
      (target_x,target_y) = other.get_position()

      #return the distance to another object
      dx = target_x - self.model.x
      dy = target_y - self.model.y
      return math.sqrt(dx ** 2 + dy ** 2)

   def take_damage(self, damage):
      #apply damage if possible
      if damage > 0:
         self.model.hp -= damage

      if self.model.hp <= 0:
         self.die()

   def attack(self, target):
      #a simple formula for attack damage
      damage = self.model.power - target.model.defense
                         
      messages = MessagesBorg()
      if damage > 0:
         #make the target take some damage
         messages.add(self.model.uid + ' attacks ' + target.model.uid + ' for ' + str(damage) + ' hit points.')
         target.take_damage(damage)
      else:
         messages.add(self.model.uid + ' attacks ' + target.model.uid + ' but it has no effect!')

   def heal(self, amount):
      #heal by the given amount, without going over the maximum
      self.model.hp += amount
      if self.model.hp > self.model.max_hp:
         self.model.hp = self.model.max_hp

   def die(self):
      #transform it into a nasty corpse! it doesn't block, can't be
      #attacked and doesn't move
      messages = MessagesBorg()
      messages.add(self.model.uid + ' is dead!',libtcod.white)
      self.ai = None
      self.view.char = '%'
      self.model.blocks = False
      self.model.uid += " (dead)"

   def has_died(self):
      return (self.model.hp <= 0)

class Player(CreatureController):
   def __init__(self,x,y):
      self.model = models.creatures.Player(x,y)
      self.view = views.creatures.Player(self.model)
      self.ai = None
      self.confused_ai = None
      self.confused_turns = 0

   def pick_item(self,item):
      #add to the player's inventory and remove from the map
      messages = MessagesBorg()
      if len(self.model.inventory) >= 26:
         messages.add('Your inventory is full, cannot pick up ' + item.name + '.', libtcod.red)
         return False
      
      self.model.inventory.append(item)
      messages.add('You picked up a ' + item.name + '!', libtcod.green)
      return True

   def drop_item(self,item):
      #add to the map and remove from the player's inventory. also, place it at the player's coordinates
      self.model.inventory.remove(item)
      item.model.x = self.model.x
      item.model.y = self.model.y

      messages = MessagesBorg()
      messages.add('You dropped a ' + item.name + '.', libtcod.yellow)

class Orc(CreatureController):
   def __init__(self,x,y):
      self.model = models.creatures.Orc(x,y)
      self.view = views.creatures.Orc(self.model)
      self.ai = BasicMonsterAI()
      self.confused_ai = ConfusedMonsterAI()
      self.confused_turns = 0

class Troll(CreatureController):
   def __init__(self,x,y):
      self.model = models.creatures.Troll(x,y)
      self.view = views.creatures.Troll(self.model)
      self.ai = BasicMonsterAI()
      self.confused_ai = ConfusedMonsterAI()
      self.confused_turns = 0

class Item(ObjectController):
   def __init__(self,x,y,use_function=None):
      pass

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
      x,y = monster.get_position()
      if libtcod.map_is_in_fov(fov_map, x, y):
          #calculate distance between this object and the player
          dist = player.distance_to_creature(monster)
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
