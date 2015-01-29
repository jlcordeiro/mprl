import random
import views.dungeon
import common.models.dungeon
from common.models.dungeon import Level, Stairs
from common.utilities.geometry import Rect, Point
from common.utilities.utils import reduce_map, expand_map
from common.utilities.path import APath
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
    levels = {idx: Level(reduce_map(generate_random_walls(MAX_ROOMS)))
              for idx in xrange(0, NUM_LEVELS)}

    #build stairs
    for idx in xrange(0, NUM_LEVELS - 1):
        while True:
            stairs_pos = (random.randint(1, MAP_WIDTH - 1),
                          random.randint(1, MAP_HEIGHT - 1),
                          0)
            if not levels[idx].is_blocked(stairs_pos) and \
               not levels[idx + 1].is_blocked(stairs_pos):
                break

        levels[idx].stairs = Stairs(stairs_pos)

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

    @property
    def depth(self):
        return self._model.current_level

    def is_blocked(self, pos):
        if len(pos) == 2: pos = (pos[0], pos[1], self.depth)
        return self._model.levels[pos[2]].is_blocked(pos)

    def get_path(self, source_pos, target_pos):
        sx, sy, _ = source_pos
        tx, ty, _ = target_pos
        A = APath(MAP_WIDTH, MAP_HEIGHT, (sx, sy), self.is_blocked)
        A.find_path((tx, ty))

        return A.path[0]

    def update_explored(self, player):
        for y in range(MAP_HEIGHT):
            for x in range(MAP_WIDTH):
                if player.is_in_fov((x, y)):
                    self.__clevel.explored[x][y] = True

    def compute_path(self):
        pass

    def climb_stairs(self, pos):
        sx, sy, _ = self.__clevel.stairs.position
        if sx == pos.x and sy == pos.y:
            self._model.current_level += 1

        return self._model.current_level

    def clear_ui(self, con):
        self._view.clear(con, self.__clevel)

    def draw_ui(self, con, is_in_fov_func):
        self._view.draw(con, self.__clevel, is_in_fov_func)
