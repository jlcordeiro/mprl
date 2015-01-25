import libtcodpy as libtcod
from config import *
from common.utilities.geometry import Point
from common.models.objects import ObjectModel

class Stairs(ObjectModel):
    def __init__(self, position):
        super(Stairs, self).__init__("stairs", "stairs_down", position, False)


class Level(object):
    def __init__(self, walls, stairs=None, explored=None):
        self.walls = walls
        self.explored = explored if explored else self._get_unexplored_array()
        self.stairs = stairs

    def _get_unexplored_array(self):
        return [[False for _ in range(MAP_HEIGHT)] for _ in range(MAP_WIDTH)]

    def is_blocked(self, pos):
        return self.walls[pos[0]][pos[1]]

    def json(self):
        return {'walls': [[b for b in row] for row in self.walls],
                'explored': [[e for e in row] for row in self.explored],
                'stairs': self.stairs.position if self.stairs else None}


class Dungeon(object):
    def __init__(self, levels, current_level):
        self.levels = levels
        self.current_level = current_level

    def json(self):
        return {'current_level': self.current_level,
                'levels': {i: l.json() for i, l in self.levels.items()}}
