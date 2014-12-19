from config import *

class ObjectModel(object):
    def __init__(self, name, type, x, y, blocks):
        self.x = x
        self.y = y
        self.key = '_'
        self.name = name
        self.blocks = blocks
        self.type = type

    @property
    def position(self):
        return (self.x, self.y)

    @position.setter
    def position(self, value):
        self.x = value[0]
        self.y = value[1]

    def json(self):
        return {'type': self.type,
                'x': self.x,
                'y': self.y
               }


class Potion(ObjectModel):
    def __init__(self, name, x, y, range, affects):
        super(Potion, self).__init__(name, "cast", x, y, False)
        self.range = range
        self.affects = affects


class Scroll(ObjectModel):
    def __init__(self, name, x, y, range, affects):
        super(Scroll, self).__init__(name, "cast", x, y, False)
        self.range = range
        self.affects = affects


class Weapon(ObjectModel):
    def __init__(self, name, x, y, damage, defense):
        super(Weapon, self).__init__(name, "melee", x, y, False)
        self.damage = damage
        self.defense = defense
 
    def json(self):
        return {'type': self.type,
                'x': self.x,
                'y': self.y,
                'damage': self.damage,
                'defense': self.defense
               }


class Armour(ObjectModel):
    def __init__(self, name, x, y, damage, defense):
        super(Armour, self).__init__(name, "armour", x, y, False)
        self.damage = damage
        self.defense = defense
 
    def json(self):
        return {'type': self.type,
                'x': self.x,
                'y': self.y,
                'damage': self.damage,
                'defense': self.defense
               }


################ Potions


class HealingPotion(Potion):
    def __init__(self, x, y):
        super(HealingPotion, self).__init__('Healing Potion', x, y, 0, 'owner')


################ Scrolls


class LightningBolt(Scroll):
    def __init__(self, x, y):
        super(LightningBolt, self).__init__('Lightning Bolt Scroll',
                                            x, y, LIGHTNING_RANGE, 'closest')


class ConfusionScroll(Scroll):
    def __init__(self, x, y):
        super(ConfusionScroll, self).__init__('Confusion Scroll',
                                              x, y, CONFUSE_RANGE, 'aim')


################ Weapons

class Stick(Weapon):
    def __init__(self, x, y):
        super(Stick, self).__init__('Stick', x, y, STICK_DMG, STICK_DEF)


class Crowbar(Weapon):
    def __init__(self, x, y):
        super(Crowbar, self).__init__('Crowbar', x, y, CROWBAR_DMG, CROWBAR_DEF)


class WoodenShield(Weapon):
    def __init__(self, x, y):
        super(WoodenShield, self).__init__('Wooden Shield', x, y,
                                           WOODEN_SHIELD_DMG, WOODEN_SHIELD_DEF)


class Cloak(Weapon):
    def __init__(self, x, y):
        super(Cloak, self).__init__('Cloak', x, y, CLOAK_DMG, CLOAK_DEF)
