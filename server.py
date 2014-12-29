import libtcodpy as libtcod
from config import *
from messages import *
from platform.ui import *
from platform.keyboard import *
from common.utilities.geometry import Rect
from common.utilities.geometry import Point
import controllers.creatures
import controllers.dungeon
import common.models.creatures
from controllers.creatures import attack
import time
import json
from sockets import TCPServer
from Queue import Queue
from threading import Thread
from views.objects import draw_object, erase_object

TCP_SERVER = TCPServer('localhost', 4446)

DRAW_NOT_IN_FOV = False

game_state = 'playing'
player_action = None

dungeon = controllers.dungeon.Dungeon()

# start the player on a random position (not blocked)
(x, y) = dungeon.random_unblocked_pos()
player = common.models.creatures.Player(x, y)

items = []
monsters = []

def move_player(dx, dy):
    old_pos = player.position
    new_pos = old_pos.add(Point(dx, dy))

    monster = None # TODO: monster = dungeon.get_monster_in_pos(new_pos)
    if monster is not None:
        attack(player, monster)
    elif not dungeon.is_blocked(new_pos):
        player.position = new_pos

    dungeon.update_fov(player.position)


def take_turn_monster(monster):
    if monster.died:
        return

    previous_pos = monster.position

    if monster.confused_turns > 0:
        monster.confused_move()

        if dungeon.is_blocked(monster.position) is False:
            monster.position = previous_pos

        return

    #not confused

    #close enough, attack! (if the player is still alive.)
    if euclidean_distance(player.position, monster.position) < 2 and player.hp > 0:
        attack(monster, player)
        return

    #if the monster sees the player, update its target position
    if dungeon.is_in_fov(monster.position):
        monster.target_pos = player.position

    if monster.target_pos not in (None, monster.position):
        #move towards player if far away
        if euclidean_distance(monster.position, monster.target_pos) >= 2:
            path = dungeon.get_path(monster.position, monster.target_pos)
            if path is not None and not dungeon.is_blocked(path):
                monster.position = Point(path[0], path[1])

def take_turn():
    dungeon.compute_path()

    for monster in monsters:
        take_turn_monster(monster)

def take_item_from_player(item):
    messages = MessagesBorg()
    messages.add('You dropped a ' + item.name + '.', libtcod.yellow)
    player.remove_item(item)
    item.position = player.position
    items.append(item)

def give_item_to_player():
    messages = MessagesBorg()
    for item in items:
        if item.position == player.position:
            if player.add_item(item) is True:
                messages.add('You picked up a ' + item.name + '! (' + item.key + ')', libtcod.green)
                items.remove(item)
            else:
                messages.add('Your inventory is full, cannot pick up ' +
                         item.name + '.', libtcod.red)

def closest_monster_to_pos(pos, monsters, max_range):
    #find closest enemy, up to a maximum range, and in the FOV
    if len(monsters) < 1:
        return None

    closest = min(monsters, key = lambda x: euclidean_distance(x.position, pos))
    if (closest is None or
        not dungeon.is_in_fov(closest.position) or
        euclidean_distance(closest.position, pos) > max_range):
        return None

    return closest


HP_BAR = UIBar('HP', libtcod.darker_red, libtcod.light_red)

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
        movement = get_key_direction(key)
        if movement is not None:
            dx, dy = movement
            move_player(dx, dy)

        elif chr(key.c) == 'i':
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
                    messages.add('You can\'t wear a ' + chosen_item.name + '.', libtcod.red)
                else:
                    messages.add('You are now wearing a ' + chosen_item.name + '.', libtcod.green)
                    player.armour = chosen_item
            elif chosen_item.type == "melee":
                messages.add('You equipped a ' + weapon.name + '.', libtcod.green)
                if option == 'r':
                    player.weapon_right = chosen_item
                elif option == 'l':
                    player.weapon_left = chosen_item

        elif chr(key.c) == 'g':
            #pick up an item
            dungeon.give_item_to_player()
        else:
            if chr(key.c) == 'v':
                DRAW_NOT_IN_FOV = not DRAW_NOT_IN_FOV
            elif chr(key.c) in ('>', '<'):
                dungeon.climb_stairs(player.position)
                move_player(0, 0)

            return 'did-not-take-turn'

