import libtcodpy as libtcod
import random
from config import *
import controllers
from collections import namedtuple
from controllers.objects import ItemFactory
from controllers.creatures import MonsterFactory
from utilities.geometry import Rect
from utilities.geometry import Point

Stairs = namedtuple('Stairs', ['pos_i', 'pos_f', 'type', 'destiny'])


class Room(Rect):
    #a rectangle on the map. used to characterize a room.
    def __init__(self, x, y, w, h):
        super(Room, self).__init__(x, y, w, h)
        self.connected = False

    def get_random_point(self):
        x = random.randint(self.top_left.x + 1, self.bottom_right.x - 1)
        y = random.randint(self.top_left.y + 1, self.bottom_right.y - 1)

        return Point(x, y)


def create_room_connection(room1, room2, mode="center"):
    """Create tunnels to connect room1 and room2.
       When mode is "center" the tunnels are started from the
       center of each room. When it is "random", the origin
       points are random points inside the room."""

    h_tunnel = lambda x1, x2, y: Room(min(x1, x2), y, abs(x1 - x2) + 1, 1)
    v_tunnel = lambda y1, y2, x: Room(x, min(y1, y2), 1, abs(y1 - y2) + 1)

    if mode == "center":
        origin1 = room1.center
        origin2 = room2.center
    elif mode == "random":
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


class BasicLevel(object):
    def __init__(self, branch_name, name, n_rooms):
        #fill map with "unblocked" tiles
        self.blocked = [[True for y in range(MAP_HEIGHT)] for x in range(MAP_WIDTH)]
        self.explored = [[False for y in range(MAP_HEIGHT)] for x in range(MAP_WIDTH)]

        self.branch_name = branch_name
        self.name = name

        self.rooms = []
        self.num_rooms = 0

        self.items = []
        self.monsters = []

        self.stairs = []

        self.fov_map = libtcod.map_new(MAP_WIDTH, MAP_HEIGHT)
        self.path = None

        self.aim_target = None

        # often it may be required to draw things and then remove
        # them some turns later. This list will keep track of all
        # of them. Format: (position, char, nturns)
        self.temp_artifacts = []

    def dig_room(self, room):
        #go through the tiles in the rectangle and make them passable
        tl = room.top_left
        br = room.bottom_right
        for x in range(tl.x, br.x):
            for y in range(tl.y, br.y):
                self.blocked[x][y] = False

    def add_room(self, room):
        self.rooms.append(room)
        self.num_rooms += 1

    def is_blocked(self, pos):
        x, y = pos

        #first test the map tile
        if self.blocked[x][y]:
            return True

        #now check for any blocking monsters
        return (self.get_monster_in_pos(pos) is not None)

    def is_in_fov(self, pos):
        return libtcod.map_is_in_fov(self.fov_map, pos[0], pos[1])

    def random_unblocked_pos(self):
        #choose random spot
        pos = (random.randint(1, MAP_WIDTH - 1),
               random.randint(1, MAP_HEIGHT - 1))

        if not self.is_blocked(pos):
            return pos

        return self.random_unblocked_pos()

    def get_monster_in_pos(self, pos):
        return next((m for m in self.monsters
                     if m.position == pos and m.blocks), None)

    def closest_monster_to_pos(self, pos, max_range):
        #find closest enemy, up to a maximum range, and in the player's FOV
        if len(self.monsters) < 1:
            return None

        closest = min(self.monsters, key = lambda x: x.distance_to(pos))
        if (closest is None or
            not self.is_in_fov(closest.position) or
            closest.distance_to(pos) > max_range):
            return None

        return closest

    def compute_path(self):
        # build map for path finding
        path_map = libtcod.map_new(MAP_WIDTH, MAP_HEIGHT)

        for x in range(MAP_WIDTH):
            for y in range(MAP_HEIGHT):
                libtcod.map_set_properties(path_map, x, y, True,
                                           not self.is_blocked((x, y)))

        self.path = libtcod.path_new_using_map(path_map)

    def get_path_to_pos(self, monster, pos):
        mx, my = monster.position
        libtcod.path_compute(self.path, mx, my, pos[0], pos[1])

        if libtcod.path_is_empty(self.path):
            return None

        return libtcod.path_get(self.path, 0)

    def _compute_fov(self):
        for y in range(MAP_HEIGHT):
            for x in range(MAP_WIDTH):
                blocked = self.blocked[x][y]
                libtcod.map_set_properties(self.fov_map, x, y,
                                           not blocked,
                                           not blocked)

    def update_fov(self, pos):
        libtcod.map_compute_fov(self.fov_map, pos[0], pos[1],
                                TORCH_RADIUS, FOV_LIGHT_WALLS, FOV_ALGO)

        for y in range(MAP_HEIGHT):
            for x in range(MAP_WIDTH):
                if self.is_in_fov((x, y)):
                    self.explored[x][y] = True

    def update_artifacts(self):
        #remove artifacts that are too "old"
        self.temp_artifacts = [v for v in self.temp_artifacts if v[2] > 0]


