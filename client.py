import libtcodpy as libtcod
from config import *
from messages import *
from platform.ui import *
from platform.keyboard import *
from common.utilities.geometry import Rect
import common.models.creatures
import controllers.creatures
import controllers.dungeon
import views.creatures
from views.dungeon import COLOURS

DRAW_NOT_IN_FOV = False

game_state = 'playing'
player_action = None

dungeon = controllers.dungeon.Dungeon()


HP_BAR = UIBar('HP', libtcod.darker_red, libtcod.light_red)

gap = (SCREEN_WIDTH - INVENTORY_WIDTH)
SCREEN_RECT = Rect(gap/2, gap/2, INVENTORY_WIDTH, SCREEN_HEIGHT - gap)


def flush():
    #blit the contents of "console" to the root console
    libtcod.console_blit(con, 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, 0, 0, 0)

    #blit the contents of "panel" to the root console
    libtcod.console_blit(panel, 0, 0, SCREEN_WIDTH, PANEL_HEIGHT, 0, 0, PANEL_Y)

    libtcod.console_flush()
    dungeon.clear_ui(con)

def draw_client(console, branch_name, blocked, draw_not_in_fov=False):
    colours = COLOURS[branch_name]

    #go through all tiles, and set their background color
    for y in range(MAP_HEIGHT):
        for x in range(MAP_WIDTH):
            wall = blocked[x][y]
            #visible = libtcod.map_is_in_fov(level.fov_map, x, y)
            visible = True

            color = libtcod.black
            if visible or draw_not_in_fov:
                color = colours.light_wall if wall else colours.light_ground
            #elif explored[x][y]:
            #    color = colours.dark_wall if wall else colours.dark_ground

            libtcod.console_set_char_background(console,
                                                x,
                                                y,
                                                color,
                                                libtcod.BKGND_SET)


def draw_everything(walls, player):
    #render the screen
    draw_client(con, "Town", walls, False)

    player_view = views.creatures.Player(player)
    player_view.draw(con)

    #prepare to render the GUI panel
    libtcod.console_set_default_background(panel, libtcod.black)
    libtcod.console_clear(panel)

    #draw level name
    #dungeon.draw_name(panel, 1, 1)

    #show the player's stats
    hp_rect = Rect(1, 2, BAR_WIDTH, 1)
    HP_BAR.update(player.hp, player.max_hp)
    HP_BAR.draw(panel, hp_rect)

    libtcod.console_print_ex(panel, 1, 3, libtcod.BKGND_NONE, libtcod.LEFT,
                             "Attack: " + str(player.power))

    libtcod.console_print_ex(panel, 1, 4, libtcod.BKGND_NONE, libtcod.LEFT,
                             "Defense: " + str(player.defense))

    #print the game messages, one line at a time
    #y = 1
    #for (line, color) in messages.get_all():
    #    libtcod.console_set_default_foreground(panel, color)
    #    libtcod.console_print_ex(panel, MSG_X, y,
    #                             libtcod.BKGND_NONE, libtcod.LEFT,
    #                             line)
    #    y += 1

    flush()

#############################################
# Initialization & Main Loop
#############################################

flags = libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD
libtcod.console_set_custom_font('./resources/fonts/arial10x10.png', flags)
libtcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, 'mprl', False)
libtcod.sys_set_fps(LIMIT_FPS)
con = libtcod.console_new(MAP_WIDTH, MAP_HEIGHT)
panel = libtcod.console_new(SCREEN_WIDTH, PANEL_HEIGHT)

#messages = MessagesBorg()
#messages.add('Welcome stranger!', libtcod.red)

import socket
import json
import sys

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect the socket to the port where the server is listening
server_address = ('localhost', 4446)
print 'connecting to %s port %s' % server_address
sock.connect(server_address)

try:
    while True:
        data_expected = None
        all_data = None
        while all_data is None or len(all_data) < data_expected:
            new_data = sock.recv(16)

            if data_expected is None:
                data_expected = int(new_data.split(' ')[0])
                all_data = " ".join(new_data.split(' ')[1:])
            else:
                all_data += new_data

        print ">> ", len(all_data)
        data = json.loads(all_data)

        (player_x, player_y) = data['player']['position']

        player = common.models.creatures.Creature('player',
                                                  player_x,
                                                  player_y,
                                                  data['player']['hp'],
                                                  data['player']['defense'],
                                                  data['player']['power'])

        draw_everything(data['dungeon']['walls'], player)
finally:
    sock.close()