def flush():
    #blit the contents of "console" to the root console
    libtcod.console_blit(con, 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, 0, 0, 0)

    #blit the contents of "panel" to the root console
    libtcod.console_blit(panel, 0, 0, SCREEN_WIDTH, PANEL_HEIGHT, 0, 0, PANEL_Y)

    libtcod.console_flush()
    dungeon.clear_ui(con)

    for obj in monsters + items:
        erase_object(con, obj)

    erase_object(con, player)

def draw_everything():
    #render the screen

    dungeon.draw_ui(con, DRAW_NOT_IN_FOV)

    #draw stairs, then the items on the floor and finally, the monsters that are still alive
    objects = items + monsters
    for obj in objects:
        if dungeon.is_in_fov(obj.position) or DRAW_NOT_IN_FOV:
            draw_object(con, obj)

    draw_object(con, player)

    #prepare to render the GUI panel
    libtcod.console_set_default_background(panel, libtcod.black)
    libtcod.console_clear(panel)

    #draw level name
    dungeon.draw_name(panel, 1, 1)

    #show the player's stats
    hp_rect = Rect(1, 2, BAR_WIDTH, 1)
    HP_BAR.update(player.hp, player.max_hp)
    HP_BAR.draw(panel, hp_rect)

    libtcod.console_print_ex(panel, 1, 3, libtcod.BKGND_NONE, libtcod.LEFT,
                             "Attack: " + str(player.power))

    libtcod.console_print_ex(panel, 1, 4, libtcod.BKGND_NONE, libtcod.LEFT,
                             "Defense: " + str(player.defense))

    #print the game messages, one line at a time
    y = 1
    for (line, color) in messages.get_all():
        libtcod.console_set_default_foreground(panel, color)
        libtcod.console_print_ex(panel, MSG_X, y,
                                 libtcod.BKGND_NONE, libtcod.LEFT,
                                 line)
        y += 1

    flush()

    level = dungeon._model.current_level

    data = {}
    data['dungeon'] = {}
    data['dungeon']['walls'] = [[1 if b else 0 for b in row] for row in level.blocked]
    data['dungeon']['stairs'] = [str(stairs) for stairs in dungeon._model.current_level.stairs]
    data['player'] = player.json()
#    print "+++"
#    for stairs in dungeon._model.current_level.stairs:
#        print str(stairs)

#    print str({'monsters': [m.json() for m in level.monsters]})
#    print str({'items': [i.json() for i in level.items]})

#    print str({'walls': [[1 if b else 0 for b in row] for row in level.blocked]})
#    print str({'explored': [[1 if e else 0 for e in row] for row in explored]})
#    print level.fov_map

#    print str(messages.get_all())
#    print "---"

#    send_data = json.dumps(data)
#    TCP_SERVER.broadcast(str(len(send_data)) + " " + send_data)

#############################################
# Initialization & Main Loop
#############################################

flags = libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD
libtcod.console_set_custom_font('./resources/fonts/arial10x10.png', flags)
libtcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, 'mprl', False)
libtcod.sys_set_fps(LIMIT_FPS)
con = libtcod.console_new(MAP_WIDTH, MAP_HEIGHT)
panel = libtcod.console_new(SCREEN_WIDTH, PANEL_HEIGHT)

move_player(0, 0)

messages = MessagesBorg()
messages.add('Welcome stranger!', libtcod.red)

message_queue = Queue()

def recv_forever(put_queue):
    while True:
        TCP_SERVER.receive(put_queue)
        time.sleep(1)

RECV_THREAD = Thread(target = recv_forever, args = (message_queue,))
RECV_THREAD.daemon = True
RECV_THREAD.start()

while not libtcod.console_is_window_closed():
    draw_everything()

    #handle keys and exit game if needed
    player_action = handle_keys()
    if player_action == "exit":
        break

    #let monsters take their turn
    if game_state == "playing" and player_action != 'did-not-take-turn':
        take_turn()

    if player.died and game_state != 'dead':
        messages.add("YOU DIED!", libtcod.red)
        game_state = 'dead'

TCP_SERVER.close()
#RECV_THREAD.join()
