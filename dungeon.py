import random
import libtcodpy as libtcod

MAP_WIDTH = 80
MAP_HEIGHT = 45
ROOM_MAX_SIZE = 10
ROOM_MIN_SIZE = 6
MAX_ROOMS = 30

color_dark_wall = libtcod.Color(0, 0, 100)
color_dark_ground = libtcod.Color(50, 50, 150)


class Tile:
   #a tile of the map and its properties
   def __init__(self, blocked, block_sight = None):
      self.blocked = blocked
 
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
      self.grid = [[ Tile(True)
            for y in range(MAP_HEIGHT) ]
            for x in range(MAP_WIDTH) ]

      self.rooms = []
      self.num_rooms = 0

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

   def draw(self,console):
      #go through all tiles, and set their background color
      for y in range(MAP_HEIGHT):
         for x in range(MAP_WIDTH):
            wall = self.model.grid[x][y].block_sight
            if wall:
               libtcod.console_set_char_background(console, x, y, color_dark_wall, libtcod.BKGND_SET )
            else:
               libtcod.console_set_char_background(console, x, y, color_dark_ground, libtcod.BKGND_SET )

class LevelController:
   def __init__(self):
      self.model = LevelModel()
      self.view = LevelView(self.model)
                                
      for r in range(MAX_ROOMS):
         #random width and height
         w = random.randint(ROOM_MIN_SIZE, ROOM_MAX_SIZE)
         h = random.randint(ROOM_MIN_SIZE, ROOM_MAX_SIZE)
         #random position without going out of the boundaries of the map
         x = random.randint(0, MAP_WIDTH - w - 1)
         y = random.randint(0, MAP_HEIGHT - h - 1)
    
         #"Rect" class makes rectangles easier to work with
         new_room = Rect(x, y, w, h)
    
         #check if there are no intersections, so this room is valid
         if self.model.does_room_overlap(new_room) == False:
            #"paint" it to the map's tiles
            self.create_room(new_room)
    
            #connect all rooms but the first to the previous room with a tunnel
            prev_room = self.model.get_last_room()
            if prev_room is not None:
               prev_center = prev_room.center()
               new_center = new_room.center()
               self.connect_rooms(prev_center,new_center)

            #append the new room to the list
            self.model.add_room(new_room)

   def create_room(self,room):
      #go through the tiles in the rectangle and make them passable
      for x in range(room.x1, room.x2):
         for y in range(room.y1, room.y2):
            self.model.grid[x][y].blocked = False
            self.model.grid[x][y].block_sight = False

   def create_h_tunnel(self, x1, x2, y):
      x, w = min(x1,x2), abs(x1-x2)+1
      room = Rect(x,y,w,1)
      self.create_room(room)

   def create_v_tunnel(self, y1, y2, x):
      y, h = min(y1,y2), abs(y1-y2)+1
      room = Rect(x,y,1,h)
      self.create_room(room)

   def connect_rooms(self,center1,center2): 
      (center1x, center1y) = center1
      (center2x, center2y) = center2

      #draw a coin (random number that is either 0 or 1)
      if random.choice([True, False]):
         #first move horizontally, then vertically
         self.create_h_tunnel(center1x, center2x, center1y)
         self.create_v_tunnel(center1y, center2y, center2x)
      else:
         #first move vertically, then horizontally
         self.create_v_tunnel(center1y, center2y, center1x)
         self.create_h_tunnel(center1x, center2x, center2y)
