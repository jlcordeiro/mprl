import libtcodpy as libtcod
import random
import views.dungeon
import common.models.dungeon
from common.models.dungeon import Stairs, Level
from common.utilities.geometry import Rect, Point2, Point3
from config import *
from messages import *


def create_room_connection(room1, room2):
    """Create tunnels to connect room1 and room2.
       The origin points are random points inside the room."""

    h_tunnel = lambda x1, x2, y: Rect(min(x1, x2), y, abs(x1 - x2) + 1, 1)
    v_tunnel = lambda y1, y2, x: Rect(x, min(y1, y2), 1, abs(y1 - y2) + 1)

    origin1 = room1.get_random_point()
    origin2 = room2.get_random_point()

    #draw a coin (random number that is either 0 or 1)
    if random.choice([True, False]):
        #first move horizontally, then vertically
        h_tunnel = h_tunnel(origin1.x, origin2.x, origin1.y)
        v_tunnel = v_tunnel(origin1.y, origin2.y, origin2.x)
    else:
        #first move vertically, then horizontally
        v_tunnel = v_tunnel(origin1.y, origin2.y, origin1.x)
        h_tunnel = h_tunnel(origin1.x, origin2.x, origin2.y)

    return (h_tunnel, v_tunnel)


def get_room_connections(rooms):
    connections = []

    # keep track of which rooms aren't connected yet
    unconnected = list(rooms)

    for room in rooms:
        # connect rooms
        if room not in unconnected:
            continue

        unconnected.remove(room)

        if len(unconnected) == 0:
            break

        closest = min(unconnected, key=room.distance_to_rect)

        (h_tunnel, v_tunnel) = create_room_connection(room, closest)
        connections += [h_tunnel, v_tunnel]

    return connections


def generate_rooms(n_rooms):
    rooms = []

    for _ in xrange(0, n_rooms):
        #random width and height
        w = random.randint(ROOM_MIN_SIZE, ROOM_MAX_SIZE)
        h = random.randint(ROOM_MIN_SIZE, ROOM_MAX_SIZE)
        #random position without going out of the boundaries of the map
        x = random.randint(1, MAP_WIDTH - w - 1)
        y = random.randint(1, MAP_HEIGHT - h - 1)

        room = Rect(x, y, w, h)

        #check if there are no intersections, so this room is valid
        if next((r for r in rooms if r.intersects(room)), None) is None:
            rooms.append(room)

    return rooms


def generate_random_walls(n_rooms):
    result = [[True for y in range(MAP_HEIGHT)] for x in range(MAP_WIDTH)]

    rooms = generate_rooms(n_rooms)

    for room in rooms + get_room_connections(rooms):
        for x in range(room.top_left.x, room.bottom_right.x):
            for y in range(room.top_left.y, room.bottom_right.y):
                result[x][y] = False

    return result


def generate_random_levels():
    levels = {idx: Level(generate_random_walls(MAX_ROOMS))
              for idx in xrange(0, NUM_LEVELS)}

    #build stairs
    for idx in xrange(0, NUM_LEVELS - 1):
        while True:
            stairs_pos = Point2(random.randint(1, MAP_WIDTH - 1),
                                random.randint(1, MAP_HEIGHT - 1))
            if not levels[idx].is_blocked(stairs_pos) and \
               not levels[idx + 1].is_blocked(stairs_pos):
                break

        levels[idx].stairs = Stairs(stairs_pos, "stairs_down")

    return levels


class Dungeon(object):
    def __init__(self, levels=None, current_level=0):
        if levels is None:
            levels = generate_random_levels()
        self._model = common.models.dungeon.Dungeon(levels, current_level)
        self._view = views.dungeon.Level()

    @property
    def __clevel(self):
        """ Return the current level. """
        return self._model.levels[self._model.current_level]

    def is_blocked(self, pos):
        #first test the map tile
        if self._model.levels[pos[2]].is_blocked(pos):
            return True

        #now check for any blocking monsters
        #return (self.get_monster_in_pos(pos) is not None)
        return False

    def random_unblocked_pos(self, depth=None):
        if depth is None:
            depth = self._model.current_level

        pos = Point3(random.randint(1, MAP_WIDTH - 1),
                     random.randint(1, MAP_HEIGHT - 1),
                     depth)

        if not self.is_blocked(pos):
            return pos

        return self.random_unblocked_pos(depth)

    def get_path(self, source_pos, target_pos):
        libtcod.path_compute(self.path, source_pos[0], source_pos[1],
                             target_pos[0], target_pos[1])

        if libtcod.path_is_empty(self.path):
            return None

        return libtcod.path_get(self.path, 0)

    def update_explored(self, player):
        for y in range(MAP_HEIGHT):
            for x in range(MAP_WIDTH):
                if player.is_in_fov((x, y)):
                    self.__clevel.explored[x][y] = True

    def compute_path(self):
        # build map for path finding
        path_map = libtcod.map_new(MAP_WIDTH, MAP_HEIGHT)

        z = self._model.current_level
        for x in range(MAP_WIDTH):
            for y in range(MAP_HEIGHT):
                libtcod.map_set_properties(path_map, x, y, True,
                                           not self.is_blocked((x, y, z)))

        self.path = libtcod.path_new_using_map(path_map)

    def climb_stairs(self, pos):
        messages = Messages()

        sx, sy = self.__clevel.stairs.position
        if sx != pos.x or sy != pos.y:
            messages.add('There are no stairs here.')
        else:
            messages.add('You climb some stairs..')
            self._model.current_level += 1

        return self._model.current_level

    def clear_ui(self, con):
        self._view.clear(con, self.__clevel)

    def draw_ui(self, con, is_in_fov_func):
        self._view.draw(con, self.__clevel, is_in_fov_func)
