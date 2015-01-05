""" Module to wrap UI interfaces and hide it from the game. """

import libtcodpy as libtcod
from config import *

ITEM_TYPE_OPTIONS = {
        "cast": [('u', "(U)se"), ('d', "(D)rop")],
        "melee": [('r', "Equip in (r)ight hand"), ('l', "Equip in (l)eft hand"), ('d', "(D)rop")],
        "armour": [('w', "(W)ear"), ('d', "(D)rop")]
        }

class UIBar(object):
    """ Class representing a horizontal bar. """
    def __init__(self, name, bg_colour, fg_colour, maximum = 0):
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
        self.text = "%s %s/%s" % (self.name, str(self.value), str(self.maximum))

    def draw(self, panel, bar_rect):
        """ Draw the bar. """

        x, y = bar_rect.top_left.coords
        width, height = bar_rect.width, bar_rect.height

        #first calculate the width of the bar
        bar_width = int(float(self.value) / self.maximum * width)

        #render the background first
        libtcod.console_set_default_background(panel, self.bg_colour)
        libtcod.console_rect(panel, x, y, width, height, False, libtcod.BKGND_SCREEN)

        #now render the bar on top
        libtcod.console_set_default_background(panel, self.fg_colour)
        libtcod.console_rect(panel, x, y, bar_width, height, False, libtcod.BKGND_SCREEN)

        #finally, some centered text with the values
        libtcod.console_set_default_foreground(panel, libtcod.white)
        libtcod.console_print_ex(panel, x + width / 2, y,
                                 libtcod.BKGND_NONE, libtcod.CENTER, self.text)


def show_menu(con, header, options, rect, hide_options = False):
    """ Show menu with header and options in the screen. """

    height = rect.bottom_right.y - rect.top_left.y
    width = rect.bottom_right.x - rect.top_left.x

    #calculate total height for the header (after auto-wrap)
    header_height = libtcod.console_get_height_rect(con, 0, 0, width,
                                                    height, header)

    needed_height = len(options) + header_height
    height = max(height, needed_height)

    #create an off-screen console that represents the menu's window
    window = libtcod.console_new(width, height)
    #print the header, with auto-wrap
    libtcod.console_set_default_foreground(window, libtcod.white)
    libtcod.console_print_rect_ex(window, 0, 0, width, height,
                                  libtcod.BKGND_NONE, libtcod.LEFT, header)

    #print all the options
    y = header_height
    for (option_key, option_text) in options:
        if hide_options is True:
            text = option_text
        else:
            text = '(' + option_key + ') ' + option_text
        libtcod.console_print_ex(window, 0, y,
                                 libtcod.BKGND_NONE, libtcod.LEFT, text)
        y += 1

    #blit the contents of "window" to the root console
    x, y = rect.top_left.coords
    libtcod.console_blit(window, 0, 0, width, height, 0, x, y, 1.0, 0.7)

def option_menu(con, rect, header, options, hide_options = False):
    show_menu(con, header, options, rect, hide_options)

    #wait for a key-press
    libtcod.console_flush()
    key = libtcod.console_wait_for_keypress(True)

    #convert the ASCII code to an index;
    valid_keys = [o[0] for o in options]

    #if it corresponds to an option, return it
    if chr(key.c) in valid_keys:
        return chr(key.c)

    return None

def inventory_menu(con, rect, header, player):
    #show a menu with each item of the inventory as an option
    items = player.inventory
    if len(items) == 0:
        messages.add('Inventory is empty.')
        return

    options = []
    for item in items:
        text = "(*) " + item.name if False else item.name #TODO: fix
        options.append((item.key, text))

    item_key = option_menu(con, rect, header, options)

    #if an item was chosen, return it
    if item_key is None:
        return None

    chosen_item = player.get_item(item_key)

    if chosen_item is None:
        return (None, None)

    #show a menu with each item of the inventory as an option
    option = option_menu(con, rect, chosen_item.name + ":\n",
                         ITEM_TYPE_OPTIONS[chosen_item.type], True)

    return (chosen_item, option)

