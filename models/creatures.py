from objects import ObjectModel


class Creature(ObjectModel):
    def __init__(self, name, x, y, hp, defense, power):
        super(Creature, self).__init__(name, x, y, True)
        self.max_hp = hp
        self.hp = hp
        self.defense = defense
        self.power = power
        self.confused_turns = 0
        self.target_pos = None

        self.weaponr = None
        self.weaponl = None
        self.armour = None

class Orc(Creature):
    def __init__(self, x, y):
        super(Orc, self).__init__('orc', x, y, 10, 0, 3)


class Troll(Creature):
    def __init__(self, x, y):
        super(Troll, self).__init__('troll', x, y, 16, 1, 4)


class Player(Creature):
    def __init__(self, x, y):
        super(Player, self).__init__('player', x, y, 30, 2, 5)
        self.inventory = []
