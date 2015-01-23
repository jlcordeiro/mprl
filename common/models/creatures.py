import libtcodpy as libtcod
from objects import ObjectModel
from config import *


class Creature(ObjectModel):
    def __init__(self, name, position, max_hp, hp, defense, power):
        super(Creature, self).__init__(name, "creature", position, True)
        self.max_hp = max_hp
        self.current_hp = hp
        self.base_defense = defense
        self.base_power = power
        self.confused_turns = 0
        self.target_pos = None

        self.weapon_right = None
        self.weapon_left = None
        self.armour = None

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
    def __init__(self, dungeon, pos):
        super(Player, self).__init__('player', pos, 30, 30, 2, 5)
        self.inventory = []
        self.fov_map = libtcod.map_new(MAP_WIDTH, MAP_HEIGHT)

        for y in range(MAP_HEIGHT):
            for x in range(MAP_WIDTH):
                libtcod.map_set_properties(self.fov_map, x, y,
                                           not dungeon.is_blocked(pos),
                                           not dungeon.is_blocked(pos))

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
        for item in self.inventory:
            if item.key == key:
                return item

    def remove_item(self, item):
        self.inventory.remove(item)

    def is_in_fov(self, pos):
        return libtcod.map_is_in_fov(self.fov_map, pos[0], pos[1])

    def update_fov(self):
        libtcod.map_compute_fov(self.fov_map,
                                self.position[0], self.position[1],
                                TORCH_RADIUS, FOV_LIGHT_WALLS, FOV_ALGO)

    def json(self):
        result = super(Player, self).json()
        result['items'] = [i.json() for i in self.inventory]
        return result
