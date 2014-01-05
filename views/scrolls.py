from objects import ObjectView
import libtcodpy as libtcod


class Scroll(ObjectView):
    def __init__(self, model):
        super(Scroll, self).__init__(model, '#', libtcod.light_yellow)


class LightningBolt(Scroll):
    def __init__(self, model):
        super(LightningBolt, self).__init__(model)


class ConfusionScroll(Scroll):
    def __init__(self, model):
        super(ConfusionScroll, self).__init__(model)
