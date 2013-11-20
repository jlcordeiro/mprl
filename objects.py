import math
import libtcodpy as libtcod
from messages import *

last_uid = 0

def get_uid():
   global last_uid
   last_uid += 1
   return last_uid

class ObjectModel(object):
   def __init__(self,x,y,blocks):
      self.x = x
      self.y = y
      self.blocks = blocks

      self.uid = str(get_uid())

class CreatureModel(ObjectModel):
   def __init__(self,x,y,hp,defense,power):
      super(CreatureModel, self).__init__(x,y,True)
      self.max_hp = hp
      self.hp = hp
      self.defense = defense
      self.power = power

class ObjectView():
   def __init__(self,model,char,colour):
      self.model = model
      self.char = char
      self.colour = colour

   def draw(self,console):
      #set the colour and then draw the character that represents this object at its position
      libtcod.console_set_default_foreground(console, self.colour)
      libtcod.console_put_char(console, self.model.x, self.model.y, self.char, libtcod.BKGND_NONE)

   def clear(self,console):
      #erase the character that represents this object
      libtcod.console_put_char(console, self.model.x, self.model.y, ' ', libtcod.BKGND_NONE)

class ObjectController(object):
   def __init__(self,x,y,char,colour,blocks=False):
      self.model = ObjectModel(x,y,blocks)
      self.view = ObjectView(self.model,char,colour)

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
   def __init__(self, x, y, hp, defense, power, char, colour, ai=None):
      self.model = CreatureModel(x,y,hp,defense,power)
      self.view = ObjectView(self.model,char,colour)
      self.ai = ai

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
      super(Player, self).__init__(x,y,30,2,5,'@',libtcod.white)
      self.inventory = []

   def pick_item(self,item):
      #add to the player's inventory and remove from the map
      messages = MessagesBorg()
      if len(self.inventory) >= 26:
         messages.add('Your inventory is full, cannot pick up ' + item.name + '.', libtcod.red)
         return False
      
      self.inventory.append(item)
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
      ai = BasicMonsterAI()
      super(Orc, self).__init__(x,y,10,0,3,'O',libtcod.desaturated_green,ai)

class Troll(CreatureController):
   def __init__(self,x,y):
      ai = BasicMonsterAI()
      super(Troll, self).__init__(x,y,16,1,4,'T',libtcod.darker_green,ai)

class HealingPotion(ObjectController):
   def __init__(self,x,y):
      super(HealingPotion, self).__init__(x,y, '!', libtcod.violet)
