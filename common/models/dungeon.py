import libtcodpy as libtcod
from config import *
from common.utilities.geometry import Point
from common.models.objects import ObjectModel
from common.utilities.utils import reduce_map, expand_map

class Stairs(ObjectModel):
    def __init__(self, position):
        super(Stairs, self).__init__("stairs", "stairs_down", position, False)


class Level(object):
    def __init__(self, walls, stairs=None, explored=None):
        self.walls = expand_map(walls)
        self.explored = expand_map(explored) if explored else self._get_unexplored_array()
        self.stairs = stairs

    def _get_unexplored_array(self):
        return [[False for _ in range(MAP_HEIGHT)] for _ in range(MAP_WIDTH)]

    def is_blocked(self, pos):
        return self.walls[pos[0]][pos[1]]

    def json(self):
        return {'walls': reduce_map(self.walls),
                'explored': reduce_map(self.explored),
                'stairs': self.stairs.position if self.stairs else None}


class Dungeon(object):
    def __init__(self, levels, current_level):
        self.levels = levels
        self.current_level = current_level

    def json(self):
        return {'current_level': self.current_level,
                'levels': {i: l.json() for i, l in self.levels.items()}}
