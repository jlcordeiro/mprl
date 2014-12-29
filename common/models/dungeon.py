import libtcodpy as libtcod
import random
from config import *
import controllers
from collections import namedtuple
from controllers.objects import ItemFactory
from controllers.creatures import MonsterFactory
import common.models.creatures
from common.utilities.geometry import Rect
from common.utilities.geometry import Point
from controllers.creatures import attack

Stairs = namedtuple('Stairs', ['position', 'type', 'destiny'])

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


class Level(object):
    def __init__(self, branch_name, name, n_rooms):
        #fill map with "unblocked" tiles
        self.blocked = [[True for y in range(MAP_HEIGHT)] for x in range(MAP_WIDTH)]
        self.explored = [[False for y in range(MAP_HEIGHT)] for x in range(MAP_WIDTH)]

        self.branch_name = branch_name
        self.name = name

        self.rooms = []
        self.stairs = []

        self.fov_map = libtcod.map_new(MAP_WIDTH, MAP_HEIGHT)
        self.path = None

        self.__generate(n_rooms)
        self.__compute_fov()

    def is_blocked(self, pos):
        x, y = pos
        return self.blocked[x][y]

    def dig_room(self, room):
        for x in range(room.top_left.x, room.bottom_right.x):
            for y in range(room.top_left.y, room.bottom_right.y):
                self.blocked[x][y] = False

    def is_in_fov(self, pos):
        return libtcod.map_is_in_fov(self.fov_map, pos[0], pos[1])

    def __compute_fov(self):
        for y in range(MAP_HEIGHT):
            for x in range(MAP_WIDTH):
                blocked = self.blocked[x][y]
                libtcod.map_set_properties(self.fov_map, x, y,
                                           not blocked,
                                           not blocked)

    def __generate(self, n_rooms):
        # build rooms
        for r in range(n_rooms):
            self.__build_complete_room()

        # keep track of which rooms aren't connected yet
        unconnected = list(self.rooms)

        for room in self.rooms:
            # connect rooms
            if room not in unconnected:
                continue

            closest = min(unconnected, key = room.distance_to_rect)

            (h_tunnel, v_tunnel) = create_room_connection(room, closest)
            self.dig_room(h_tunnel)
            self.dig_room(v_tunnel)

            unconnected.remove(room)

    def __build_complete_room(self):
        #random width and height
        w = random.randint(ROOM_MIN_SIZE, ROOM_MAX_SIZE)
        h = random.randint(ROOM_MIN_SIZE, ROOM_MAX_SIZE)
        #random position without going out of the boundaries of the map
        x = random.randint(1, MAP_WIDTH - w - 1)
        y = random.randint(1, MAP_HEIGHT - h - 1)

        room = Rect(x, y, w, h)

        #check if there are no intersections, so this room is valid
        intersection = next((r for r in self.rooms if r.intersects(room)), None)
        if intersection is None:
            self.dig_room(room)
            self.rooms.append(room)


class Dungeon:
    def __init__(self):
        self.levels = {}

        # main level
        main_level = Level("Town", "Town", 1)

        self.levels[main_level.name] = main_level
        self.current_level = self.levels[main_level.name]

        self._create_branch("Forest", NUM_LEVELS, main_level)
        self._create_branch("Mines", NUM_LEVELS, main_level)

    def _create_branch(self, branch_name, n_levels, origin_level):
        for l in xrange(0, NUM_LEVELS):
            level_name = branch_name + " (" + str(l+1)  + ")"
            new_level = Level(branch_name, level_name, MAX_ROOMS)
            self.levels[level_name] = new_level

            while True:
                stairs_pos = Point(random.randint(1, MAP_WIDTH - 1),
                                   random.randint(1, MAP_HEIGHT - 1))
                if new_level.is_blocked(stairs_pos) is False:
                    break

            down_stairs = Stairs(stairs_pos, "stairs_down", new_level)
            up_stairs = Stairs(stairs_pos, "stairs_up", origin_level)

            origin_level.stairs.append(down_stairs)
            new_level.stairs.append(up_stairs)

            origin_level = new_level
