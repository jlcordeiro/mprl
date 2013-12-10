from objects import ObjectController
from messages import *
import views.potions
import models.potions


class Item(ObjectController):
    def __init__(self, x, y):
        raise NotImplementedError("not_implemented")

    @property
    def who_is_affected(self):
        return self.model.affects

    @property
    def affects_range(self):
        return self.model.range

    def cast(self, player, monsters):
        raise NotImplementedError("not_implemented")


class HealingPotion(Item):
    def __init__(self, x, y):
        self.model = models.potions.HealingPotion(x, y)
        self.view = views.potions.HealingPotion(self.model)

    def cast(self, player, monsters):
        messages = MessagesBorg()
        messages.add('Your wounds start to feel better!', libtcod.light_violet)
        player.heal(HEAL_AMOUNT)
        return True


class LightningBolt(Item):
    def __init__(self, x, y):
        self.model = models.potions.LightningBolt(x, y)
        self.view = views.potions.LightningBolt(self.model)

    def cast(self, player, monsters):
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
        self.model = models.potions.ConfusionScroll(x, y)
        self.view = views.potions.ConfusionScroll(self.model)

    def cast(self, player, monsters):
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


def ItemFactory(x, y):
    dice = libtcod.random_get_int(0, 0, 100)
    if dice < 30:
        return HealingPotion(x, y)
    elif dice < 60:
        return LightningBolt(x, y)
    else:
        return ConfusionScroll(x, y)
