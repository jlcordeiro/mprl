import libtcodpy as libtcod
import random
import views.dungeon
import common.models.dungeon
from common.utilities.geometry import Point
from config import *
from messages import *

class Dungeon(object):
    def __init__(self):
        self._model = common.models.dungeon.Dungeon()
        self._view = views.dungeon.Level(self._model)
   
    @property
    def __clevel(self):
        """ Return the current level. """
        return self._model.current_level

    def is_blocked(self, pos):
        #first test the map tile
        if self.__clevel.is_blocked(pos):
            return True

        #now check for any blocking monsters
        #return (self.get_monster_in_pos(pos) is not None)
        return False

    def is_in_fov(self, pos):
        return self.__clevel.is_in_fov(pos)

    def random_unblocked_pos(self):
        #choose random spot
        pos = Point(random.randint(1, MAP_WIDTH - 1),
                    random.randint(1, MAP_HEIGHT - 1))

        if not self.is_blocked(pos):
            return pos

        return self.random_unblocked_pos()

    def get_path(self, source_pos, target_pos):
        sx, sy = source_pos
        tx, ty = target_pos
        libtcod.path_compute(self.path, sx, sy, tx, ty)

        if libtcod.path_is_empty(self.__clevel.path):
            return None

        return libtcod.path_get(self.__clevel.path, 0)

    def update_fov(self, pos):
        libtcod.map_compute_fov(self.__clevel.fov_map, pos[0], pos[1],
                                TORCH_RADIUS, FOV_LIGHT_WALLS, FOV_ALGO)

        for y in range(MAP_HEIGHT):
            for x in range(MAP_WIDTH):
                if self.is_in_fov((x, y)):
                    self.__clevel.explored[x][y] = True

    def compute_path(self):
        # build map for path finding
        path_map = libtcod.map_new(MAP_WIDTH, MAP_HEIGHT)

        for x in range(MAP_WIDTH):
            for y in range(MAP_HEIGHT):
                libtcod.map_set_properties(path_map, x, y, True,
                                           not self.is_blocked((x, y)))

        self.__clevel.path = libtcod.path_new_using_map(path_map)

    def climb_stairs(self, pos):
        messages = MessagesBorg()

        stairs = next((s for s in self.__clevel.stairs if s.position == pos), None)

        if stairs == None:
            messages.add('There are no stairs here.', libtcod.orange)
        else:
            messages.add('You climb some stairs..', libtcod.green)
            self._model.current_level = stairs.destiny

    def clear_ui(self, con):
        self._view.clear(con)

    def draw_ui(self, con, draw_outside_fov):
        self._view.draw(con, draw_outside_fov)

    def draw_name(self, con, x, y):
        self._view.draw_name(con, x, y)
