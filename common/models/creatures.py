from config import *
from objects import ObjectModel, Weapon, Armour
from common.utilities.fov import Fov


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
            self.confused_turns = 0
            self.blocks = False

    @property
    def power(self):
        damage = lambda x: 0 if x is None else x.damage
        base = self.base_power
        return base + max(damage(self.weapon_right), damage(self.weapon_left))

    @property
    def defense(self):
        defense = lambda x: 0 if x is None else x.defense
        return (self.base_defense + defense(self.armour) +
                max(defense(self.weapon_right), defense(self.weapon_left)))

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
    def __init__(self, position, max_hp=30, hp=30, **extras):
        super(Player, self).__init__('player', position, max_hp, hp, PLAYER_BASE_DEF, PLAYER_BASE_POW)
        self.inventory = []
        self.fov = Fov(MAP_WIDTH, MAP_HEIGHT)

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
        return self.fov.contains((pos[0], pos[1]))

    def update_fov(self, blocks_visibility):
        self.fov.update(self.position, TORCH_RADIUS, blocks_visibility)

    def json(self):
        result = super(Player, self).json()
        result['items'] = [i.json() for i in self.inventory]

        weapon_json = lambda x: x.json() if x else None

        result['weapon_right'] = weapon_json(self.weapon_right)
        result['weapon_left'] = weapon_json(self.weapon_left)
        result['armour'] = weapon_json(self.armour)
        return result

    @staticmethod
    def fromJson(dic, **extras):
        player = Player(**dic)
        player.inventory = [ObjectModel(**i) for i in dic['items']]

        wear = lambda c, x: c(**dic[x]) if dic[x] else None
        player.weapon_left = wear(Weapon, 'weapon_left')
        player.weapon_right = wear(Weapon, 'weapon_right')
        player.armour = wear(Armour, 'armour')

        return player
