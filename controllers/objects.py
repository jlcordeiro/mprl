import math
import views.objects
import common.models.objects
import libtcodpy as libtcod
from messages import *
from utils import euclidean_distance


class ObjectController(object):
    def __init__(self):
        self._model = None
        self._view = None
        raise NotImplementedError("not_implemented")

    def __str__(self):
        return str(self.json())

    def move(self, dx = None, dy = None, new_pos = None):
        if new_pos is None:
            self._model.x += dx
            self._model.y += dy
        else:
            self._model.x = new_pos[0]
            self._model.y = new_pos[1]

    @property
    def position(self):
        return (self._model.x, self._model.y)

    @position.setter
    def position(self, value):
        self._model.x = value[0]
        self._model.y = value[1]

    @property
    def blocks(self):
        return self._model.blocks

    @property
    def name(self):
        return self._model.name

    @property
    def used(self):
        return self._model.used

    @used.setter
    def used(self, value):
        self._model.used = value

    def distance_to(self, pos):
        return euclidean_distance(self.position, pos)

    def draw_ui(self, con):
        self._view.draw(con)

    def clear_ui(self, con):
        self._view.clear(con)


################ Potions/Scrolls

class Item(ObjectController):
    def __init__(self, x, y):
        self._model = None
        raise NotImplementedError("not_implemented")

    @property
    def type(self):
        return "cast"

    @property
    def who_is_affected(self):
        return self._model.affects

    @property
    def range(self):
        return self._model.range

    def use(self, player, monsters):
        raise NotImplementedError("not_implemented")

    def json(self):
        return {'type': self.type,
                'x': self._model.x,
                'y': self._model.y
               }


class HealingPotion(Item):
    def __init__(self, x, y):
        self._model = common.models.objects.HealingPotion(x, y)
        self._view = views.objects.Potion(self._model)

    def use(self, player, monsters):
        messages = MessagesBorg()
        messages.add('Your wounds start to feel better!', libtcod.light_violet)
        player.heal(HEAL_AMOUNT)
        return True


class LightningBolt(Item):
    def __init__(self, x, y):
        self._model = models.objects.LightningBolt(x, y)
        self._view = views.objects.Scroll(self._model)

    def use(self, player, monsters):
        messages = MessagesBorg()

        if len(monsters) < 1:
            messages.add('No enemy is close enough to strike.', libtcod.red)
            return False

        damage = LIGHTNING_DAMAGE
        for monster in monsters:
            messages.add('A lighting bolt strikes the ' + monster.name +
                         ' with a loud thunder! The damage is '
                         + str(damage) + ' hit points.', libtcod.light_blue)
            monster.take_damage(damage)

        return True


class ConfusionScroll(Item):
    def __init__(self, x, y):
        self._model = common.models.objects.ConfusionScroll(x, y)
        self._view = views.objects.Scroll(self._model)

    def use(self, player, monsters):
        messages = MessagesBorg()

        if len(monsters) < 1:
            messages.add('No enemy is close enough to confuse.', libtcod.red)
            return False

        for monster in monsters:
            messages.add('The eyes of the ' + monster.name +
                         ' look vacant, as he starts to stumble around!',
                         libtcod.light_green)
            monster.confuse()

        return True


################ Weapons

class Weapon(ObjectController):
    def __init__(self, x, y):
        self._model = None
        self._views = None
        raise NotImplementedError("not_implemented")

    @property
    def type(self):
        return "melee"

    @property
    def damage(self):
        return self._model.damage

    @property
    def defense(self):
        return self._model.defense
 
    def json(self):
        return {'type': self.type,
                'x': self._model.x,
                'y': self._model.y,
                'dmg': self.damage,
                'def': self.defense
               }


class Armour(ObjectController):
    def __init__(self, x, y):
        self._model = None
        self._views = None
        raise NotImplementedError("not_implemented")

    @property
    def type(self):
        return "armour"

    @property
    def damage(self):
        return self._model.damage

    @property
    def defense(self):
        return self._model.defense
 
    def json(self):
        return {'type': self.type,
                'x': self._model.x,
                'y': self._model.y,
                'dmg': self.damage,
                'def': self.defense
               }


class Stick(Weapon):
    def __init__(self, x, y):
        self._model = common.models.objects.Stick(x, y)
        self._view = views.objects.Weapon(self._model)


class Crowbar(Weapon):
    def __init__(self, x, y):
        self._model = common.models.objects.Crowbar(x, y)
        self._view = views.objects.Weapon(self._model)


class WoodenShield(Weapon):
    def __init__(self, x, y):
        self._model = common.models.objects.WoodenShield(x, y)
        self._view = views.objects.Weapon(self._model)


class Cloak(Armour):
    def __init__(self, x, y):
        self._model = common.models.objects.Cloak(x, y)
        self._view = views.objects.Armour(self._model)


def ItemFactory(x, y):
    dice = libtcod.random_get_int(0, 0, 100)
    if dice < 20:
        return HealingPotion(x, y)
    elif dice < 20:
        return LightningBolt(x, y)
    elif dice < 60:
        return ConfusionScroll(x, y)
    elif dice < 70:
        return WoodenShield(x, y)
    elif dice < 80:
        return Cloak(x, y)
    elif dice < 90:
        return Stick(x, y)
    else:
        return Crowbar(x, y)
