import libtcodpy as libtcod
from config import *
from messages import *
from platform.ui import *
from platform.keyboard import *
from common.utilities.geometry import Rect, Point3, euclidean_distance
import controllers.creatures
import controllers.objects
import controllers.dungeon
import common.models.creatures
from controllers.creatures import attack
import time
import json
from sockets import *
from Queue import Queue
from threading import Thread
from draw import Draw

TCP_SERVER = TCPServer('localhost', 4446)

draw = Draw()

DRAW_NOT_IN_FOV = False

game_state = 'playing'
player_action = None

# start the player on a random position (not blocked)
dungeon = controllers.dungeon.Dungeon()
(x, y, z) = dungeon.random_unblocked_pos(depth = 0)
player = common.models.creatures.Player(dungeon, Point3(x, y, 0))

def generate_monsters():
    new_monsters = []

    for level_idx in xrange(0, NUM_LEVELS):
        for _ in xrange(0, MAX_LEVEL_MONSTERS):
            pos = dungeon.random_unblocked_pos(depth = level_idx)
            monster = controllers.creatures.MonsterFactory(pos)
            new_monsters.append(monster)

    return new_monsters

def generate_items():
    new_items = []

    for level_idx in xrange(0, NUM_LEVELS):
        for _ in xrange(0, MAX_LEVEL_ITEMS):
            pos = dungeon.random_unblocked_pos(depth = level_idx)
            item = controllers.objects.ItemFactory(pos)
            new_items.append(item)

    return new_items

monsters = generate_monsters()
items = generate_items()

def get_monster_in_pos(pos):
    for monster in monsters:
        if monster.position == pos and not monster.died:
            return monster

    return None

def move_player(dx, dy):
    old_pos = player.position
    new_pos = old_pos.add(Point3(dx, dy, 0))

    monster = get_monster_in_pos(new_pos)
    if monster is not None:
        attack(player, monster)
    elif not dungeon.is_blocked(new_pos):
        player.position = new_pos

    player.update_fov()
    dungeon.update_explored(player)

def take_turn_monster(monster):
    if monster.died:
        return

    previous_pos = monster.position

    if monster.confused_turns > 0:
        monster.confused_move()

        if (dungeon.is_blocked(monster.position) is False or
            get_monster_in_pos(monster.position) is not None):
            monster.position = previous_pos

        return

    #not confused

    #close enough, attack! (if the player is still alive.)
    if euclidean_distance(player.position, monster.position) < 2 and player.hp > 0:
        attack(monster, player)
        return

    #if the monster sees the player, update its target position
    if player.is_in_fov(monster.position):
        monster.target_pos = player.position

    if monster.target_pos not in (None, monster.position):
        #move towards player if far away
        if euclidean_distance(monster.position, monster.target_pos) >= 2:
            path = dungeon.get_path(monster.position, monster.target_pos)
            if path is not None:
                new_pos = Point3(path[0], path[1], monster.position.z)
                if not dungeon.is_blocked(new_pos):
                    monster.position = new_pos

def take_turn():
    dungeon.compute_path()

    level_monsters = [m for m in monsters if m.position.z == player.position.z]

    for monster in level_monsters:
        take_turn_monster(monster)

def take_item_from_player(item):
    messages = MessagesBorg()
    messages.add('You dropped a ' + item.name + '.')
    player.remove_item(item)
    item.position = player.position
    items.append(item)

def give_item_to_player():
    messages = MessagesBorg()
    for item in items:
        if item.position == player.position:
            if player.add_item(item) is True:
                messages.add('You picked up a ' + item.name + '! (' + item.key + ')')
                items.remove(item)
            else:
                messages.add('Your inventory is full, cannot pick up ' +
                         item.name + '.')

def closest_monster_to_pos(pos, monsters, max_range):
    level_monsters = [m for m in monsters if m.position.z == pos.z]
    #find closest enemy, up to a maximum range, and in the FOV
    if len(level_monsters) < 1:
        return None

    closest = min(level_monsters, key = lambda x: euclidean_distance(x.position, pos))
    if (closest is None or
        not player.is_in_fov(closest.position) or
        euclidean_distance(closest.position, pos) > max_range):
        return None

    return closest

gap = (SCREEN_WIDTH - INVENTORY_WIDTH)
SCREEN_RECT = Rect(gap/2, gap/2, INVENTORY_WIDTH, SCREEN_HEIGHT - gap)

def handle_keys():
    global DRAW_NOT_IN_FOV

    #turn-based
    key = wait_keypress()

    if key_is_escape(key):
        return "exit"

    if game_state == 'playing':
        #movement keys
        if chr(key.c) == 'i':
            header = "Press the key next to an item to choose it, or any other to cancel.\n"
            (chosen_item, option) = inventory_menu(con, SCREEN_RECT, header, player)

            if chosen_item is None:
                return

            if option == 'd':
                dungeon.take_item_from_player(chosen_item)
            elif chosen_item.type == "cast" and option == 'u':
                item_range = chosen_item.range
                affected_monsters = []

                if chosen_item.affects == 'closest':
                    closest_one = dungeon.closest_monster_to_player(item_range)
                    if closest_one is not None:
                        affected_monsters.append(closest_one)

                if chosen_item.use(player, affected_monsters) is True:
                    player.remove_item(chosen_item)

            elif chosen_item.type == "armour" and option == 'w':
                if chosen_item.type != "armour":
                    messages.add('You can\'t wear a ' + chosen_item.name + '.')
                else:
                    messages.add('You are now wearing a ' + chosen_item.name + '.')
                    player.armour = chosen_item
            elif chosen_item.type == "melee":
                messages.add('You equipped a ' + weapon.name + '.')
                if option == 'r':
                    player.weapon_right = chosen_item
                elif option == 'l':
                    player.weapon_left = chosen_item

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

#############################################
# Initialization & Main Loop
#############################################

move_player(0, 0)

messages = MessagesBorg()

message_queue = Queue()

def send_all():
    data = {}
    data['dungeon'] = dungeon._model.json()
    data['player'] = player.json()
    data['messages'] = messages.get_all()
    send_data = json.dumps(data)
    TCP_SERVER.broadcast(str(len(send_data)) + " " + send_data)

def recv_forever(put_queue):
    while True:
        TCP_SERVER.receive(put_queue)

        if not put_queue.empty():
            data = put_queue.get()
            print(data)
            if 'move' in data.keys():
                dx, dy = data['move']
                move_player(dx, dy)
            put_queue.task_done()

            draw.draw(dungeon, player, level_monsters, level_items, messages.get_all(), DRAW_NOT_IN_FOV)
            send_all()

RECV_THREAD = Thread(target = recv_forever, args = (message_queue,))
RECV_THREAD.daemon = True
RECV_THREAD.start()

while not libtcod.console_is_window_closed():
    level_monsters = [m for m in monsters if m.position.z == player.position.z]
    level_items = [i for i in items if i.position.z == player.position.z]

    draw.draw(dungeon, player, level_monsters, level_items, messages.get_all(), DRAW_NOT_IN_FOV)
    send_all()

    #handle keys and exit game if needed
    player_action = handle_keys()
    if player_action == "exit":
        break

    #let monsters take their turn
    if game_state == "playing" and player_action != 'did-not-take-turn':
        take_turn()

    if player.died and game_state != 'dead':
        messages.add("YOU DIED!")
        game_state = 'dead'

TCP_SERVER.close()
#RECV_THREAD.join()
