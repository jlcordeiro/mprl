from objects import ObjectView
import libtcodpy as libtcod


class Player(ObjectView):
    def __init__(self, model):
        super(Player, self).__init__(model, '@', libtcod.white)


class Orc(ObjectView):
    def __init__(self, model):
        super(Orc, self).__init__(model, 'O', libtcod.desaturated_green)


class Troll(ObjectView):
    def __init__(self, model):
        super(Troll, self).__init__(model, 'T', libtcod.darker_green)
