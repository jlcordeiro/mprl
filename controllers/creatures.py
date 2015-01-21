import random
from messages import *
import common.models.creatures


def attack(source, target):
    damage = max(0, source.power - target.defense)
    target.hp -= damage

    messages = MessagesBorg()
    messages.add(source.name + ' attacks ' + target.name + ' for '
                 + str(damage) + ' hit points.')


def confused_move(source):
    source.position = source.position.add(random.randint(-1, 1), random.randint(-1, 1))
    source.confused_turns -= 1


def MonsterFactory(pos):
    dice = libtcod.random_get_int(0, 0, 100)
    if dice < 80:
        return common.models.creatures.Creature('Orc', pos, 10, 0, 3)
    else:
        return common.models.creatures.Creature('Troll', pos, 16, 1, 4)

    return None
