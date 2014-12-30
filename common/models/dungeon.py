import libtcodpy as libtcod
from config import *
from collections import namedtuple

Stairs = namedtuple('Stairs', ['position', 'type'])

class Level(object):
    def __init__(self, walls, stairs = None):
        self.id = id
        self.walls = walls
        self.explored = [[False for y in range(MAP_HEIGHT)] for x in range(MAP_WIDTH)]
        self.stairs = stairs
        self.fov_map = libtcod.map_new(MAP_WIDTH, MAP_HEIGHT)

        for y in range(MAP_HEIGHT):
            for x in range(MAP_WIDTH):
                libtcod.map_set_properties(self.fov_map, x, y,
                                           not walls[x][y],
                                           not walls[x][y])

    def is_blocked(self, pos):
        return self.walls[pos[0]][pos[1]]

    def is_in_fov(self, pos):
        return libtcod.map_is_in_fov(self.fov_map, pos[0], pos[1])


class Dungeon(object):
    def __init__(self, levels):
        self.levels = levels
        self.current_level = 0
