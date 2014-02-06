from config import *

class ObjectModel(object):
    def __init__(self, name, x, y, blocks):
        self.x = x
        self.y = y
        self.name = name
        self.blocks = blocks


################ Potions

class Potion(ObjectModel):
    def __init__(self, name, x, y, range, affects):
        super(Potion, self).__init__(name, x, y, False)
        self.range = range
        self.affects = affects


class HealingPotion(Potion):
    def __init__(self, x, y):
        super(HealingPotion, self).__init__('Healing Potion', x, y, 0, 'owner')


################ Scrolls

class Scroll(ObjectModel):
    def __init__(self, name, x, y, range, affects):
        super(Scroll, self).__init__(name, x, y, False)
        self.range = range
        self.affects = affects


class LightningBolt(Scroll):
    def __init__(self, x, y):
        super(LightningBolt, self).__init__('Lightning Bolt Scroll',
                                            x, y, LIGHTNING_RANGE, 'closest')


class ConfusionScroll(Scroll):
    def __init__(self, x, y):
        super(ConfusionScroll, self).__init__('Confusion Scroll',
                                              x, y, CONFUSE_RANGE, 'aim')


################ Weapons


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