class Town(BasicLevel):
    def __init__(self):
        super(Town, self).__init__("Town", "Town", 1)

        self.__build_empty_room()
        self._compute_fov()

    def __build_empty_room(self):
        #random width and height
        w = random.randint(ROOM_MIN_SIZE, ROOM_MAX_SIZE)
        h = random.randint(ROOM_MIN_SIZE, ROOM_MAX_SIZE)
        #random position without going out of the boundaries of the map
        x = random.randint(1, MAP_WIDTH - w - 1)
        y = random.randint(1, MAP_HEIGHT - h - 1)

        room = Room(x, y, w, h)
        self.dig_room(room)
        self.add_room(room)


class Level(BasicLevel):
    def __init__(self, branch_name, name, n_rooms):
        super(Level, self).__init__(branch_name, name, n_rooms)
        self.__generate(n_rooms)
        self._compute_fov()

    def __generate(self, n_rooms):
        # build rooms
        for r in range(n_rooms):
            self.__build_complete_room()

        # connect rooms
        for room in self.rooms:
            if room.connected:
                continue

            unconnected = [r for r in self.rooms if not r.connected and r != room]

            if len(unconnected) > 0:
                closest = min(unconnected, key = room.distance_to_rect)

                (h_tunnel, v_tunnel) = create_room_connection(room, closest, "random")
                self.dig_room(h_tunnel)
                self.dig_room(v_tunnel)

            room.connected = True

    def __place_monsters_in_room(self, room):
        #choose random number of monsters
        num_monsters = random.randint(0, MAX_ROOM_MONSTERS)

        for i in range(num_monsters):
            #choose random spot for this monster
            x, y = room.get_random_point().coords

            if not self.is_blocked((x, y)):
                monster = MonsterFactory(x, y)
                self.monsters.append(monster)

    def __place_items_in_room(self, room):
        #choose random number of items
        num_items = libtcod.random_get_int(0, 0, MAX_ROOM_ITEMS)

        for i in range(num_items):
            #choose random spot for this item
            x, y = room.get_random_point().coords

            #only place it if the tile is not blocked
            if not self.is_blocked((x, y)):
                item = ItemFactory(x, y)
                self.items.append(item)

    def __build_complete_room(self):
        #random width and height
        w = random.randint(ROOM_MIN_SIZE, ROOM_MAX_SIZE)
        h = random.randint(ROOM_MIN_SIZE, ROOM_MAX_SIZE)
        #random position without going out of the boundaries of the map
        x = random.randint(1, MAP_WIDTH - w - 1)
        y = random.randint(1, MAP_HEIGHT - h - 1)

        room = Room(x, y, w, h)

        #check if there are no intersections, so this room is valid
        intersection = next((r for r in self.rooms if r.intersects(room)), None)
        if intersection is None:
            self.dig_room(room)
            self.add_room(room)

            self.__place_items_in_room(room)
            self.__place_monsters_in_room(room)





# M (Main level)
# |
# |--- Branch 1 -- (...)
# |
# |--- Branch 2 -- (...)
# |
# |--- Branch 3 -- (...)
# |
# (...)

class Dungeon:
    def __init__(self):
        self.levels = {}

        # main level
        main_level = Town()

        self.levels[main_level.name] = main_level
        self.current_level = self.levels[main_level.name]

        self._create_branch("Forest", NUM_LEVELS, main_level)
        self._create_branch("Mines", NUM_LEVELS, main_level)

        # start the player on a random position (not blocked)
        (x, y) = self.current_level.random_unblocked_pos()
        self.player = controllers.creatures.Player(x, y)

    def _create_branch(self, branch_name, n_levels, origin_level):
        levels = {}

        from_pos = origin_level.random_unblocked_pos()

        for l in xrange(0, NUM_LEVELS):
            level_name = branch_name + " (" + str(l+1)  + ")"

            new_level = Level(branch_name, level_name, MAX_ROOMS)
            to_pos = new_level.random_unblocked_pos()

            levels[level_name] = new_level

            down_stairs = Stairs(from_pos, to_pos, "STAIRS_DOWN", new_level)
            up_stairs = Stairs(to_pos, from_pos, "STAIRS_UP", origin_level)

            origin_level.stairs.append(down_stairs)
            new_level.stairs.append(up_stairs)

            origin_level = new_level
            from_pos = origin_level.random_unblocked_pos()

    def move_player(self, dx, dy):

        old_pos = self.player.position
        new_pos = (old_pos[0]+dx, old_pos[1]+dy)

        cur_level = self.current_level

        monster = cur_level.get_monster_in_pos(new_pos)
        if monster is not None:
            self.player.attack(monster)
        elif not cur_level.is_blocked(new_pos):
            self.player.move(dx, dy)

        cur_level.update_fov(self.player.position)
