import random
from config import *
from objects import *
import libtcodpy as libtcod

color_dark_wall = libtcod.Color(0, 0, 100)
color_light_wall = libtcod.Color(130, 110, 50)
color_dark_ground = libtcod.Color(50, 50, 150)
color_light_ground = libtcod.Color(200, 180, 50)

class Tile:
   #a tile of the map and its properties
   def __init__(self, blocked, block_sight = None):
      self.blocked = blocked
      self.explored = False
 
      #by default, if a tile is blocked, it also blocks sight
      self.block_sight = blocked if block_sight is None else block_sight

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

class LevelModel:
   def __init__(self):
      #fill map with "unblocked" tiles
      self.tiles = [[ Tile(True)
            for y in range(MAP_HEIGHT) ]
            for x in range(MAP_WIDTH) ]

      self.rooms = []
      self.num_rooms = 0

      self.items = []
      self.monsters = []

   def does_room_overlap(self,room):
      #run through the other rooms and see if they intersect with this one
      for other_room in self.rooms:
         if room.intersect(other_room):
            return True

      return False

   def add_room(self, room):
      self.rooms.append(room)
      self.num_rooms += 1

   def get_last_room(self):
      if self.num_rooms == 0:
         return None

      return self.rooms[self.num_rooms-1]


class LevelView:
   def __init__(self,model):
      self.model = model
      self.fov_map = libtcod.map_new(MAP_WIDTH, MAP_HEIGHT)

   def set_fovmap(self):
      for y in range(MAP_HEIGHT):
         for x in range(MAP_WIDTH):
            isTransparent = not self.model.tiles[x][y].block_sight
            isWalkable = not self.model.tiles[x][y].blocked
            libtcod.map_set_properties(self.fov_map, x, y, isTransparent, isWalkable)

   def __draw_items(self,console):
      for item in self.model.items:
         (itemx,itemy) = item.get_position()
         if libtcod.map_is_in_fov(self.fov_map, itemx, itemy):
            item.view.draw(console)

   def __draw_monsters(self,console,draw_dead=False):
      #go through all monsters
      for monster in self.model.monsters:
         (monsterx,monstery) = monster.get_position()
         if libtcod.map_is_in_fov(self.fov_map, monsterx, monstery):
            if ((draw_dead == True and monster.has_died() == True) or
               (draw_dead == False and monster.has_died() == False)):
               monster.view.draw(console)

   def draw(self,console):
      #go through all tiles, and set their background color
      for y in range(MAP_HEIGHT):
         for x in range(MAP_WIDTH):
            wall = self.model.tiles[x][y].block_sight
            visible = libtcod.map_is_in_fov(self.fov_map, x, y)

            if visible:
               if wall:
                  libtcod.console_set_char_background(console, x, y, color_light_wall, libtcod.BKGND_SET )
               else:
                  libtcod.console_set_char_background(console, x, y, color_light_ground, libtcod.BKGND_SET )
            else:
               if self.model.tiles[x][y].explored is True:
                  if wall:
                     libtcod.console_set_char_background(console, x, y, color_dark_wall, libtcod.BKGND_SET )
                  else:
                     libtcod.console_set_char_background(console, x, y, color_dark_ground, libtcod.BKGND_SET )

      self.__draw_items(console)
      # start by drawing the monsters that have died
      self.__draw_monsters(console,True)
      self.__draw_monsters(console,False)

