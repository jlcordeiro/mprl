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
      self.view = LevelView(self.model)
