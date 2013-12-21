import libtcodpy as libtcod
from config import *

color_black = libtcod.Color(0, 0, 0)
color_dark_wall = libtcod.Color(0, 0, 100)
color_light_wall = libtcod.Color(130, 110, 50)
color_dark_ground = libtcod.Color(50, 50, 150)
color_light_ground = libtcod.Color(200, 180, 50)


class Level:
    def __init__(self, model):
        self.model = model
        self.fov_map = libtcod.map_new(MAP_WIDTH, MAP_HEIGHT)

    def __draw_items(self, console, draw_not_in_fov=False):
        for item in self.model.items:
            (x, y) = item.position
            if libtcod.map_is_in_fov(self.fov_map, x, y) or draw_not_in_fov:
                item.view.draw(console)

    def __draw_monsters(self, console, draw_dead=False, draw_not_in_fov=False):
        #go through all monsters
        for monster in self.model.monsters:
            (x, y) = monster.position
            if libtcod.map_is_in_fov(self.fov_map, x, y) or draw_not_in_fov:
                if draw_dead == monster.died:
                    monster.view.draw(console)

    def draw(self, console, draw_not_in_fov=False):
        #go through all tiles, and set their background color
        for y in range(MAP_HEIGHT):
            for x in range(MAP_WIDTH):
                wall = self.model.tiles[x][y].block_sight
                visible = libtcod.map_is_in_fov(self.fov_map, x, y)
                explored = self.model.tiles[x][y].explored

                color = color_black
                if visible or draw_not_in_fov:
                    color = color_light_wall if wall else color_light_ground
                elif explored:
                    color = color_dark_wall if wall else color_dark_ground

                libtcod.console_set_char_background(console,
                                                    x,
                                                    y,
                                                    color,
                                                    libtcod.BKGND_SET)

        # start by drawing the monsters that have died
        self.__draw_monsters(console, True, draw_not_in_fov)

        #then the items on the floor
        self.__draw_items(console, draw_not_in_fov)

        #and finally, the monsters that are still alive
        self.__draw_monsters(console, False, draw_not_in_fov)
