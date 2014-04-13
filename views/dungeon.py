import libtcodpy as libtcod
from config import *

color_none = libtcod.Color(0, 0, 0)
color_dark_wall = libtcod.Color(0, 0, 200)
color_light_wall = libtcod.Color(200, 200, 200)
color_dark_ground = libtcod.Color(0, 0, 70)
color_light_ground = libtcod.Color(0, 25, 50)


class Level:
    def __init__(self, model):
        self._bkgd = libtcod.BKGND_NONE
        self._model = model

    def __draw_items(self, console, draw_not_in_fov=False):
        level = self._model.current_level

        for item in level.items:
            (x, y) = item.position
            if libtcod.map_is_in_fov(level.fov_map, x, y) or draw_not_in_fov:
                item.draw_ui(console)

    def __draw_monsters(self, console, draw_dead=False, draw_not_in_fov=False):
        level = self._model.current_level

        #go through all monsters
        for monster in level.monsters:
            (x, y) = monster.position
            if libtcod.map_is_in_fov(level.fov_map, x, y) or draw_not_in_fov:
                if draw_dead == monster.died:
                    monster.draw_ui(console)

    def __draw_stairs(self, console, draw_not_in_fov=False):
        level = self._model.current_level

        for stairs in level.stairs:
            (x, y) = stairs.pos_i
            visible = libtcod.map_is_in_fov(level.fov_map, x, y)

            # draw stairs
            if visible or draw_not_in_fov:

                char = '<' if stairs.type == "STAIRS_UP" else '>'
                libtcod.console_put_char(console, x, y, char, self._bkgd)

    def draw(self, console, draw_not_in_fov=False):
        level = self._model.current_level

        #go through all tiles, and set their background color
        for y in range(MAP_HEIGHT):
            for x in range(MAP_WIDTH):
                wall = level.tiles[x][y].block_sight
                visible = libtcod.map_is_in_fov(level.fov_map, x, y)
                explored = level.tiles[x][y].explored

                color = color_none
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

        #draw stairs
        self.__draw_stairs(console, draw_not_in_fov)

        #and finally, the monsters that are still alive
        self.__draw_monsters(console, False, draw_not_in_fov)

        #draw temporary artifacts
        for artifact in level.temp_artifacts:
            x, y = artifact[0]
            libtcod.console_put_char(console, x, y, artifact[1], self._bkgd)

    def draw_name(self, console, x, y):
        level = self._model.current_level

        libtcod.console_set_default_foreground(console, level.theme_colour)
        libtcod.console_print_ex(console, x, y, libtcod.BKGND_NONE, libtcod.LEFT,
                                 str(level.name))

    def clear(self, console):
        level = self._model.current_level

        #erase the character that represents this object
        for s in level.stairs:
            (x, y) = s.pos_i
            libtcod.console_put_char(console, x, y, ' ', self._bkgd)

        #decrement the turns left for each temporary artifact
        #if it becomes 0, remove them
        for artifact in level.temp_artifacts:
            x, y = artifact[0]
            libtcod.console_put_char(console, x, y, ' ', self._bkgd)

        for monster in level.monsters:
            monster.clear_ui(console)

        for item in level.items:
            item.clear_ui(console)
