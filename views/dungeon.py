import libtcodpy as libtcod
from config import *
from collections import namedtuple
from views.objects import draw_object, erase_object

LevelColours = namedtuple('LevelColours', ['dark_wall',
                                           'light_wall',
                                           'dark_ground',
                                           'light_ground'])

LEVEL_COLOURS = LevelColours(libtcod.Color(0, 0, 200),
                             libtcod.Color(200, 200, 200),
                             libtcod.Color(0, 0, 70),
                             libtcod.Color(0, 25, 50))

class Level:
    background = libtcod.BKGND_NONE

    def __init__(self):
        pass

    def draw(self, console, level, is_in_fov_func):
        #go through all tiles, and set their background color
        for y in range(MAP_HEIGHT):
            for x in range(MAP_WIDTH):
                wall = level.is_blocked((x, y))
                visible = is_in_fov_func((x, y))

                color = libtcod.black
                if visible:
                    color = LEVEL_COLOURS.light_wall if wall else LEVEL_COLOURS.light_ground
                elif level.explored[x][y]:
                    color = LEVEL_COLOURS.dark_wall if wall else LEVEL_COLOURS.dark_ground

                libtcod.console_set_char_background(console,
                                                    x,
                                                    y,
                                                    color,
                                                    libtcod.BKGND_SET)

        #draw stairs
        stairs = level.stairs
        if stairs is not None and is_in_fov_func(stairs.position):
            draw_object(console, stairs)

    def draw_name(self, console, level, x, y):
        libtcod.console_set_default_foreground(console, LEVEL_COLOURS.light_wall)
        libtcod.console_print_ex(console, x, y, libtcod.BKGND_NONE, libtcod.LEFT,
                                 str(level.id))

    def clear(self, console, level):
        #erase the character that represents this object
        if level.stairs is not None:
            (x, y) = level.stairs.position
            libtcod.console_put_char(console, x, y, ' ', Level.background)
