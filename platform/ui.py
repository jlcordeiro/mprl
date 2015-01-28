""" Module to wrap UI interfaces and hide it from the game. """

import libtcodpy as libtcod
from config import *
from platform.ui import *
from common.utilities.geometry import Rect
from views.objects import draw_object, erase_object

gap = (SCREEN_WIDTH - INVENTORY_WIDTH)
SCREEN_RECT = Rect(gap / 2, gap / 2, INVENTORY_WIDTH, SCREEN_HEIGHT - gap)


class UIBar(object):
    """ Class representing a horizontal bar. """
    def __init__(self, name, bg_colour, fg_colour, maximum=0):
        self.name = name
        self.bg_colour = bg_colour
        self.fg_colour = fg_colour

        self.value = None
        self.maximum = None
        self.text = None
        self.update(0, maximum)

    def update(self, value, maximum):
        """ Update bar values. """
        self.value = value
        self.maximum = maximum
        self.text = "%s %s/%s" % (self.name, str(value), str(maximum))

    def draw(self, panel, bar_rect):
        """ Draw the bar. """

        x, y, _ = bar_rect.top_left.coords
        width, height = bar_rect.width, bar_rect.height

        #first calculate the width of the bar
        bar_width = int(float(self.value) / self.maximum * width)

        #render the background first
        libtcod.console_set_default_background(panel, self.bg_colour)
        libtcod.console_rect(panel, x, y, width, height,
                             False, libtcod.BKGND_SCREEN)

        #now render the bar on top
        libtcod.console_set_default_background(panel, self.fg_colour)
        libtcod.console_rect(panel, x, y, bar_width, height,
                             False, libtcod.BKGND_SCREEN)

        #finally, some centered text with the values
        libtcod.console_set_default_foreground(panel, libtcod.white)
        libtcod.console_print_ex(panel, x + width / 2, y,
                                 libtcod.BKGND_NONE, libtcod.CENTER, self.text)


class MainWindow(object):
    font = './resources/fonts/arial10x10.png'

    def __init__(self):
        flags = libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD
        libtcod.console_set_custom_font(self.font, flags)
        libtcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, 'mprl', False)
        libtcod.sys_set_fps(LIMIT_FPS)

        self.con = libtcod.console_new(MAP_WIDTH, MAP_HEIGHT)
        self.panel = libtcod.console_new(SCREEN_WIDTH, PANEL_HEIGHT)
        self.inv_window = libtcod.console_new(MAP_WIDTH, MAP_HEIGHT)

        self.hp_bar = UIBar('HP', libtcod.darker_red, libtcod.light_red)

    def flush(self, dungeon, player, monsters, items):
        #blit the contents of "console" to the root console
        libtcod.console_blit(self.con, 0, 0,
                             SCREEN_WIDTH, SCREEN_HEIGHT, 0, 0, 0)

        #blit the contents of "panel" to the root console
        libtcod.console_blit(self.panel, 0, 0,
                             SCREEN_WIDTH, PANEL_HEIGHT, 0, 0, PANEL_Y)

        libtcod.console_flush()
        dungeon.clear_ui(self.con)

        for obj in monsters + items:
            erase_object(self.con, obj)

        erase_object(self.con, player)

    def draw(self, dungeon, player, monsters, items, messages, draw_not_fov):
        #render the screen
        if draw_not_fov is True:
            is_in_fov_func = lambda pos: True
        else:
            is_in_fov_func = player.is_in_fov

        dungeon.draw_ui(self.con, is_in_fov_func)

        objects = items + monsters
        for obj in objects:
            if player.is_in_fov(obj.position) or draw_not_fov:
                draw_object(self.con, obj)

        draw_object(self.con, player)

        #prepare to render the GUI panel
        libtcod.console_set_default_background(self.panel, libtcod.black)
        libtcod.console_clear(self.panel)

        #show the player's stats
        self.hp_bar.update(player.hp, player.max_hp)
        self.hp_bar.draw(self.panel, Rect(1, 2, BAR_WIDTH, 1))

        libtcod.console_print_ex(self.panel, 1, 3,
                                 libtcod.BKGND_NONE, libtcod.LEFT,
                                 "Attack: " + str(player.power))

        libtcod.console_print_ex(self.panel, 1, 4,
                                 libtcod.BKGND_NONE, libtcod.LEFT,
                                 "Defense: " + str(player.defense))

        #print the game messages, one line at a time
        y = 1
        for line in messages:
            libtcod.console_set_default_foreground(self.panel, libtcod.white)
            libtcod.console_print_ex(self.panel, MSG_X, y,
                                     libtcod.BKGND_NONE, libtcod.LEFT,
                                     line)
            y += 1

        self.flush(dungeon, player, monsters, items)

    def show_menu(self, options, header, hide_options=False):
        """ Show menu with header and options in the screen. """

        #calculate total height for the header (after auto-wrap)
        header_height = libtcod.console_get_height_rect(self.inv_window, 0, 0, MAP_WIDTH,
                                                        MAP_HEIGHT, header)

        #print the header, with auto-wrap
        libtcod.console_set_default_foreground(self.inv_window, libtcod.white)
        libtcod.console_print_rect_ex(self.inv_window, 0, 0, MAP_WIDTH, MAP_HEIGHT,
                                      libtcod.BKGND_NONE, libtcod.LEFT, header)

        #print all the options
        y = header_height
        for (option_key, option_text) in options:
            if hide_options is True:
                text = option_text
            else:
                text = '(' + option_key + ') ' + option_text
            libtcod.console_print_ex(self.inv_window, 0, y,
                                     libtcod.BKGND_NONE, libtcod.LEFT, text)
            y += 1

        #blit the contents of "self.inv_window" to the root console
        x, y, _ = SCREEN_RECT.top_left.coords
        libtcod.console_blit(self.inv_window, 0, 0, MAP_WIDTH, MAP_HEIGHT, 0, x, y, 1.0, 0.7)
        libtcod.console_flush()
        libtcod.console_clear(self.inv_window)
