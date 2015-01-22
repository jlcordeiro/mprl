import math
import views.objects
import common.models.objects
import libtcodpy as libtcod
from messages import *
from utils import euclidean_distance

################ Potions/Scrolls

def use_healing_potion(player, monsters):
    messages = Messages()
    messages.add('Your wounds start to feel better!')
    player.hp += HEAL_AMOUNT
    return True


def use_lightning_bolt(player, monsters):
    messages = Messages()

    if len(monsters) < 1:
        messages.add('No enemy is close enough to strike.')
        return False

    damage = LIGHTNING_DAMAGE
    for monster in monsters:
        messages.add('A lighting bolt strikes the ' + monster.name +
                     ' with a loud thunder! The damage is '
                     + str(damage) + ' hit points.')
        monster.hp -= damage

    return True


def use_confusion_scroll(player, monsters):
    messages = Messages()

    if len(monsters) < 1:
        messages.add('No enemy is close enough to confuse.')
        return False

    for monster in monsters:
        messages.add('The eyes of the ' + monster.name +
                     ' look vacant, as he starts to stumble around!')
        monster.confused_turns = CONFUSE_NUM_TURNS

    return True


################ Weapons


def ItemFactory(pos):
    dice = libtcod.random_get_int(0, 0, 100)
    if dice < 20:
        return common.models.objects.HealingPotion(pos)
    elif dice < 20:
        return common.models.objects.LightningBolt(pos)
    elif dice < 60:
        return common.models.objects.ConfusionScroll(pos)
    elif dice < 70:
        return common.models.objects.WoodenShield(pos)
    elif dice < 80:
        return common.models.objects.Cloak(pos)
    elif dice < 90:
        return common.models.objects.Stick(pos)
    else:
        return common.models.objects.Crowbar(pos)