class LevelController:
   def __init__(self):
      self.model = LevelModel()
                                
      self.view = LevelView(self.model)

      for r in range(MAX_ROOMS):
         new_room = self.__build_complete_room()

         if new_room is not None:
            #append the new room to the list
            self.model.add_room(new_room)

      self.view.set_fovmap()

   def __create_room(self,room):
      #go through the tiles in the rectangle and make them passable
      for x in range(room.x1, room.x2):
         for y in range(room.y1, room.y2):
            self.model.tiles[x][y].blocked = False
            self.model.tiles[x][y].block_sight = False

   def __create_h_tunnel(self, x1, x2, y):
      x, w = min(x1,x2), abs(x1-x2)+1
      room = Rect(x,y,w,1)
      self.__create_room(room)

   def __create_v_tunnel(self, y1, y2, x):
      y, h = min(y1,y2), abs(y1-y2)+1
      room = Rect(x,y,1,h)
      self.__create_room(room)

   def __connect_rooms(self,center1,center2): 
      (center1x, center1y) = center1
      (center2x, center2y) = center2

      #draw a coin (random number that is either 0 or 1)
      if random.choice([True, False]):
         #first move horizontally, then vertically
         self.__create_h_tunnel(center1x, center2x, center1y)
         self.__create_v_tunnel(center1y, center2y, center2x)
      else:
         #first move vertically, then horizontally
         self.__create_v_tunnel(center1y, center2y, center1x)
         self.__create_h_tunnel(center1x, center2x, center2y)

   def __place_monsters_in_room(self,room):
       #choose random number of monsters
       num_monsters = random.randint(0, MAX_ROOM_MONSTERS)
    
       for i in range(num_monsters):
           #choose random spot for this monster
           x = random.randint(room.x1+1, room.x2-1)
           y = random.randint(room.y1+1, room.y2-1)
    
           if not self.is_blocked((x,y)):
              if random.randint(0, 100) < 80:  #80% chance of getting an orc
                  monster = Orc(x,y)
              else:
                  monster = Troll(x,y)
       
              self.model.monsters.append(monster)

   def __place_items_in_room(self,room):
      #choose random number of items
      num_items = libtcod.random_get_int(0, 0, MAX_ROOM_ITEMS)

      for i in range(num_items):
         #choose random spot for this item
         x = random.randint(room.x1+1, room.x2-1)
         y = random.randint(room.y1+1, room.y2-1)

         #only place it if the tile is not blocked
         if not self.is_blocked((x,y)):
            dice = libtcod.random_get_int(0, 0, 100)
            if dice < 70:
               item = HealingPotion(x,y)
            else:
               item = LightningBolt(x,y,self.view.fov_map)


            self.model.items.append(item)

   def __build_complete_room(self):
      #random width and height
      w = random.randint(ROOM_MIN_SIZE, ROOM_MAX_SIZE)
      h = random.randint(ROOM_MIN_SIZE, ROOM_MAX_SIZE)
      #random position without going out of the boundaries of the map
      x = random.randint(1, MAP_WIDTH - w - 1)
      y = random.randint(1, MAP_HEIGHT - h - 1)
 
      #"Rect" class makes rectangles easier to work with
      new_room = Rect(x, y, w, h)
 
      #check if there are no intersections, so this room is valid
      if self.model.does_room_overlap(new_room):
         return None

      #"paint" it to the map's tiles
      self.__create_room(new_room)
      self.__place_items_in_room(new_room)
      self.__place_monsters_in_room(new_room)

      #connect all rooms but the first to the previous room with a tunnel
      prev_room = self.model.get_last_room()
      if prev_room is not None:
         prev_center = prev_room.center()
         new_center = new_room.center()
         self.__connect_rooms(prev_center,new_center)

      return new_room

   def update(self,pos):
      x, y = pos
      libtcod.map_compute_fov(self.view.fov_map, x, y, TORCH_RADIUS, FOV_LIGHT_WALLS, FOV_ALGO)

      for y in range(MAP_HEIGHT):
         for x in range(MAP_WIDTH):
            if libtcod.map_is_in_fov(self.view.fov_map, x, y):
               self.model.tiles[x][y].explored = True

   def is_blocked(self, pos):
      x, y = pos

      #first test the map tile
      if self.model.tiles[x][y].blocked:
         return True
    
      #now check for any blocking monsters
      for monster in self.model.monsters:
         if monster.blocks() and monster.get_position() == pos:
            return True
    
      return False

   def get_unblocked_pos(self):
     #choose random spot
     x = random.randint(1, MAP_WIDTH - 1)
     y = random.randint(1, MAP_HEIGHT - 1)

     if not self.is_blocked((x,y)):
        return (x,y)

     return self.get_unblocked_pos()
