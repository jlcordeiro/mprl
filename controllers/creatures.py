import random
from messages import *
import views.creatures
import common.models.creatures


def attack(source, target):
    damage = max(0, source.power - target.defense)
    target.hp -= damage

    messages = MessagesBorg()
    messages.add(source.name + ' attacks ' + target.name + ' for '
                 + str(damage) + ' hit points.')


def confused_move(source):
    source.move(random.randint(-1, 1), random.randint(-1, 1))
    source.confused_turns -= 1


class Player(object):
    def __init__(self, x, y):
        self._model = common.models.creatures.Player(x, y)
        self._view = views.creatures.Player(self._model)

    def __key_is_used(self, key):
        for item in self._model.inventory:
            if item.key == key:
                return True

        return False

    def __get_unused_key(self):
        for key in ITEM_KEYS:
            if not self.__key_is_used(key):
                return key

    def pick_item(self, item):
        #add to the player's inventory and remove from the map
        messages = MessagesBorg()
        if len(self._model.inventory) >= len(ITEM_KEYS):
            messages.add('Your inventory is full, cannot pick up ' +
                         item.name + '.', libtcod.red)
            return False

        item.key = self.__get_unused_key()

        self._model.inventory.append(item)
        messages.add('You picked up a ' + item.name + '! (' + item.key + ')', libtcod.green)

        #sort inventory by item key
        self._model.inventory.sort(key=lambda i: i.key)

        return True

    def get_item_with_key(self, key):
        for item in self._model.inventory:
            if item.key == key:
                return item

    def remove_item(self, item):
        self._model.inventory.remove(item)

    def drop_item(self, item):
        #add to the map and remove from the player's inventory.
        self.remove_item(item)
        # place it on the current player position
        item.position = self.position

        messages = MessagesBorg()
        messages.add('You dropped a ' + item.name + '.', libtcod.yellow)

    def equip(self, hand, weapon):
        """Replace equipped weapon by a new one."""

        if hand == "right":
            self._model.weaponr = weapon
        else:
            self._model.weaponl = weapon

        messages = MessagesBorg()
        messages.add('You equipped a ' + weapon.name + '.', libtcod.green)

    def wear(self, armour):
        """Replace equipped armour by a new one."""

        messages = MessagesBorg()
        if armour.type != "armour":
            messages.add('You can\'t wear a ' + armour.name + '.', libtcod.red)
            return

        messages.add('You are now wearing a ' + armour.name + '.', libtcod.green)

        self._model.armour = armour


def MonsterFactory(x, y):
    dice = libtcod.random_get_int(0, 0, 100)

    if dice < 80:
        model = common.models.creatures.Creature('Orc', x, y, 10, 0, 3)
    else:
        model = common.models.creatures.Creature('Troll', x, y, 16, 1, 4)

    return model
