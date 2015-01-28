""" Game client. """

from platform.ui import *
from platform.keyboard import *
from common.models.dungeon import Level
from common.models.objects import ObjectModel
from common.models.creatures import Creature, Player
import controllers.dungeon
from sockets import TCPClient
from threading import Thread, Event
from Queue import Queue

main_window = MainWindow()

socket = TCPClient('localhost', 4446)

events = Queue()
CLOSE_CLIENT = False

ITEM_TYPE_OPTIONS = {"cast": [('u', "(U)se"),
                              ('d', "(D)rop")],
                     "melee": [('r', "Equip in (r)ight hand"),
                               ('l', "Equip in (l)eft hand"),
                               ('d', "(D)rop")],
                     "armour": [('w', "(W)ear"),
                                ('d', "(D)rop")]
                     }

OPTION_NAMES = {'u': 'cast',
                'd': 'drop',
                'w': 'wear',
                'r': 'use-right',
                'l': 'use-left'}


def handle_keys():
    global CLOSE_CLIENT
    while not CLOSE_CLIENT:
        key = wait_keypress()

        if key_is_escape(key):
            CLOSE_CLIENT = True
            return

        movement = get_key_direction(key)
        if movement is not None:
            socket.send({'move': movement})
        elif chr(key.c) == 'g':
            socket.send({'get': None})
        elif chr(key.c) == 'i':
            events.put(('inventory-show',))
            key = wait_keypress()
            item_key = chr(key.c)
            events.put(('inventory-item', item_key))
            key = wait_keypress()
            option = chr(key.c)
            events.put(('inventory-hide',))

            if option in OPTION_NAMES:
                socket.send({OPTION_NAMES[option]: item_key})
        else:
            if chr(key.c) == 'v':
                events.put(('toggle-fov',))
            elif chr(key.c) in ('>', '<'):
                socket.send({'climb': None})

            return 'did-not-take-turn'


def ui_draw():
    global main_window

    dungeon = None
    player = None
    messages = []
    monsters = []
    items = []
    draw_not_in_fov = False

    while not CLOSE_CLIENT:
        if not events.empty():
            event = events.get()

            if event[0] == 'toggle-fov':
                draw_not_in_fov = not draw_not_in_fov
                main_window.draw(dungeon, player, monsters, items, messages, draw_not_in_fov)
            elif event[0] == 'inventory-show':
                header = "Press the key next to an item to choose it, or any other to cancel.\n"
                options = [(item.key, item.name) for item in player.inventory]
                main_window.show_menu(options, header, False)
            elif event[0] == 'inventory-item':
                item_key = event[1]
                item = player.get_item(item_key)

                if item:
                    header = item.name + ":\n"
                    options = ITEM_TYPE_OPTIONS[item.type]
                    main_window.show_menu(options, header, True)
            elif event[0] == 'inventory-hide':
                main_window.draw(dungeon, player, monsters, items, messages, draw_not_in_fov)
            elif event[0] == 'server-msg':
                data = event[1]
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
                        player = Player.fromJson(value)
                        player.update_fov(dungeon.is_blocked)
                    elif key == 'messages':
                        messages = value
                    elif key == 'monsters':
                        monsters = [Creature(**m) for m in value]
                    elif key == 'items':
                        items = [ObjectModel(**i) for i in value]

                dungeon.update_explored(player)
                main_window.draw(dungeon, player, monsters, items, messages, draw_not_in_fov)

            events.task_done()


def recv_forever():
    while not CLOSE_CLIENT:
        data = socket.recv()
        if data is None:
            continue

        events.put(('server-msg', data))


Thread(target=recv_forever, args=()).start()
Thread(target=ui_draw, args=()).start()
Thread(target=handle_keys(), args=()).start()

import time

try:
    while not CLOSE_CLIENT:
        time.sleep(1)
finally:
    socket.close()
