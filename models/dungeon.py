import libtcodpy as libtcod
import math
import random
from config import *
import controllers
from controllers.items import ItemFactory
from controllers.creatures import MonsterFactory


class Tile:
   #a tile of the map and its properties
    def __init__(self, blocked, block_sight=None):
        self.blocked = blocked
        self.explored = False

        #by default, if a tile is blocked, it also blocks sight
        self.block_sight = blocked if block_sight is None else block_sight


class Room:
    #a rectangle on the map. used to characterize a room.
    def __init__(self, x, y, w, h):
        self.x1 = x
        self.y1 = y
        self.x2 = x + w
        self.y2 = y + h
        self.connected = False

    @property
    def all_points(self):
        return [(x, y)
                for x in range(self.x1, self.x2)
                for y in range(self.y1, self.y2)]

    @property
    def center(self):
        center_x = (self.x1 + self.x2) / 2
        center_y = (self.y1 + self.y2) / 2
        return (center_x, center_y)

    def get_random_point(self):
        x = random.randint(self.x1 + 1, self.x2 - 1)
        y = random.randint(self.y1 + 1, self.y2 - 1)

        return (x, y)
 
    def x_distance_to_room(self, other):
        if (self.x1 >= other.x1 and self.x1 <= other.x2) or \
           (self.x2 >= other.x1 and self.x2 <= other.x2):
            return 0

        if self.x2 < other.x1:
            return other.x1 - self.x2

        return self.x1 - other.x2

    def y_distance_to_room(self, other):
        if (self.y1 >= other.y1 and self.y1 <= other.y2) or \
           (self.y2 >= other.y1 and self.y2 <= other.y2):
            return 0

        if self.y2 < other.y1:
            return other.y1 - self.y2

        return self.y1 - other.y2

    def intersects(self, other):
        #returns true if this rectangle intersects with another one
        return (self.x_distance_to_room(other) <= 1 and
                self.y_distance_to_room(other) <= 1)

    def distance_to_room(self, other):
        if self.intersects(other):
            return 1

        dx = self.x_distance_to_room(other)
        dy = self.y_distance_to_room(other)

        return math.sqrt(dx ** 2 + dy ** 2)


def create_room_connection(room1, room2, mode="center"):
    """Create tunnels to connect room1 and room2.
       When mode is "center" the tunnels are started from the
       center of each room. When it is "random", the origin
       points are random points inside the room."""

    h_tunnel = lambda x1, x2, y: Room(min(x1, x2), y, abs(x1 - x2) + 1, 1)
    v_tunnel = lambda y1, y2, x: Room(x, min(y1, y2), 1, abs(y1 - y2) + 1)

    if mode == "center":
        (origin1x, origin1y) = room1.center
        (origin2x, origin2y) = room2.center
    elif mode == "random":
        (origin1x, origin1y) = room1.get_random_point()
        (origin2x, origin2y) = room2.get_random_point()

    #draw a coin (random number that is either 0 or 1)
    if random.choice([True, False]):
        #first move horizontally, then vertically
        h_tunnel = h_tunnel(origin1x, origin2x, origin1y)
        v_tunnel = v_tunnel(origin1y, origin2y, origin2x)
    else:
        #first move vertically, then horizontally
        v_tunnel = v_tunnel(origin1y, origin2y, origin1x)
        h_tunnel = h_tunnel(origin1x, origin2x, origin2y)

    return (h_tunnel, v_tunnel)


class Level:
    def __init__(self):
        #fill map with "unblocked" tiles
        self.tiles = [[Tile(True)
                       for y in range(MAP_HEIGHT)]
                      for x in range(MAP_WIDTH)]

        self.rooms = []
        self.num_rooms = 0

        self.items = []
        self.monsters = []

        self.stairs_up_pos = None
        self.stairs_down_pos = None

        self.fov_map = libtcod.map_new(MAP_WIDTH, MAP_HEIGHT)
        self.path = None

        self.aim_target = None

        # often it may be required to draw things and then remove
        # them some turns later. This list will keep track of all
        # of them. Format: (position, char, nturns)
        self.temp_artifacts = []

    def __add_room(self, room):
        self.rooms.append(room)
        self.num_rooms += 1

    def __dig_room(self, room):
        #go through the tiles in the rectangle and make them passable
        for (x, y) in room.all_points:
            self.tiles[x][y].blocked = False
            self.tiles[x][y].block_sight = False

    def is_blocked(self, pos):
        x, y = pos

        #first test the map tile
        if self.tiles[x][y].blocked:
            return True

        #now check for any blocking monsters
        return (self.get_monster_in_pos(pos) is not None)

    def is_in_fov(self, pos):
        return libtcod.map_is_in_fov(self.fov_map, pos[0], pos[1]) 

    def __place_monsters_in_room(self, room):
        #choose random number of monsters
        num_monsters = random.randint(0, MAX_ROOM_MONSTERS)

        for i in range(num_monsters):
            #choose random spot for this monster
            (x, y) = room.get_random_point()

            if not self.is_blocked((x, y)):
                monster = MonsterFactory(x, y)
                self.monsters.append(monster)

    def __place_items_in_room(self, room):
        #choose random number of items
        num_items = libtcod.random_get_int(0, 0, MAX_ROOM_ITEMS)

        for i in range(num_items):
            #choose random spot for this item
            (x, y) = room.get_random_point()

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
            self.__dig_room(room)
            self.__add_room(room)

            self.__place_items_in_room(room)
            self.__place_monsters_in_room(room)

    def generate(self):
        # build rooms
        for r in range(MAX_ROOMS):
            self.__build_complete_room()

        # place stairs
        self.stairs_up_pos = self.random_unblocked_pos()
        self.stairs_down_pos = self.random_unblocked_pos()

        # connect rooms
        for room in self.rooms:
            if room.connected:
                continue

            unconnected = [r for r in self.rooms if not r.connected and r != room]

            if len(unconnected) > 0:
                closest = min(unconnected, key = room.distance_to_room)

                (h_tunnel, v_tunnel) = create_room_connection(room, closest, "random")
                self.__dig_room(h_tunnel)
                self.__dig_room(v_tunnel)

            room.connected = True

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

    def compute_fov(self):
        for y in range(MAP_HEIGHT):
            for x in range(MAP_WIDTH):
                tile = self.tiles[x][y]
                libtcod.map_set_properties(self.fov_map, x, y,
                                           not tile.block_sight,
                                           not tile.blocked)

    def update_fov(self, pos):
        libtcod.map_compute_fov(self.fov_map, pos[0], pos[1],
                                TORCH_RADIUS, FOV_LIGHT_WALLS, FOV_ALGO)

        for y in range(MAP_HEIGHT):
            for x in range(MAP_WIDTH):
                if self.is_in_fov((x, y)):
                    self.tiles[x][y].explored = True


class Dungeon:
    def __init__(self):
        self.levels = {}
        self.current_level = 0

        for l in xrange(0, NUM_LEVELS):
            new_level = Level()
            new_level.generate()
            new_level.compute_fov()
            self.levels[l] = new_level

        # start the player on a random position (not blocked)
        (x, y) = self.levels[0].random_unblocked_pos()
        self.player = controllers.creatures.Player(x, y)

    def move_player(self, dx, dy):

        old_pos = self.player.position
        new_pos = (old_pos[0]+dx, old_pos[1]+dy)

        cur_level = self.levels[self.current_level]

        monster = cur_level.get_monster_in_pos(new_pos)
        if monster is not None:
            self.player.attack(monster)
        elif not cur_level.is_blocked(new_pos):
            self.player.move(dx, dy)

        cur_level.update_fov(self.player.position)
