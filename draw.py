import libtcodpy as libtcod
from config import *
from platform.ui import *
from common.utilities.geometry import Rect
from views.objects import draw_object, erase_object

class Draw(object):
    def __init__(self):
        flags = libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD
        libtcod.console_set_custom_font('./resources/fonts/arial10x10.png', flags)
        libtcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, 'mprl', False)
        libtcod.sys_set_fps(LIMIT_FPS)

        self.con = libtcod.console_new(MAP_WIDTH, MAP_HEIGHT)
        self.panel = libtcod.console_new(SCREEN_WIDTH, PANEL_HEIGHT)

        self.hp_bar = UIBar('HP', libtcod.darker_red, libtcod.light_red)



    def flush(self, dungeon, player):
        #blit the contents of "console" to the root console
        libtcod.console_blit(self.con, 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, 0, 0, 0)

        #blit the contents of "panel" to the root console
        libtcod.console_blit(self.panel, 0, 0, SCREEN_WIDTH, PANEL_HEIGHT, 0, 0, PANEL_Y)

        libtcod.console_flush()
        dungeon.clear_ui(self.con)

#        for obj in monsters + items:
#            erase_object(self.con, obj)

        erase_object(self.con, player)

    def draw(self, dungeon, player, messages, draw_not_in_fov):
        #render the screen
        if draw_not_in_fov is True:
            is_in_fov_func = lambda pos: True
        else:
            is_in_fov_func = player.is_in_fov

        dungeon.draw_ui(self.con, is_in_fov_func)

        #draw stairs, then the items on the floor and finally, the monsters that are still alive
#        objects = items + monsters
#        for obj in objects:
#            if dungeon.is_in_fov(obj.position) or draw_not_in_fov:
#                draw_object(self.con, obj)

        draw_object(self.con, player)

        #prepare to render the GUI panel
        libtcod.console_set_default_background(self.panel, libtcod.black)
        libtcod.console_clear(self.panel)

        #draw level name
        dungeon.draw_name(self.panel, 1, 1)

        #show the player's stats
        self.hp_bar.update(player.hp, player.max_hp)
        self.hp_bar.draw(self.panel, Rect(1, 2, BAR_WIDTH, 1))

        libtcod.console_print_ex(self.panel, 1, 3, libtcod.BKGND_NONE, libtcod.LEFT,
                                 "Attack: " + str(player.power))

        libtcod.console_print_ex(self.panel, 1, 4, libtcod.BKGND_NONE, libtcod.LEFT,
                                 "Defense: " + str(player.defense))

        #print the game messages, one line at a time
#        y = 1
#        for (line, color) in messages.get_all():
#            libtcod.console_set_default_foreground(self.panel, color)
#            libtcod.console_print_ex(self.panel, MSG_X, y,
#                                     libtcod.BKGND_NONE, libtcod.LEFT,
#                                     line)
#            y += 1

        self.flush(dungeon, player)
