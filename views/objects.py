import libtcodpy as libtcod


class ObjectView(object):
    def __init__(self, model, char, colour):
        self._model = model
        self.char = char
        self.colour = colour

    def draw(self, console):
        #set the colour
        libtcod.console_set_default_foreground(console, self.colour)
        #draw the character that represents this object at its position
        libtcod.console_put_char(console,
                                 self._model.x,
                                 self._model.y,
                                 self.char,
                                 libtcod.BKGND_NONE)

    def clear(self, console):
        #erase the character that represents this object
        libtcod.console_put_char(console,
                                 self._model.x,
                                 self._model.y,
                                 ' ',
                                 libtcod.BKGND_NONE)


class Potion(ObjectView):
    def __init__(self, model):
        super(Potion, self).__init__(model, '!', libtcod.light_green)


class Scroll(ObjectView):
    def __init__(self, model):
        super(Scroll, self).__init__(model, '#', libtcod.light_yellow)
