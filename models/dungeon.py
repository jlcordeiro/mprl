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

    def __add_room(self, room):
        self.rooms.append(room)
        self.num_rooms += 1

    def add_monster(self, monster):
        self.monsters.append(monster)

    def add_item(self, item):
        self.items.append(item)

    def __room_overlaps(self, room):
        #run through the other rooms and see if they intersect with this one
        for other_room in self.rooms:
            if room.intersects(other_room):
                return True

        return False

    def __dig_room(self, room):
        #go through the tiles in the rectangle and make them passable
        for (x, y) in room.all_points:
            self.tiles[x][y].blocked = False
            self.tiles[x][y].block_sight = False

    def __dig_h_tunnel(self, x1, x2, y):
        x, w = min(x1, x2), abs(x1 - x2) + 1
        room = Room(x, y, w, 1)
        self.__dig_room(room)

    def __dig_v_tunnel(self, y1, y2, x):
        y, h = min(y1, y2), abs(y1 - y2) + 1
        room = Room(x, y, 1, h)
        self.__dig_room(room)

    def __connect_two_rooms(self, room1, room2, mode="center"):
        """Digs tunnels between room1 and room2.
           When mode is "center" the tunnels are started from the
           center of each room. When it is "random", the origin
           points are random points inside the room."""

        if mode == "center":
            (origin1x, origin1y) = room1.center
            (origin2x, origin2y) = room2.center
        elif mode == "random":
            (origin1x, origin1y) = room1.get_random_point()
            (origin2x, origin2y) = room2.get_random_point()

        #draw a coin (random number that is either 0 or 1)
        if random.choice([True, False]):
            #first move horizontally, then vertically
            self.__dig_h_tunnel(origin1x, origin2x, origin1y)
            self.__dig_v_tunnel(origin1y, origin2y, origin2x)
        else:
            #first move vertically, then horizontally
            self.__dig_v_tunnel(origin1y, origin2y, origin1x)
            self.__dig_h_tunnel(origin1x, origin2x, origin2y)

    def is_blocked(self, pos):
        x, y = pos

        #first test the map tile
        if self.tiles[x][y].blocked:
            return True

        #now check for any blocking monsters
        return (self.__get_monster_in_pos(pos) is not None)

    def __place_monsters_in_room(self, room):
        #choose random number of monsters
        num_monsters = random.randint(0, MAX_ROOM_MONSTERS)

        for i in range(num_monsters):
            #choose random spot for this monster
            (x, y) = room.get_random_point()

            if not self.is_blocked((x, y)):
                monster = MonsterFactory(x, y)
                self.add_monster(monster)

    def __place_items_in_room(self, room):
        #choose random number of items
        num_items = libtcod.random_get_int(0, 0, MAX_ROOM_ITEMS)

        for i in range(num_items):
            #choose random spot for this item
            (x, y) = room.get_random_point()

            #only place it if the tile is not blocked
            if not self.is_blocked((x, y)):
                item = ItemFactory(x, y)
                self.add_item(item)

    def __build_complete_room(self):
        #random width and height
        w = random.randint(ROOM_MIN_SIZE, ROOM_MAX_SIZE)
        h = random.randint(ROOM_MIN_SIZE, ROOM_MAX_SIZE)
        #random position without going out of the boundaries of the map
        x = random.randint(1, MAP_WIDTH - w - 1)
        y = random.randint(1, MAP_HEIGHT - h - 1)

        new_room = Room(x, y, w, h)

        #check if there are no intersections, so this room is valid
        if self.__room_overlaps(new_room):
            return None

        self.__dig_room(new_room)
        #self.__connect_with_previous_room(new_room)

        #append the new room to the list
        self.__add_room(new_room)

        return new_room

    def closest_unconnected_room(self, room):
        closest = None
        min_distance = MAP_WIDTH * MAP_HEIGHT

        unconnected_rooms = [r
                             for r in self.rooms
                             if r.connected is False and r is not room]

        for r in unconnected_rooms:
            distance = room.distance_to_room(r)

            if distance < min_distance:
                closest = r
                min_distance = distance

        return closest

    def generate(self):

        # build rooms
        for r in range(MAX_ROOMS):
            new_room = self.__build_complete_room()

            if new_room is not None:
                self.__place_items_in_room(new_room)
                self.__place_monsters_in_room(new_room)

        # connect rooms
        for r in self.rooms:
            if r.connected:
                continue

            closest = self.closest_unconnected_room(r)

            if closest:
                self.__connect_two_rooms(r,closest,"random")

            r.connected = True

        # start the player on a random position (not blocked)
        (x, y) = self.__random_unblocked_pos()
        self.player = controllers.creatures.Player(x, y)

    def __random_unblocked_pos(self):
        #choose random spot
        pos = (random.randint(1, MAP_WIDTH - 1),
               random.randint(1, MAP_HEIGHT - 1))

        if not self.is_blocked(pos):
            return pos

        return self.__random_unblocked_pos()

    def __get_monster_in_pos(self, pos):
        for monster in self.monsters:
            if monster.position == pos and monster.blocks:
                return monster

        return None

    def move_player(self, dx, dy):

        self.player.move(dx, dy)

        monster = self.__get_monster_in_pos(self.player.position)
        if monster is not None:
            self.player.attack(monster)
            self.player.move(-dx, -dy)

        if self.is_blocked(self.player.position):
            self.player.move(-dx, -dy)

        return self.player.position

    def closest_monster_to_player(self, max_range):
        #find closest enemy, up to a maximum range, and in the player's FOV
        closest_enemy = None
        closest_dist = max_range + 1

        for monster in self.monsters:
            #calculate distance between this object and the player
            dist = monster.distance_to(self.player)
            if dist < closest_dist:
                closest_enemy = monster
                closest_dist = dist

        return closest_enemy

    def take_item_from_player(self, item):
        self.model.player.drop_item(item)
        self.model.items.append(item)

    def give_item_to_player(self):
        for item in self.model.items:
            if item.position == self.model.player.position:
                if self.model.player.pick_item(item) is True:
                    self.model.items.remove(item)
