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
DRAW_EVENTS = Queue()
CLOSE_CLIENT = False
INVENTORY_ITEM = None


def loop(func):
    """ Run function passed as parameter until the game is closing. """
    while not CLOSE_CLIENT:
        func()


def handle_keys():
    global CLOSE_CLIENT
    key = wait_keypress()

    if key_is_escape(key):
        CLOSE_CLIENT = True
        return

    if INVENTORY_ITEM is not None:
        option = chr(key.c)
        # tell the draw thread to close the inventory window
        DRAW_EVENTS.put(('inventory-hide', None))
        # send chosen option to the game server
        if option in ObjectModel.action_names:
            SOCKET.send({ObjectModel.action_names[option]: INVENTORY_ITEM.key})
        return

    movement = get_key_direction(key)
    if movement is not None:
        SOCKET.send({'move': movement})
    elif chr(key.c) == 'g':
        SOCKET.send({'get': None})
    elif chr(key.c) == 'i':
        DRAW_EVENTS.put(('inventory-show', None))
        key = wait_keypress()
        item_key = chr(key.c)
        DRAW_EVENTS.put(('inventory-item', item_key))
    else:
        if chr(key.c) == 'v':
            DRAW_EVENTS.put(('toggle-fov', None))
        elif chr(key.c) in ('>', '<'):
            SOCKET.send({'climb': None})


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
        """ Handle data that was sent by the server. """
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
        global INVENTORY_ITEM
        """ Get a new event and process it. """
        if not DRAW_EVENTS.empty():
            event_name, event_data = DRAW_EVENTS.get()

            if event_name == 'toggle-fov':
                self.draw_not_in_fov = not self.draw_not_in_fov
                self.draw()
            elif event_name == 'inventory-show':
                header = "Press the key next to an item to choose it, or any other to cancel.\n"
                options = [(item.key, item.name) for item in self.player.inventory]
                self.main_window.show_menu(options, header, False)
            elif event_name == 'inventory-item':
                INVENTORY_ITEM = self.player.get_item(event_data)

                if INVENTORY_ITEM:
                    header = INVENTORY_ITEM.name + ":\n"
                    options = INVENTORY_ITEM.allowed_actions()
                    self.main_window.show_menu(options, header, True)
                else:
                    self.draw()
            elif event_name == 'inventory-hide':
                INVENTORY_ITEM = None
                self.draw()
            elif event_name == 'server-msg':
                self._handle_server_data(event_data)

            DRAW_EVENTS.task_done()


def recv_data():
    """ Receive data from the server and insert it into the events queue. """
    data = SOCKET.recv()
    if data:
        DRAW_EVENTS.put(('server-msg', data))


if __name__ == '__main__':
    ui_draw = UIDraw()

    Thread(target=loop, args=(recv_data,)).start()
    Thread(target=loop, args=(ui_draw.handle_event,)).start()
    Thread(target=loop, args=(handle_keys,)).start()

    # wait until game is closed
    import time
    while not CLOSE_CLIENT:
        time.sleep(0.1)

    # release resources
    SOCKET.close()
