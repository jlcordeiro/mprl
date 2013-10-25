import random
import libtcod.libtcodpy as libtcod
from ai import *
from config import *
from objects import *
  
def random_choice(chances_dict):
    #choose one option from dictionary of chances, returning its key
    chances = chances_dict.values()
    strings = chances_dict.keys()
 
    return strings[random_choice_index(chances)]
 
def random_choice_index(chances):  #choose one option from list of chances, returning its index
    #the dice will land on some number between 1 and the sum of the chances
    dice = random.randint( 1, sum(chances))
 
    #go through all chances, keeping the sum so far
    running_sum = 0
    choice = 0
    for w in chances:
        running_sum += w
 
        #see if the dice landed in the part that corresponds to this choice
        if dice <= running_sum:
            return choice
        choice += 1

class Tile:
    #a tile of the map and its properties
    def __init__(self, blocked, block_sight = None):
        self.blocked = blocked
 
        #all tiles start unexplored
        self.explored = False
 
        #by default, if a tile is blocked, it also blocks sight
        if block_sight is None: block_sight = blocked
        self.block_sight = block_sight
 
class Rect:
    #a rectangle on the map. used to characterize a room.
    def __init__(self, x, y, w, h):
        self.x1 = x
        self.y1 = y
        self.x2 = x + w
        self.y2 = y + h
 
    def center(self):
        center_x = (self.x1 + self.x2) / 2
        center_y = (self.y1 + self.y2) / 2
        return (center_x, center_y)
 
    def intersect(self, other):
        #returns true if this rectangle intersects with another one
        return (self.x1 <= other.x2 and self.x2 >= other.x1 and
                self.y1 <= other.y2 and self.y2 >= other.y1)

