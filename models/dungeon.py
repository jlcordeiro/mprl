import math
import random
from config import *


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

    def __connect_two_rooms(self, room1, room2):
        (center1x, center1y) = room1.center
        (center2x, center2y) = room2.center

        #draw a coin (random number that is either 0 or 1)
        if random.choice([True, False]):
            #first move horizontally, then vertically
            self.__dig_h_tunnel(center1x, center2x, center1y)
            self.__dig_v_tunnel(center1y, center2y, center2x)
        else:
            #first move vertically, then horizontally
            self.__dig_v_tunnel(center1y, center2y, center1x)
            self.__dig_h_tunnel(center1x, center2x, center2y)

    def is_blocked(self, pos):
        x, y = pos

        #first test the map tile
        if self.tiles[x][y].blocked:
            return True

        #now check for any blocking monsters
        for monster in self.monsters:
            if monster.blocks and monster.position == pos:
                return True

        return False

    def build_complete_room(self):
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

    def connect_rooms(self):
        for r in self.rooms:
            if r.connected:
                continue

            closest = self.closest_unconnected_room(r)

            if closest:
                self.__connect_two_rooms(r,closest)

            r.connected = True