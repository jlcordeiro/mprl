import libtcodpy as libtcod
from draw import Draw
from config import *
from messages import *
from platform.ui import *
from platform.keyboard import *
from common.models.dungeon import Stairs, Level
from common.utilities.geometry import Point
import common.models.creatures
import controllers.creatures
import controllers.dungeon
import socket
import json

draw = Draw()
DRAW_NOT_IN_FOV = False

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Connect the socket to the port where the server is listening
server_address = ('localhost', 4446)
print 'connecting to %s port %s' % server_address
sock.connect(server_address)

messages = []
monsters = []
items = []

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

        levels = {}
        for idx, ldata in data['dungeon']['levels'].items():
            sdata = ldata['stairs']
            stairs = None
            if sdata is not None:
                stairs = Stairs(Point(sdata[0], sdata[1]), "stairs_down")

            levels[int(idx)] = Level(ldata['walls'], stairs)

        dungeon = controllers.dungeon.Dungeon(levels)

        (player_x, player_y) = data['player']['position']

        messages = data['messages']

        player = common.models.creatures.Player(dungeon, player_x, player_y)
#        player = common.models.creatures.Creature('player',
#                                                  player_x,
#                                                  player_y,
#                                                  data['player']['hp'],
#                                                  data['player']['defense'],
#                                                  data['player']['power'])

        player.update_fov()
        dungeon.update_explored(player)

        draw.draw(dungeon, player, monsters, items, messages, DRAW_NOT_IN_FOV)
finally:
    sock.close()

