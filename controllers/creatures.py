from objects import ObjectController
import random
from messages import *
import views.creatures
import common.models.creatures


class CreatureController(ObjectController):
    def __init__(self):
        raise NotImplementedError("not_implemented")

    def confuse(self):
        messages = MessagesBorg()
        messages.add('The ' + self.name + ' is confused!', libtcod.red)
        self._model.confused_turns = CONFUSE_NUM_TURNS

    def confused_move(self):
        self.move(random.randint(-1, 1), random.randint(-1, 1))

        self.confused_turns -= 1

        if self.confused_turns == 0:
            messages = MessagesBorg()
            messages.add('The ' + self.name + ' is no longer confused!',
                         libtcod.red)

    @property
    def power(self):
        total = self._model.base_power

        r_weapon = self._model.weaponr
        l_weapon = self._model.weaponl

        r_dmg = 0 if r_weapon is None else r_weapon.damage
        l_dmg = 0 if l_weapon is None else l_weapon.damage

        return total + max(r_dmg, l_dmg)

    def attack(self, target):
        #a simple formula for attack damage
        damage = self.power - target.defense

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

    @property
    def died(self):
        return (self._model.hp <= 0)

    @property
    def confused_turns(self):
        return self._model.confused_turns

    @confused_turns.setter
    def confused_turns(self, value):
        self._model.confused_turns = value

    @property
    def hp(self):
        return self._model.hp

    @property
    def max_hp(self):
        return self._model.max_hp

    @property
    def defense(self):
        total = self._model.defense

        r_weapon = self._model.weaponr
        l_weapon = self._model.weaponl

        if self._model.armour is not None:
            total += self._model.armour.defense

        r_def = 0 if r_weapon is None else r_weapon.defense
        l_def = 0 if l_weapon is None else l_weapon.defense

        return total + max(r_def, l_def)

    @property
    def target(self):
        return self._model.target_pos

    @target.setter
    def target(self, value):
        self._model.target_pos = value

    def json(self):
        return {}

class Player(CreatureController):
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
            previous_weapon = self._model.weaponr
            self._model.weaponr = weapon
        else:
            previous_weapon = self._model.weaponl
            self._model.weaponl = weapon

        if previous_weapon is not None:
            previous_weapon.used = False

        weapon.used = True

        messages = MessagesBorg()
        messages.add('You equipped a ' + weapon.name + '.', libtcod.green)

    def wear(self, armour):
        """Replace equipped armour by a new one."""

        messages = MessagesBorg()
        if armour.type != "armour":
            messages.add('You can\'t wear a ' + armour.name + '.', libtcod.red)
            return

        messages.add('You are now wearing a ' + armour.name + '.', libtcod.green)

        previous = self._model.armour
        self._model.armour = armour

        if previous is not None:
            previous.used = False

        armour.used = True

    @property
    def items(self):
        return self._model.inventory


class Orc(CreatureController):
    def __init__(self, x, y):
        self._model = common.models.creatures.Orc(x, y)
        self._view = views.creatures.Orc(self._model)


class Troll(CreatureController):
    def __init__(self, x, y):
        self._model = common.models.creatures.Troll(x, y)
        self._view = views.creatures.Troll(self._model)


def MonsterFactory(x, y):
    dice = libtcod.random_get_int(0, 0, 100)

    if dice < 80:
        return Orc(x, y)

    return Troll(x, y)