class Dungeon:
   def __init__(self,level):
    
       #fill map with "blocked" tiles
       self.map = [[ Tile(True)
                   for y in range(MAP_HEIGHT) ]
                   for x in range(MAP_WIDTH) ]
    
       self.level = level
       self.rooms = []
       self.num_rooms = 0
       self.objects = []

   def is_blocked(self, x, y):
       #first test the map tile
       if self.map[x][y].blocked:
           return True
    
       #now check for any blocking objects
       for object in self.objects:
           if object.blocks and object.x == x and object.y == y:
               return True
    
       return False
    
   def create_room(self, room):
       #go through the tiles in the rectangle and make them passable
       for x in range(room.x1 + 1, room.x2):
           for y in range(room.y1 + 1, room.y2):
               self.map[x][y].blocked = False
               self.map[x][y].block_sight = False
    
   def create_h_tunnel(self, x1, x2, y):
       #horizontal tunnel. min() and max() are used in case x1>x2
       for x in range(min(x1, x2), max(x1, x2) + 1):
           self.map[x][y].blocked = False
           self.map[x][y].block_sight = False
    
   def create_v_tunnel(self, y1, y2, x):
       #vertical tunnel
       for y in range(min(y1, y2), max(y1, y2) + 1):
           self.map[x][y].blocked = False
           self.map[x][y].block_sight = False
    
   def make_map(self, player):
    
       #the list of objects with just the player
       self.objects.append(player)
    
       for r in range(MAX_ROOMS):
           #random width and height
           w = random.randint( ROOM_MIN_SIZE, ROOM_MAX_SIZE)
           h = random.randint( ROOM_MIN_SIZE, ROOM_MAX_SIZE)
           #random position without going out of the boundaries of the map
           x = random.randint( 0, MAP_WIDTH - w - 1)
           y = random.randint( 0, MAP_HEIGHT - h - 1)
    
           #"Rect" class makes rectangles easier to work with
           new_room = Rect(x, y, w, h)
    
           #run through the other rooms and see if they intersect with this one
           failed = False
           for other_room in self.rooms:
               if new_room.intersect(other_room):
                   failed = True
                   break
    
           if not failed:
               #this means there are no intersections, so this room is valid
    
               #"paint" it to the map's tiles
               self.create_room(new_room)
    
               #add some contents to this room, such as monsters
               self.generate_objects(new_room)
    
               #center coordinates of new room, will be useful later
               (new_x, new_y) = new_room.center()
    
               if self.num_rooms == 0:
                   #this is the first room, where the player starts at
                   player.x = new_x
                   player.y = new_y
               else:
                   #all rooms after the first:
                   #connect it to the previous room with a tunnel
    
                   #center coordinates of previous room
                   (prev_x, prev_y) = self.rooms[self.num_rooms-1].center()
    
                   #draw a coin (random number that is either 0 or 1)
                   if random.randint( 0, 1) == 1:
                       #first move horizontally, then vertically
                       self.create_h_tunnel(prev_x, new_x, prev_y)
                       self.create_v_tunnel(prev_y, new_y, new_x)
                   else:
                       #first move vertically, then horizontally
                       self.create_v_tunnel(prev_y, new_y, prev_x)
                       self.create_h_tunnel(prev_x, new_x, new_y)
    
               #finally, append the new room to the list
               self.rooms.append(new_room)
               self.num_rooms += 1
    
       #create stairs at the center of the last room
       self.stairs = Object(new_x, new_y, '<', 'stairs', libtcod.white, always_visible=True)
       self.objects.append(self.stairs)
       self.stairs.send_to_back()  #so it's drawn below the monsters

   def generate_objects(self, room):
    
       (max_monsters, monster_chances, max_items, item_chances) = get_object_chances(self.level)
    
       #choose random number of monsters
       num_monsters = random.randint( 0, max_monsters)
    
       for i in range(num_monsters):
           #choose random spot for this monster
           x = random.randint( room.x1+1, room.x2-1)
           y = random.randint( room.y1+1, room.y2-1)
    
           #only place it if the tile is not blocked
           if not self.is_blocked(x, y):
               ai_component = BasicMonster()

               choice = random_choice(monster_chances)
               if choice == 'orc':
                   #create an orc
                   fighter_component = Fighter(hp=20, defense=0, power=4, xp=35, death_function=monster_death)
    
                   monster = Object(x, y, 'o', 'orc', libtcod.desaturated_green,
                                    blocks=True, fighter=fighter_component, ai=ai_component)
    
               elif choice == 'troll':
                   #create a troll
                   fighter_component = Fighter(hp=30, defense=2, power=8, xp=100, death_function=monster_death)
    
                   monster = Object(x, y, 'T', 'troll', libtcod.darker_green,
                                    blocks=True, fighter=fighter_component, ai=ai_component)
    
               objects.append(monster)
    
       #choose random number of items
       num_items = random.randint( 0, max_items)
    
       for i in range(num_items):
           #choose random spot for this item
           x = random.randint( room.x1+1, room.x2-1)
           y = random.randint( room.y1+1, room.y2-1)
    
           #only place it if the tile is not blocked
           if not self.is_blocked(x, y):
               choice = random_choice(item_chances)
               if choice == 'heal':
                   #create a healing potion
                   item_component = Item(use_function=cast_heal)
                   item = Object(x, y, '!', 'healing potion', libtcod.violet, item=item_component)
    
               elif choice == 'lightning':
                   #create a lightning bolt scroll
                   item_component = Item(use_function=cast_lightning)
                   item = Object(x, y, '#', 'scroll of lightning bolt', libtcod.light_yellow, item=item_component)
    
               elif choice == 'fireball':
                   #create a fireball scroll
                   item_component = Item(use_function=cast_fireball)
                   item = Object(x, y, '#', 'scroll of fireball', libtcod.light_yellow, item=item_component)
    
               elif choice == 'confuse':
                   #create a confuse scroll
                   item_component = Item(use_function=cast_confuse)
                   item = Object(x, y, '#', 'scroll of confusion', libtcod.light_yellow, item=item_component)
    
               elif choice == 'sword':
                   #create a sword
                   equipment_component = Equipment(slot='right hand', power_bonus=3)
                   item = Object(x, y, '/', 'sword', libtcod.sky, equipment=equipment_component)
    
               elif choice == 'shield':
                   #create a shield
                   equipment_component = Equipment(slot='left hand', defense_bonus=1)
                   item = Object(x, y, '[', 'shield', libtcod.darker_orange, equipment=equipment_component)
    
               objects.append(item)
               item.send_to_back()  #items appear below other objects
               item.always_visible = True  #items are visible even out-of-FOV, if in an explored area
