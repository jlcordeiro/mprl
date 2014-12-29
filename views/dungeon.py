import libtcodpy as libtcod
from config import *
from collections import namedtuple
from views.objects import draw_object, erase_object

LevelColours = namedtuple('LevelColours', ['dark_wall',
                                           'light_wall',
                                           'dark_ground',
                                           'light_ground'])

DEFAULT_LEVEL_COLOURS = LevelColours(libtcod.Color(0, 0, 200),
                                     libtcod.Color(200, 200, 200),
                                     libtcod.Color(0, 0, 70),
                                     libtcod.Color(0, 25, 50))

FOREST_COLOURS = LevelColours(libtcod.Color(140, 180, 140),
                              libtcod.Color(180, 220, 180),
                              libtcod.Color(36,62,42),
                              libtcod.Color(26,42,32))

MINE_COLOURS = LevelColours(libtcod.Color(180, 140, 140),
                            libtcod.Color(220, 180, 180),
                            libtcod.desaturated_orange,
                            libtcod.darkest_red)

COLOURS = {"Town": DEFAULT_LEVEL_COLOURS, "Forest": FOREST_COLOURS, "Mines": MINE_COLOURS}

class Level:
    def __init__(self, model):
        self._bkgd = libtcod.BKGND_NONE
        self._model = model

    def draw(self, console, draw_not_in_fov=False):
        level = self._model.current_level

        colours = COLOURS[level.branch_name]

        #go through all tiles, and set their background color
        for y in range(MAP_HEIGHT):
            for x in range(MAP_WIDTH):
                wall = level.blocked[x][y]
                visible = libtcod.map_is_in_fov(level.fov_map, x, y)

                color = libtcod.black
                if visible or draw_not_in_fov:
                    color = colours.light_wall if wall else colours.light_ground
                elif level.explored[x][y]:
                    color = colours.dark_wall if wall else colours.dark_ground

                libtcod.console_set_char_background(console,
                                                    x,
                                                    y,
                                                    color,
                                                    libtcod.BKGND_SET)

        #draw stairs
        for s in level.stairs:
            if level.is_in_fov(s.position) or draw_not_in_fov:
                draw_object(console, s)

    def draw_name(self, console, x, y):
        level = self._model.current_level

        colours = COLOURS[level.branch_name]
        libtcod.console_set_default_foreground(console, colours.light_wall)
        libtcod.console_print_ex(console, x, y, libtcod.BKGND_NONE, libtcod.LEFT,
                                 str(level.name))

    def clear(self, console):
        level = self._model.current_level

        #erase the character that represents this object
        for s in level.stairs:
            (x, y) = s.position
            libtcod.console_put_char(console, x, y, ' ', self._bkgd)
