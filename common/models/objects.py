from config import *
from common.utilities.geometry import Point


class ObjectModel(object):
    """ Base class for all objects. """

    # name of each action
    action_names = {'u': 'cast',
                    'd': 'drop',
                    'w': 'wear',
                    'r': 'use-right',
                    'l': 'use-left'}

    def __init__(self, name, type, position, blocks, key='_', **extras):
        self.position = Point.copy(position)
        self.key = key
        self.name = name
        self.blocks = blocks
        self.type = type

    def allowed_actions(self):
        """ Return list of actions that can be performed on this item.
            Returns both its identifying key, and a description. """
        _actions_by_type = {"cast": [('u', "(U)se"),
                                     ('d', "(D)rop")],
                            "melee": [('r', "Equip in (r)ight hand"),
                                      ('l', "Equip in (l)eft hand"),
                                      ('d', "(D)rop")],
                            "armour": [('w', "(W)ear"),
                                       ('d', "(D)rop")]}

        return _actions_by_type[self.type]

    def json(self):
        return {'name': self.name,
                'type': self.type,
                'position': self.position,
                'blocks': self.blocks,
                'key': self.key}


class Potion(ObjectModel):
    def __init__(self, name, position, range, affects):
        super(Potion, self).__init__(name, "cast", position, False)
        self.range = range
        self.affects = affects


class Weapon(ObjectModel):
    def __init__(self, name, position, damage, defense, **extras):
        super(Weapon, self).__init__(name, "melee", position, False)
        self.damage = damage
        self.defense = defense

    def json(self):
        result = super(Weapon, self).json()
        result['damage'] = self.damage
        result['defense'] = self.defense
        return result


class Armour(ObjectModel):
    def __init__(self, name, position, damage, defense, **extras):
        super(Armour, self).__init__(name, "armour", position, False)
        self.damage = damage
        self.defense = defense

    def json(self):
        result = super(Armour, self).json()
        result['damage'] = self.damage
        result['defense'] = self.defense
        return result


################ Potions


class HealingPotion(Potion):
    def __init__(self, pos):
        super(HealingPotion, self).__init__('Healing Potion', pos, 0, 'owner')


################ Weapons

class Stick(Weapon):
    def __init__(self, pos):
        super(Stick, self).__init__('Stick', pos, STICK_DMG, STICK_DEF)


class Crowbar(Weapon):
    def __init__(self, pos):
        super(Crowbar, self).__init__('Crowbar', pos, CROWBAR_DMG, CROWBAR_DEF)


class WoodenShield(Weapon):
    def __init__(self, pos):
        super(WoodenShield, self).__init__('Wooden Shield',
                                           pos,
                                           WOODEN_SHIELD_DMG,
                                           WOODEN_SHIELD_DEF)


class Cloak(Armour):
    def __init__(self, pos):
        super(Cloak, self).__init__('Cloak', pos, CLOAK_DMG, CLOAK_DEF)
