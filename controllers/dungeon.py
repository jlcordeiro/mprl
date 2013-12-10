import libtcodpy as libtcod
import random
import views.dungeon
import models.dungeon
from items import ItemFactory
from creatures import MonsterFactory
from config import *


class Level:
    def __init__(self):
        self.model = models.dungeon.Level()
        self.view = views.dungeon.Level(self.model)

        for r in range(MAX_ROOMS):
            new_room = self.model.build_complete_room()

            if new_room is not None:
                self.__place_items_in_room(new_room)
                self.__place_monsters_in_room(new_room)

                #append the new room to the list
                self.model.add_room(new_room)

        self.set_fov()

    def __place_monsters_in_room(self, room):
        #choose random number of monsters
        num_monsters = random.randint(0, MAX_ROOM_MONSTERS)

        for i in range(num_monsters):
            #choose random spot for this monster
            (x, y) = room.get_random_point()

            if not self.is_blocked((x, y)):
                monster = MonsterFactory(x, y)
                self.model.add_monster(monster)

    def __place_items_in_room(self, room):
        #choose random number of items
        num_items = libtcod.random_get_int(0, 0, MAX_ROOM_ITEMS)

        for i in range(num_items):
            #choose random spot for this item
            (x, y) = room.get_random_point()

            #only place it if the tile is not blocked
            if not self.is_blocked((x, y)):
                item = ItemFactory(x, y)
                self.model.add_item(item)

    def update(self, pos):
        x, y = pos
        libtcod.map_compute_fov(self.view.fov_map,
                                x,
                                y,
                                TORCH_RADIUS,
                                FOV_LIGHT_WALLS,
                                FOV_ALGO)

        for y in range(MAP_HEIGHT):
            for x in range(MAP_WIDTH):
                if libtcod.map_is_in_fov(self.view.fov_map, x, y):
                    self.model.tiles[x][y].explored = True

    def get_unblocked_pos(self):
        #choose random spot
        x = random.randint(1, MAP_WIDTH - 1)
        y = random.randint(1, MAP_HEIGHT - 1)

        if not self.is_blocked((x, y)):
            return (x, y)

        return self.get_unblocked_pos()

    def is_blocked(self, pos):
        return self.model.is_blocked(pos)

    def set_fov(self):
        for y in range(MAP_HEIGHT):
            for x in range(MAP_WIDTH):
                isTransparent = not self.model.tiles[x][y].block_sight
                isWalkable = not self.model.tiles[x][y].blocked
                libtcod.map_set_properties(self.view.fov_map,
                                           x,
                                           y,
                                           isTransparent,
                                           isWalkable)
