""" Game client. """

from platform.ui import *
from platform.keyboard import *
from common.models.dungeon import Level
from common.models.objects import ObjectModel
from common.models.creatures import Creature, Player
from controllers.dungeon import Dungeon
from sockets import TCPClient
from threading import Thread
from Queue import Queue

## Variables shared by all threads
SOCKET = TCPClient('localhost', 4446)
EVENTS = Queue()
CLOSE_CLIENT = False


def loop(func):
    """ Run function passed as parameter until the game is closing. """
    while not CLOSE_CLIENT:
        func()

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
    key = wait_keypress()

    if key_is_escape(key):
        CLOSE_CLIENT = True
        return

    movement = get_key_direction(key)
    if movement is not None:
        SOCKET.send({'move': movement})
    elif chr(key.c) == 'g':
        SOCKET.send({'get': None})
    elif chr(key.c) == 'i':
        EVENTS.put(('inventory-show',))
        key = wait_keypress()
        item_key = chr(key.c)
        EVENTS.put(('inventory-item', item_key))
        key = wait_keypress()
        option = chr(key.c)
        EVENTS.put(('inventory-hide',))

        if option in OPTION_NAMES:
            SOCKET.send({OPTION_NAMES[option]: item_key})
    else:
        if chr(key.c) == 'v':
            EVENTS.put(('toggle-fov',))
        elif chr(key.c) in ('>', '<'):
            SOCKET.send({'climb': None})

        return 'did-not-take-turn'


class UIDraw(object):
    def __init__(self):
        self.main_window = MainWindow()

        self.dungeon = None
        self.player = None
        self.messages = []
        self.monsters = []
        self.items = []
        self.draw_not_in_fov = False

    def draw(self):
        """ Draw main game window. """
        self.main_window.draw(self.dungeon, self.player, self.monsters,
                              self.items, self.messages, self.draw_not_in_fov)

    def _handle_server_data(self, data):
        for key in ('dungeon', 'player', 'messages', 'monsters', 'items'):
            if key not in data.keys():
                continue

            value = data[key]
            if key == 'dungeon':
                levels = {int(i): Level(**d)
                          for i, d in value['levels'].items()}
                current_level = value['current_level']
                self.dungeon = Dungeon(levels, current_level)
            elif key == 'player':
                self.player = Player.fromJson(value)
                self.player.update_fov(self.dungeon.is_blocked)
            elif key == 'messages':
                self.messages = value
            elif key == 'monsters':
                self.monsters = [Creature(**m) for m in value]
            elif key == 'items':
                self.items = [ObjectModel(**i) for i in value]

        self.dungeon.update_explored(self.player)
        self.draw()

    def handle_event(self):
        if not EVENTS.empty():
            event_name, event_data = EVENTS.get()

            if event_name == 'toggle-fov':
                self.draw_not_in_fov = not self.draw_not_in_fov
                self.draw()
            elif event_name == 'inventory-show':
                header = "Press the key next to an item to choose it, or any other to cancel.\n"
                options = [(item.key, item.name) for item in self.player.inventory]
                self.main_window.show_menu(options, header, False)
            elif event_name == 'inventory-item':
                item = self.player.get_item(event_data)

                if item:
                    header = item.name + ":\n"
                    options = ITEM_TYPE_OPTIONS[item.type]
                    self.main_window.show_menu(options, header, True)
            elif event_name == 'inventory-hide':
                self.draw()
            elif event_name == 'server-msg':
                self._handle_server_data(event_data)

            EVENTS.task_done()


def recv_data():
    data = SOCKET.recv()
    if data:
        EVENTS.put(('server-msg', data))


if __name__ == '__main__':
    ui_draw = UIDraw()

    Thread(target=loop, args=(recv_data,)).start()
    Thread(target=loop, args=(ui_draw.handle_event,)).start()
    Thread(target=loop, args=(handle_keys,)).start()

    import time

    try:
        while not CLOSE_CLIENT:
            time.sleep(1)
    finally:
        SOCKET.close()
