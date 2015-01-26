from draw import Draw
from config import *
from messages import *
from platform.ui import *
from platform.keyboard import *
from common.models.dungeon import Level
from common.models.creatures import Creature, Player
from common.models.objects import ObjectModel
import controllers.dungeon
from sockets import *
from threading import Thread

draw = Draw()
DRAW_NOT_IN_FOV = False

socket = TCPClient('localhost', 4446)


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
        (chosen_item, option) = inventory_menu(draw.con, header, player)
        if chosen_item is None:
            return 'did-not-take-turn'

        try:
            option_name = {'u': 'cast',
                           'd': 'drop',
                           'w': 'wear',
                           'r': 'use-right',
                           'l': 'use-left'}[option]
        except KeyError, ke:
            return 'did-not-take-turn'

        socket.send({option_name: chosen_item.key})

    else:
        if chr(key.c) == 'v':
            DRAW_NOT_IN_FOV = not DRAW_NOT_IN_FOV
        elif chr(key.c) in ('>', '<'):
            socket.send({'climb': None})

        return 'did-not-take-turn'


def recv_forever():
    dungeon = None
    player = None
    messages = []
    monsters = []
    items = []

    while True:
        data = socket.recv()
        if data is None:
            continue

        for key in ('dungeon', 'player', 'messages', 'monsters', 'items'):
            if key not in data.keys():
                continue

            value = data[key]
            if key == 'dungeon':
                levels = {int(i): Level(**d)
                          for i, d in value['levels'].items()}
                current_level = value['current_level']
                dungeon = controllers.dungeon.Dungeon(levels, current_level)
            elif key == 'player':
                player = Player.fromJson(dungeon, value)
            elif key == 'messages':
                messages = value
            elif key == 'monsters':
                monsters = [Creature(**m) for m in value]
            elif key == 'items':
                items = [ObjectModel(**i) for i in value]

        dungeon.update_explored(player)
        draw.draw(dungeon, player, monsters, items, messages, DRAW_NOT_IN_FOV)


RECV_THREAD = Thread(target=recv_forever, args=())
RECV_THREAD.daemon = True
RECV_THREAD.start()

try:
    while True:
        if handle_keys() == "exit":
            break
finally:
    socket.close()
