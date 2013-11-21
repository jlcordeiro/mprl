import math
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

class CreatureController(ObjectController):
   #combat-related properties and methods (monster, player, NPC).
   def __init__(self):
      self.model = None
      self.view = None
      self.ai = None

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

   def pick_item(self,item):
      #add to the player's inventory and remove from the map
      messages = MessagesBorg()
      if len(self.model.inventory) >= 26:
         messages.add('Your inventory is full, cannot pick up ' + item.name + '.', libtcod.red)
         return False
      
      self.model.inventory.append(item)
      item.update(self)
      messages.add('You picked up a ' + item.name + '!', libtcod.green)
      return True

class BasicMonsterAI():
   #AI for a basic monster.
   def take_turn(self,owner,player,method_check_blocks):
      #move towards player if far away
      if owner.distance_to_creature(player) >= 2:
         owner.move_towards_creature(player,method_check_blocks)
      #close enough, attack! (if the player is still alive.)
      elif player.model.hp > 0:
         owner.attack(player)

class Orc(CreatureController):
   def __init__(self,x,y):
      self.model = models.creatures.Orc(x,y)
      self.view = views.creatures.Orc(self.model)
      self.ai = BasicMonsterAI()

class Troll(CreatureController):
   def __init__(self,x,y):
      self.model = models.creatures.Troll(x,y)
      self.view = views.creatures.Troll(self.model)
      self.ai = BasicMonsterAI()

class Item(ObjectController):
   def __init__(self,x,y,use_function=None):
      self.model = models.potions.Potion(x,y)
      self.view = views.potions.Potion(self.model)
      self.use_function = use_function

   def use(self):
      self.use_function()
      return True

def cast_heal(creature):
   messages = MessagesBorg()
   messages.add('Your wounds start to feel better!', libtcod.light_violet)
   creature.heal(HEAL_AMOUNT)

class HealingPotion(Item):
   def __init__(self,x,y):
      super(HealingPotion, self).__init__(x,y)

   def update(self, owner):
      self.use_function = lambda: cast_heal(owner)
