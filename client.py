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
import socket
import json
import time
from sockets import *
from threading import Thread

draw = Draw()
DRAW_NOT_IN_FOV = False

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Connect the socket to the port where the server is listening
server_address = ('localhost', 4446)
print 'connecting to %s port %s' % server_address
sock.connect(server_address)

dungeon = None
player = None
messages = []
monsters = []
items = []

def handle_keys():
    key = wait_keypress()

    if key_is_escape(key):
        return "exit"

    movement = get_key_direction(key)
    if movement is not None:
        json_data = {'move': movement}
        send_data = json.dumps(json_data)
        print ">> ", send_data
        sock.send(str(len(send_data)) + " " + send_data)

    elif chr(key.c) == 'g':
        #pick up an item
        give_item_to_player()
    else:
        if chr(key.c) == 'v':
            DRAW_NOT_IN_FOV = not DRAW_NOT_IN_FOV
        elif chr(key.c) in ('>', '<'):
            dungeon.climb_stairs(player.position)
            move_player(0, 0)

        return 'did-not-take-turn'


def recv_forever():
    global messages, monsters, items, dungeon, player
    while True:
        data = recv_json(sock)

        levels = {}
        for idx, ldata in data['dungeon']['levels'].items():
            sdata = ldata['stairs']
            stairs = None
            if sdata is not None:
                stairs = Stairs(Point2(sdata[0], sdata[1]), "stairs_down")

            levels[int(idx)] = Level(ldata['walls'], stairs)

        dungeon = controllers.dungeon.Dungeon(levels)

        (player_x, player_y, player_z) = data['player']['position']

        messages = data['messages']

        player = common.models.creatures.Player(dungeon, Point3(player_x, player_y, player_z))
        player.hp = data['player']['hp']
        player.update_fov()
        dungeon.update_explored(player)

        monsters = []
        json_monsters = data['monsters']
        for json_m in json_monsters:
            (x, y, z) = json_m['position']
            monster = controllers.creatures.MonsterFactory(Point3(x, y, z), type = json_m['name'])
            monster.hp = json_m['hp']
            monsters.append(monster)

        draw.draw(dungeon, player, monsters, items, messages, DRAW_NOT_IN_FOV)

RECV_THREAD = Thread(target = recv_forever, args = ())
RECV_THREAD.daemon = True
RECV_THREAD.start()

try:
    while True:
        player_action = handle_keys()
        if player_action == "exit":
            break
finally:
    sock.close()

