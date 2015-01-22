import random
from messages import *
import common.models.creatures


def confused_move(source):
    source.position = source.position.add(random.randint(-1, 1), random.randint(-1, 1))
    source.confused_turns -= 1


def MonsterFactory(pos):
    dice = random.randint(0, 100)
    if dice < 80:
        return common.models.creatures.Creature('Orc', pos, 10, 10, 0, 3)
    else:
        return common.models.creatures.Creature('Troll', pos, 16, 16, 1, 4)

    return None
