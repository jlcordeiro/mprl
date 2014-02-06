import libtcodpy as libtcod


class ObjectView(object):
    """Base class for a view of any object. Potions, weapons, etc."""

    def __init__(self, model, char, colour):
        self._model = model
        self.char = char
        self.colour = colour

    def _put(self, console, char):
        """Put char on the current position."""
        libtcod.console_put_char(console, self._model.x, self._model.y,
                                 char, libtcod.BKGND_NONE)

    def draw(self, console):
        """Set the colour."""
        libtcod.console_set_default_foreground(console, self.colour)
        #draw the character that represents this object at its position
        self._put(console, self.char)

    def clear(self, console):
        """Erase the character that represents this object."""
        self._put(console, ' ')


class Potion(ObjectView):
    def __init__(self, model):
        super(Potion, self).__init__(model, '!', libtcod.light_green)


class Scroll(ObjectView):
    def __init__(self, model):
        super(Scroll, self).__init__(model, '#', libtcod.light_yellow)


class Weapon(ObjectView):
    def __init__(self, model):
        super(Weapon, self).__init__(model, '|', libtcod.light_red)
