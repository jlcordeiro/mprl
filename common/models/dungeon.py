import libtcodpy as libtcod
from config import *
from collections import namedtuple

Stairs = namedtuple('Stairs', ['position', 'type'])

class Level(object):
    def __init__(self, walls, stairs = None):
        self.walls = walls
        self.explored = [[False for y in range(MAP_HEIGHT)] for x in range(MAP_WIDTH)]
        self.stairs = stairs

    def is_blocked(self, pos):
        return self.walls[pos[0]][pos[1]]

    def json(self):
        return {'walls':  [[b for b in row] for row in self.walls],
                'stairs': self.stairs.position if self.stairs is not None else None}

class Dungeon(object):
    def __init__(self, levels):
        self.levels = levels
        self.current_level = 0

    def json(self):
        return {'current_level': self.current_level,
                'levels': {idx: level.json() for idx, level in self.levels.items()}}
