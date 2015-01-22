from config import *
from common.utilities.geometry import Point3

class ObjectModel(object):
    def __init__(self, name, type, position, blocks, key = '_'):
        self.position = Point3.copy(position)
        self.key = key
        self.name = name
        self.blocks = blocks
        self.type = type

    def json(self):
        return {'name': self.name,
                'type': self.type,
                'position': self.position,
                'blocks': self.blocks,
                'key': self.key
               }


class Potion(ObjectModel):
    def __init__(self, name, pos, range, affects):
        super(Potion, self).__init__(name, "cast", pos, False)
        self.range = range
        self.affects = affects


class Scroll(ObjectModel):
    def __init__(self, name, pos, range, affects):
        super(Scroll, self).__init__(name, "cast", pos, False)
        self.range = range
        self.affects = affects


class Weapon(ObjectModel):
    def __init__(self, name, pos, damage, defense):
        super(Weapon, self).__init__(name, "melee", pos, False)
        self.damage = damage
        self.defense = defense


class Armour(ObjectModel):
    def __init__(self, name, pos, damage, defense):
        super(Armour, self).__init__(name, "armour", pos, False)
        self.damage = damage
        self.defense = defense


################ Potions


class HealingPotion(Potion):
    def __init__(self, pos):
        super(HealingPotion, self).__init__('Healing Potion', pos, 0, 'owner')


################ Scrolls


class LightningBolt(Scroll):
    def __init__(self, pos):
        super(LightningBolt, self).__init__('Lightning Bolt Scroll',
                                            pos, LIGHTNING_RANGE, 'closest')


class ConfusionScroll(Scroll):
    def __init__(self, pos):
        super(ConfusionScroll, self).__init__('Confusion Scroll',
                                              pos, CONFUSE_RANGE, 'aim')


################ Weapons

class Stick(Weapon):
    def __init__(self, pos):
        super(Stick, self).__init__('Stick', pos, STICK_DMG, STICK_DEF)


class Crowbar(Weapon):
    def __init__(self, pos):
        super(Crowbar, self).__init__('Crowbar', pos, CROWBAR_DMG, CROWBAR_DEF)


class WoodenShield(Weapon):
    def __init__(self, pos):
        super(WoodenShield, self).__init__('Wooden Shield', pos,
                                           WOODEN_SHIELD_DMG, WOODEN_SHIELD_DEF)


class Cloak(Weapon):
    def __init__(self, pos):
        super(Cloak, self).__init__('Cloak', pos, CLOAK_DMG, CLOAK_DEF)
