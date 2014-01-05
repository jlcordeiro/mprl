
from objects import ObjectModel
from config import *


class Scroll(ObjectModel):
    def __init__(self, name, x, y, range, affects):
        super(Scroll, self).__init__(name, x, y, False)
        self.range = range
        self.affects = affects


class LightningBolt(Scroll):
    def __init__(self, x, y):
        super(LightningBolt, self).__init__('Lightning Bolt Scroll',
                                            x,
                                            y,
                                            LIGHTNING_RANGE,
                                            'closest')


class ConfusionScroll(Scroll):
    def __init__(self, x, y):
        super(ConfusionScroll, self).__init__('Confusion Scroll',
                                              x,
                                              y,
                                              CONFUSE_RANGE,
                                              'aim')
