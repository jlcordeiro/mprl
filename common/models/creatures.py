from objects import ObjectModel


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
        self.weaponr = None
        self.weaponl = None
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

    def __str__(self):
        return str(self.__dict__)

    @property
    def power(self):
        total = self.base_power

        r_dmg = 0 if self.weaponr is None else self.weaponr.damage
        l_dmg = 0 if self.weaponl is None else self.weaponl.damage

        return total + max(r_dmg, l_dmg)

    @property
    def defense(self):
        total = self.base_defense

        if self.armour is not None:
            total += self.armour.defense

        r_def = 0 if self.weaponr is None else self.weaponr.defense
        l_def = 0 if self.weaponl is None else self.weaponl.defense

        return total + max(r_def, l_def)

    @property
    def died(self):
        return (self.current_hp <= 0)

    def json(self):
        return {'name': self.name,
                'position': (self.x, self.y),
                'hp': self.hp,
                'max_hp': self.max_hp,
                'defense': self.defense,
                'power': self.power}


class Player(Creature):
    def __init__(self, x, y):
        super(Player, self).__init__('player', x, y, 30, 2, 5)
