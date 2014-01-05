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

        self.model.generate()
        self.set_fov()

    def move_player(self, dx, dy):
        x, y = self.model.move_player(dx, dy)

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

    def clear_ui(self, con):
        self.model.player.view.clear(con)

        for monster in self.model.monsters:
            monster.view.clear(con)

        for item in self.model.items:
            item.view.clear(con)

    def draw_ui(self, con, draw_outside_fov):
        self.view.draw(con, draw_outside_fov)
        self.model.player.view.draw(con)

    def closest_monster_to_player_in_fov(self, max_range):
        closest_enemy = self.model.closest_monster_to_player(max_range)

        if closest_enemy is None:
            return None

        x, y = closest_enemy.position
        if libtcod.map_is_in_fov(self.view.fov_map, x, y):
            return closest_enemy

        return None 

    @property
    def player(self):
        return self.model.player
