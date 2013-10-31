import libtcodpy as libtcod

MAP_WIDTH = 80
MAP_HEIGHT = 45

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

class LevelModel:
   def __init__(self):
      #fill map with "unblocked" tiles
      self.grid = [[ Tile(False)
            for y in range(MAP_HEIGHT) ]
            for x in range(MAP_WIDTH) ]

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

      #create two rooms
      room1 = Rect(20, 15, 10, 15)
      room2 = Rect(50, 15, 10, 15)
      self.create_room(room1)
      self.create_room(room2)
      self.create_h_tunnel(25, 55, 23)

      self.view = LevelView(self.model)

   def create_room(self,room):
      #go through the tiles in the rectangle and make them passable
      for x in range(room.x1 + 1, room.x2):
         for y in range(room.y1 + 1, room.y2):
            self.model.grid[x][y].blocked = False
            self.model.grid[x][y].block_sight = False

      for y in range(MAP_HEIGHT):
         for x in range(MAP_WIDTH):
            wall = self.model.grid[x][y].block_sight
            if wall is False:
               print wall

   def create_h_tunnel(self, x1, x2, y):
      for x in range(min(x1, x2), max(x1, x2) + 1):
         self.model.grid[x][y].blocked = False
         self.model.grid[x][y].block_sight = False

   def create_v_tunnel(self, y1, y2, x):
      for x in range(min(y1, y2), max(y1, y2) + 1):
         self.model.grid[x][y].blocked = False
         self.model.grid[x][y].block_sight = False
