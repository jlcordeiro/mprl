from objects import ObjectController
from messages import *
import views.creatures
import models.creatures


class CreatureController(ObjectController):
    def __init__(self):
        raise NotImplementedError("not_implemented")

    def confuse(self):
        self._model.confused_turns = CONFUSE_NUM_TURNS

    def attack(self, target):
        #a simple formula for attack damage
        damage = self._model.power - target.defense

        messages = MessagesBorg()
        if damage > 0:
            #make the target take some damage
            messages.add(self.name + ' attacks ' + target.name + ' for '
                         + str(damage) + ' hit points.')
            target.take_damage(damage)
        else:
            messages.add(self.name + ' attacks ' + target.name +
                         ' but it has no effect!')

    def take_damage(self, damage):
        #apply damage if possible
        if damage > 0:
            self._model.hp -= damage

        if self._model.hp <= 0:
            self.die()

    def heal(self, amount):
        #heal by the given amount, without going over the maximum
        self._model.hp = max(self._model.hp + amount, self._model.max_hp)

    def die(self):
        #transform it into a nasty corpse! it doesn't block, can't be
        #attacked and doesn't move
        messages = MessagesBorg()
        messages.add(self.name + ' is dead!', libtcod.white)
        self._view.char = '%'
        self._model.confused_turns = 0
        self._model.blocks = False
        self._model.uid += " (dead)"

    @property
    def died(self):
        return (self._model.hp <= 0)

    @property
    def confused_turns(self):
        return self._model.confused_turns

    @property
    def hp(self):
        return self._model.hp

    @property
    def max_hp(self):
        return self._model.max_hp

    @property
    def defense(self):
        return self._model.defense

class Player(CreatureController):
    def __init__(self, x, y):
        self._model = models.creatures.Player(x, y)
        self._view = views.creatures.Player(self._model)

    def pick_item(self, item):
        #add to the player's inventory and remove from the map
        messages = MessagesBorg()
        if len(self._model.inventory) >= 26:
            messages.add('Your inventory is full, cannot pick up ' +
                         item.name + '.', libtcod.red)
            return False

        self._model.inventory.append(item)
        messages.add('You picked up a ' + item.name + '!', libtcod.green)
        return True

    def remove_item(self, item):
        self._model.inventory.remove(item)

    def drop_item(self, item):
        #add to the map and remove from the player's inventory.
        self.remove_item(item)
        # place it on the current player position
        item.position = self.position

        messages = MessagesBorg()
        messages.add('You dropped a ' + item.name + '.', libtcod.yellow)

    @property
    def items(self):
        return self._model.inventory


class Orc(CreatureController):
    def __init__(self, x, y):
        self._model = models.creatures.Orc(x, y)
        self._view = views.creatures.Orc(self._model)


class Troll(CreatureController):
    def __init__(self, x, y):
        self._model = models.creatures.Troll(x, y)
        self._view = views.creatures.Troll(self._model)


def MonsterFactory(x, y):
    dice = libtcod.random_get_int(0, 0, 100)

    if dice < 80:
        return Orc(x, y)

    return Troll(x, y)
