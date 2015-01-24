from random import randint
from config import *
from messages import Messages
from common.utilities.geometry import Point, euclidean_distance
import controllers.creatures
import controllers.objects
import controllers.dungeon
import common.models.creatures
from sockets import TCPServer
from Queue import Queue

TCP_SERVER = TCPServer('localhost', 4446)

# start the player on a random position (not blocked)
dungeon = controllers.dungeon.Dungeon()
messages = Messages()

def random_unblocked_pos(objects, depth=None):
    if depth is None:
        depth = dungeon.depth

    pos = Point(randint(1, MAP_WIDTH - 1),
                randint(1, MAP_HEIGHT - 1),
                depth)

    existing_objects = [o for o in objects if o.position == pos]
    if not dungeon.is_blocked(pos) and len(existing_objects) == 0:
        return pos

    return random_unblocked_pos(objects, depth)

def generate_monsters():
    new_monsters = []

    for level_idx in xrange(0, NUM_LEVELS):
        for _ in xrange(0, MAX_LEVEL_MONSTERS):
            pos = random_unblocked_pos(new_monsters, depth=level_idx)
            monster = controllers.objects.create_random_monster(pos)
            new_monsters.append(monster)

    return new_monsters


def generate_items():
    new_items = []

    for level_idx in xrange(0, NUM_LEVELS):
        for _ in xrange(0, MAX_LEVEL_ITEMS):
            pos = random_unblocked_pos(new_items, depth=level_idx)
            item = controllers.objects.create_random_item(pos)
            new_items.append(item)

    return new_items


def use_healing_potion(player):
    messages.add('Your wounds start to feel better!')
    player.hp += HEAL_AMOUNT

ppos = random_unblocked_pos([], depth=0)
player = common.models.creatures.Player(dungeon, ppos)
monsters = generate_monsters()
items = generate_items()


def attack(source, target):
    damage = max(0, source.power - target.defense)
    target.hp -= damage

    messages.add(source.name + ' attacks ' + target.name + ' for '
                 + str(damage) + ' hit points.')


def get_monster_in_pos(pos):
    for monster in monsters:
        if monster.position == pos and not monster.died:
            return monster

    return None


def move_player(dx, dy, dz=0):
    old_pos = player.position
    new_pos = old_pos.add(Point(dx, dy, dz))

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
        randx, randy = randint(-1, 1), randint(-1, 1)
        monster.position = monster.position.add(randx, randy)
        monster.confused_turns -= 1

        if (dungeon.is_blocked(monster.position) is False or
                get_monster_in_pos(monster.position) is not None):
            monster.position = previous_pos

        return

    #not confused

    #close enough, attack! (if the player is still alive.)
    if (euclidean_distance(player.position, monster.position) < 2 and
            player.hp > 0):
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
                new_pos = Point(path[0], path[1], monster.position.z)
                if not dungeon.is_blocked(new_pos) and get_monster_in_pos(new_pos) is None:
                    monster.position = new_pos


def take_turn():
    dungeon.compute_path()

    level_monsters = [m for m in monsters if m.position.z == player.position.z]

    for monster in level_monsters:
        take_turn_monster(monster)


def take_item_from_player(item):
    messages.add('You dropped a ' + item.name + '.')
    player.remove_item(item)
    item.position = player.position
    items.append(item)


def give_item_to_player():
    for item in items:
        if item.position == player.position:
            if player.add_item(item) is True:
                messages.add('You picked a %s! (%s)' % (item.name, item.key))
                items.remove(item)
            else:
                messages.add('Your inventory is full, cannot pick up ' +
                             item.name + '.')


def closest_monster_to_pos(pos, monsters, max_range):
    level_monsters = [m for m in monsters if m.position.z == pos.z]
    #find closest enemy, up to a maximum range, and in the FOV
    if len(level_monsters) < 1:
        return None

    compare_func = lambda x: euclidean_distance(x.position, pos)
    closest = min(level_monsters, key=compare_func)
    if (closest is None or
            not player.is_in_fov(closest.position) or
            euclidean_distance(closest.position, pos) > max_range):
        return None

    return closest

#############################################
# Initialization & Main Loop
#############################################

move_player(0, 0)

message_queue = Queue()


def send_all():
    data = {}
    data['dungeon'] = dungeon._model.json()
    data['player'] = player.json()
    data['monsters'] = [m.json() for m in monsters]
    data['items'] = [i.json() for i in items]
    data['messages'] = messages.toList()
    TCP_SERVER.broadcast(data)


def recv_forever(put_queue):
    while not player.died:
        TCP_SERVER.receive(put_queue)

        if not put_queue.empty():
            data = put_queue.get()
            print(data)
            if 'move' in data.keys():
                dx, dy = data['move']
                move_player(dx, dy)
            elif 'climb' in data.keys():
                new_level = dungeon.climb_stairs(player.position)
                move_player(0, 0, new_level - player.position.z)
            elif 'get' in data.keys():
                give_item_to_player()
            elif 'drop' in data.keys():
                item_key = data['drop']
                item = player.get_item(item_key)
                if item is not None:
                    take_item_from_player(item)
            elif 'use' in data.keys():
                item_key = data['use']
                item = player.get_item(item_key)
                if item is not None:
                    print "I should be using this. TODO."

            put_queue.task_done()
            take_turn()

            if player.died:
                messages.add('You died. Game over.')

            send_all()

recv_forever(message_queue)
TCP_SERVER.close()
