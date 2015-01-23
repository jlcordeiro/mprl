import libtcodpy as libtcod


def wait_keypress():
    return libtcod.console_wait_for_keypress(True)


def key_is_escape(key):
    return key.vk == libtcod.KEY_ESCAPE


def key_is_up_move(key):
    return (key.vk in (libtcod.KEY_UP, libtcod.KEY_8, libtcod.KEY_KP8) or
            (key.vk == libtcod.KEY_CHAR and key.c == ord('k')))


def key_is_down_move(key):
    return (key.vk in (libtcod.KEY_DOWN, libtcod.KEY_2, libtcod.KEY_KP2) or
            (key.vk == libtcod.KEY_CHAR and key.c == ord('j')))


def key_is_left_move(key):
    return (key.vk in (libtcod.KEY_LEFT, libtcod.KEY_4, libtcod.KEY_KP4) or
            (key.vk == libtcod.KEY_CHAR and key.c == ord('h')))


def key_is_right_move(key):
    return (key.vk in (libtcod.KEY_RIGHT, libtcod.KEY_6, libtcod.KEY_KP6) or
            (key.vk == libtcod.KEY_CHAR and key.c == ord('l')))


def key_is_upleft_move(key):
    return (key.vk in (libtcod.KEY_7, libtcod.KEY_KP7) or
            (key.vk == libtcod.KEY_CHAR and key.c == ord('y')))


def key_is_upright_move(key):
    return (key.vk in (libtcod.KEY_9, libtcod.KEY_KP9) or
            (key.vk == libtcod.KEY_CHAR and key.c == ord('u')))


def key_is_downleft_move(key):
    return (key.vk in (libtcod.KEY_1, libtcod.KEY_KP1) or
            (key.vk == libtcod.KEY_CHAR and key.c == ord('b')))


def key_is_downright_move(key):
    return (key.vk in (libtcod.KEY_3, libtcod.KEY_KP3) or
            (key.vk == libtcod.KEY_CHAR and key.c == ord('n')))


def get_key_direction(key):
    """ Return a tuple (dx, dy) with the movement vector
        associated with the key that was pressed.
        For instance, clicking '4' will return (-1, 0).
        If the key is not a movement key, returns None """

    result = None

    if key_is_up_move(key):
        result = (0, -1)
    elif key_is_down_move(key):
        result = (0, 1)
    elif key_is_left_move(key):
        result = (-1, 0)
    elif key_is_right_move(key):
        result = (1, 0)
    elif key_is_upleft_move(key):
        result = (-1, -1)
    elif key_is_upright_move(key):
        result = (1, -1)
    elif key_is_downleft_move(key):
        result = (-1, 1)
    elif key_is_downright_move(key):
        result = (1, 1)

    return result
