from objects import ObjectModel
from config import *

class Creature(ObjectModel):
    def __init__(self, name, x, y, hp, defense, power):
        super(Creature, self).__init__(name, "creature", x, y, True)
        self.max_hp = hp
        self.current_hp = hp
        self.base_defense = defense
        self.base_power = power
        self.confused_turns = 0
        self.target_pos = None

        self.inventory = []
        self.weapon_right = None
        self.weapon_left = None
        self.armour = None

    def __key_is_used(self, key):
        for item in self.inventory:
            if item.key == key:
                return True

        return False

    def __get_unused_key(self):
        for key in ITEM_KEYS:
            if not self.__key_is_used(key):
                return key

    def add_item(self, item):
        if len(self.inventory) >= len(ITEM_KEYS):
            return False

        item.key = self.__get_unused_key()
        self.inventory.append(item)
        self.inventory.sort(key=lambda i: i.key)
        return True

    def get_item(self, key):
        for item in self._model.inventory:
            if item.key == key:
                return item

    def remove_item(self, item):
        self.inventory.remove(item)

    @property
    def hp(self):
        return self.current_hp

    @hp.setter
    def hp(self, amount):
        self.current_hp = min(amount, self.max_hp)

        if self.current_hp <= 0:
            #transform it into a nasty corpse! it doesn't block, can't be
            #attacked and doesn't move
            self.confused_turns = 0
            self.blocks = False

    @property
    def power(self):
        total = self.base_power

        r_dmg = 0 if self.weapon_right is None else self.weapon_right.damage
        l_dmg = 0 if self.weapon_left is None else self.weapon_left.damage

        return total + max(r_dmg, l_dmg)

    @property
    def defense(self):
        total = self.base_defense

        if self.armour is not None:
            total += self.armour.defense

        r_def = 0 if self.weapon_right is None else self.weapon_right.defense
        l_def = 0 if self.weapon_left is None else self.weapon_left.defense

        return total + max(r_def, l_def)

    @property
    def died(self):
        return (self.current_hp <= 0)

    def json(self):
        return {'name': self.name,
                'position': self.position.coords,
                'hp': self.hp,
                'max_hp': self.max_hp,
                'defense': self.defense,
                'power': self.power}


class Player(Creature):
    def __init__(self, x, y):
        super(Player, self).__init__('player', x, y, 30, 2, 5)
