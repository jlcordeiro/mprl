from objects import ObjectController
from messages import *
import views.creatures
import models.creatures


class CreatureController(ObjectController):
    def __init__(self):
        raise NotImplementedError("not_implemented")

    def confuse(self):
        self.model.confused_turns = CONFUSE_NUM_TURNS

    def attack(self, target):
        #a simple formula for attack damage
        damage = self.model.power - target.model.defense

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
            self.model.hp -= damage

        if self.model.hp <= 0:
            self.die()

    def heal(self, amount):
        #heal by the given amount, without going over the maximum
        self.model.hp = max(self.model.hp + amount, self.model.max_hp)

    def die(self):
        #transform it into a nasty corpse! it doesn't block, can't be
        #attacked and doesn't move
        messages = MessagesBorg()
        messages.add(self.name + ' is dead!', libtcod.white)
        self.view.char = '%'
        self.model.confused_turns = 0
        self.model.blocks = False
        self.model.uid += " (dead)"

    @property
    def died(self):
        return (self.model.hp <= 0)


class Player(CreatureController):
    def __init__(self, x, y):
        self.model = models.creatures.Player(x, y)
        self.view = views.creatures.Player(self.model)

    def pick_item(self, item):
        #add to the player's inventory and remove from the map
        messages = MessagesBorg()
        if len(self.model.inventory) >= 26:
            messages.add('Your inventory is full, cannot pick up ' +
                         item.name + '.', libtcod.red)
            return False

        self.model.inventory.append(item)
        messages.add('You picked up a ' + item.name + '!', libtcod.green)
        return True

    def drop_item(self, item):
        #add to the map and remove from the player's inventory.
        self.model.inventory.remove(item)
        # place it on the current player position
        item.model.x = self.model.x
        item.model.y = self.model.y

        messages = MessagesBorg()
        messages.add('You dropped a ' + item.name + '.', libtcod.yellow)


class Orc(CreatureController):
    def __init__(self, x, y):
        self.model = models.creatures.Orc(x, y)
        self.view = views.creatures.Orc(self.model)


class Troll(CreatureController):
    def __init__(self, x, y):
        self.model = models.creatures.Troll(x, y)
        self.view = views.creatures.Troll(self.model)


def MonsterFactory(x, y):
    dice = libtcod.random_get_int(0, 0, 100)

    if dice < 80:
        return Orc(x, y)

    return Troll(x, y)
