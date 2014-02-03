""" Module to wrap UI interfaces and hide it from the game. """

import libtcodpy as libtcod

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

    def draw(self, panel, x, y, width):
        """ Draw the bar. """
        #first calculate the width of the bar
        bar_width = int(float(self.value) / self.maximum * width)

        #render the background first
        libtcod.console_set_default_background(panel, self.bg_colour)
        libtcod.console_rect(panel, x, y, width, 1, False, libtcod.BKGND_SCREEN)

        #now render the bar on top
        libtcod.console_set_default_background(panel, self.fg_colour)
        libtcod.console_rect(panel, x, y, bar_width, 1, False, libtcod.BKGND_SCREEN)

        #finally, some centered text with the values
        libtcod.console_set_default_foreground(panel, libtcod.white)
        libtcod.console_print_ex(panel, x + width / 2, y,
                                 libtcod.BKGND_NONE, libtcod.CENTER, self.text)


def menu(con, header, options, width, total_width, total_height):
    if len(options) > 26:
        raise ValueError('Cannot have a menu with more than 26 options.')

    #calculate total height for the header (after auto-wrap)
    header_height = libtcod.console_get_height_rect(con, 0, 0, width,
                                                    total_height, header)
    height = len(options) + header_height

    #create an off-screen console that represents the menu's window
    window = libtcod.console_new(width, height)

    #print the header, with auto-wrap
    libtcod.console_set_default_foreground(window, libtcod.white)
    libtcod.console_print_rect_ex(window, 0, 0, width, height,
                                  libtcod.BKGND_NONE, libtcod.LEFT,
                                  header)

    #print all the options
    y = header_height
    letter_index = ord('a')
    for option_text in options:
        text = '(' + chr(letter_index) + ') ' + option_text
        libtcod.console_print_ex(window, 0, y,
                                 libtcod.BKGND_NONE, libtcod.LEFT,
                                 text)
        y += 1
        letter_index += 1

    #blit the contents of "window" to the root console
    x = total_width / 2 - width / 2
    y = total_height / 2 - height / 2
    libtcod.console_blit(window, 0, 0, width, height, 0, x, y, 1.0, 0.7)

    #wait for a key-press
    libtcod.console_flush()
    key = libtcod.console_wait_for_keypress(True)

    #convert the ASCII code to an index;
    index = key.c - ord('a')
    #if it corresponds to an option, return it
    if index >= 0 and index < len(options):
        return index

    return None
