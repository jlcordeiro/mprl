import libtcodpy as libtcod
from draw import Draw
from config import *
from messages import *
from platform.ui import *
from platform.keyboard import *
from common.models.dungeon import Stairs, Level
from common.utilities.geometry import Rect, Point2, Point3
import common.models.creatures
import controllers.creatures
import controllers.dungeon
import json
from sockets import *
from threading import Thread

draw = Draw()
DRAW_NOT_IN_FOV = False

socket = TCPClient('localhost', 4446)

gap = (SCREEN_WIDTH - INVENTORY_WIDTH)
SCREEN_RECT = Rect(gap / 2, gap / 2, INVENTORY_WIDTH, SCREEN_HEIGHT - gap)

dungeon = None
player = None
messages = []
monsters = []
items = []


def handle_keys():
    global DRAW_NOT_IN_FOV
    key = wait_keypress()

    if key_is_escape(key):
        return "exit"

    movement = get_key_direction(key)
    if movement is not None:
        socket.send({'move': movement})
    elif chr(key.c) == 'g':
        #pick up an item
        socket.send({'get': None})
    elif chr(key.c) == 'i':
        header = "Press the key next to an item to choose it, or any other to cancel.\n"
        (chosen_item, option) = inventory_menu(draw.con, SCREEN_RECT, header, player)
        if chosen_item is None:
            return 'did-not-take-turn'

        if option == 'd':
            socket.send({'drop': chosen_item.key})
        else:
            socket.send({'use': chosen_item.key})

    else:
        if chr(key.c) == 'v':
            DRAW_NOT_IN_FOV = not DRAW_NOT_IN_FOV
        elif chr(key.c) in ('>', '<'):
            socket.send({'climb': None})

        return 'did-not-take-turn'


def recv_forever():
    global messages, monsters, items, dungeon, player
    while True:
        data = socket.recv()

        levels = {}
        for idx, ldata in data['dungeon']['levels'].items():
            sdata = ldata['stairs']
            stairs = None
            if sdata is not None:
                stairs = Stairs(Point2(sdata[0], sdata[1]), "stairs_down")

            levels[int(idx)] = Level(ldata['walls'], stairs, ldata['explored'])

        current_level = data['dungeon']['current_level']
        dungeon = controllers.dungeon.Dungeon(levels, current_level)

        (player_x, player_y, player_z) = data['player']['position']

        player = common.models.creatures.Player(dungeon, (player_x, player_y, player_z))
        player.hp = data['player']['hp']
        player.inventory = [common.models.objects.ObjectModel(**i) for i in data['player']['items']]
        player.update_fov()
        dungeon.update_explored(player)

        messages = data['messages']

        monsters = [common.models.creatures.Creature(**m) for m in data['monsters']]
        level_monsters = [m for m in monsters if m.position.z == player_z]

        items = [common.models.objects.ObjectModel(**i) for i in data['items']]
        level_items = [i for i in items if i.position.z == player.position.z]

        draw.draw(dungeon, player, level_monsters, level_items, messages, DRAW_NOT_IN_FOV)

RECV_THREAD = Thread(target=recv_forever, args=())
RECV_THREAD.daemon = True
RECV_THREAD.start()

try:
    while True:
        player_action = handle_keys()
        if player_action == "exit":
            break
finally:
    socket.close()
