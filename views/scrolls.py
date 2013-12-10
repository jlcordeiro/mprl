from objects import ObjectView
import libtcodpy as libtcod


class Scroll(ObjectView):
    def __init__(self, model, colour):
        super(Scroll, self).__init__(model, '#', colour)


class LightningBolt(Scroll):
    def __init__(self, model):
        super(LightningBolt, self).__init__(model, libtcod.light_yellow)
