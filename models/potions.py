from objects import ObjectModel
from config import *


class Potion(ObjectModel):
    def __init__(self, name, x, y, range, affects):
        super(Potion, self).__init__(name, x, y, False)
        self.range = range
        self.affects = affects


class HealingPotion(Potion):
    def __init__(self, x, y):
        super(HealingPotion, self).__init__('Healing Potion', x, y, 0, 'owner')


class LightningBolt(Potion):
    def __init__(self, x, y):
        super(HealingPotion, self).__init__('Lightning Bolt',
                                            x,
                                            y,
                                            LIGHTNING_RANGE,
                                            'closest')


class LightningBolt(Potion):
    def __init__(self, x, y):
        super(LightningBolt, self).__init__('Lightning Bolt',
                                            x,
                                            y,
                                            LIGHTNING_RANGE,
                                            'closest')


class ConfusionScroll(Potion):
    def __init__(self, x, y):
        super(ConfusionScroll, self).__init__('Confusion Scroll',
                                              x,
                                              y,
                                              CONFUSE_RANGE,
                                              'closest')
