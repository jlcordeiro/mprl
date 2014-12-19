import libtcodpy as libtcod

def get_symbol(model):
    SYMBOLS = {'melee':     ('|', libtcod.light_red),
               'armour':    ('[', libtcod.light_red),
               'cast':      ('!', libtcod.light_green),
               'scroll':    ('#', libtcod.light_yellow),
               'Orc':       ('O', libtcod.light_orange),
               'Troll':     ('T', libtcod.light_orange),
               'player':    ('@', libtcod.white)
              }

    if model.type == 'creature':
        return SYMBOLS[model.name]

    return SYMBOLS[model.type]

class ObjectView(object):
    """Base class for a view of any object. Potions, weapons, etc."""

    def __init__(self, model, char, colour):
        self._model = model
        (self.char, self.colour) = get_symbol(model)

    def _put(self, console, char):
        """Put char on the current position."""
        libtcod.console_put_char(console, self._model.x, self._model.y,
                                 char, libtcod.BKGND_NONE)

    def draw(self, console):
        """Set the colour."""
        libtcod.console_set_default_foreground(console, self.colour)
        #draw the character that represents this object at its position
        char = self.char if self._model.died is False else '%'
        self._put(console, char)

    def clear(self, console):
        """Erase the character that represents this object."""
        self._put(console, ' ')
