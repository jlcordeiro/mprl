""" Object (items/creatures) controller. """

import random
import common.models.objects
import common.models.creatures

def create_random_monster(pos):
    """ Randomly create a monster at a given position. """
    dice = random.randint(0, 100)
    if dice < 80:
        return common.models.creatures.Creature('Orc', pos, 10, 10, 0, 3)
    else:
        return common.models.creatures.Creature('Troll', pos, 16, 16, 1, 4)

    return None


def create_random_item(pos):
    """ Randomly create an item at a given position. """
    dice = random.randint(0, 100)
    if dice < 20:
        return common.models.objects.HealingPotion(pos)
    elif dice < 40:
        return common.models.objects.WoodenShield(pos)
    elif dice < 60:
        return common.models.objects.Cloak(pos)
    elif dice < 90:
        return common.models.objects.Stick(pos)
    else:
        return common.models.objects.Crowbar(pos)

    return None
