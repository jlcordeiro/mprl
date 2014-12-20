import libtcodpy as libtcod

def get_symbol(model):
    SYMBOLS = {'melee':         ('|', libtcod.light_red),
               'armour':        ('[', libtcod.light_red),
               'cast':          ('!', libtcod.light_green),
               'scroll':        ('#', libtcod.light_yellow),
               'Orc':           ('O', libtcod.light_orange),
               'Troll':         ('T', libtcod.light_orange),
               'player':        ('@', libtcod.white),
               'stairs_up':     ('<', libtcod.white),
               'stairs_down':   ('>', libtcod.white)
              }

    if model.type == 'creature':
        return SYMBOLS[model.name]

    return SYMBOLS[model.type]

def draw_object(console, model):
    (char, colour) = get_symbol(model)
    char = char if model.type != "creature" or model.died is False else '%'
    pos = model.position

    libtcod.console_set_default_foreground(console, colour)
    libtcod.console_put_char(console, pos.x, pos.y, char, libtcod.BKGND_NONE)

def erase_object(console, model):
    pos = model.position
    libtcod.console_put_char(console, pos.x, pos.y, ' ', libtcod.BKGND_NONE)
