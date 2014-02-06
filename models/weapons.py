from objects import ObjectModel
from config import *


class Weapon(ObjectModel):
    def __init__(self, name, x, y, min_damage, max_damage):
        super(Weapon, self).__init__(name, x, y, False)
        self.min_damage = min_damage
        self.max_damage = max_damage


class Stick(Weapon):
    def __init__(self, x, y):
        super(Stick, self).__init__('Stick', x, y, STICK_MIND, STICK_MAXD)


class Crowbar(Weapon):
    def __init__(self, x, y):
        super(Crowbar, self).__init__('Crowbar', x, y,
                                      CROWBAR_MIND, CROWBAR_MAXD)
