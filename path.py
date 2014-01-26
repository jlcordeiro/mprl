import random
import libtcodpy as libtcod
from messages import *
from itertools import product

EIGHT_NEIGHBOURS = product([-1, 0, 1], [-1, 0, 1])
FOUR_NEIGHBOURS = [(x, y) for (x, y) in EIGHT_NEIGHBOURS if x == 0 or y == 0]

def min_neighbour(values, pos):
    """Determine which neighbour point around pos has the minimum value.
       * values is a bidimensional array with all the values.
       All values must be >= 0. Negative values are ignored.
       * pos is the position around which the minimum needs to be searched for.
       * Returns None if no value is found. Otherwise returns the minimum in 
       the format tuple (value, (dx, dy)) where value is the absolute value
       at the result position. (dx, dy) is the distance vector,
       so that pos+d = result. """

    res = None

    for (dx, dy) in FOUR_NEIGHBOURS:
        (x, y) = (pos[0]+dx, pos[1]+dy)

        if (y >= 0 and y < len(values) and
             x >= 0 and x < len(values[0]) and
             values[y][x] >= 0 and (res is None or res[0] > values[y][x])):
                res = (values[y][x], (dx, dy))

    return res


def find_shortest_path(destiny, source, width, height, method_check_blocks):
    """ Search for the minimum path between destiny and source.
        destiny is the path beginning with the format (x, y)
        source is the path destination with the format (x, y)
        width is the width of the map in which the path will be searched.
        height is the height of the map in which the path will be searched.
        method_check_blocks is a method that takes as argument one parameter,
            a tuple (x, y) and returns True if that position can be part
            of the path, or False if it can not.
        Returns (length, (dx, dy)) where length is the path lenght and dx, dy
            form the distance vector to which destiny should move next, to take
            the path found.
            If no path is found, returns None. """

    (end_x, end_y) = destiny

    # build map
    rmap = [[-1 for x in xrange(0, width)]
                 for y in xrange(0, height)]

    for x in xrange(0, width):
        for y in xrange(0, height):
            rmap[y][x] = None if method_check_blocks((x, y)) else -1

    rmap[end_y][end_x] = 0

    # check how far from destiny it has to go
    max_dist = max(end_x, end_y, width - end_x, height - end_y)

    for dist in xrange(1, max_dist):

        min_x = max(0, end_x - dist)
        max_x = min(width, end_x + dist + 1)
        min_y = max(0, end_y - dist)
        max_y = min(height, end_y + dist + 1)

        for tx, ty in product(xrange(min_x, max_x), xrange(min_y, max_y)):
            minn = min_neighbour(rmap, (tx, ty))

            if minn is not None and (rmap[ty][tx] is -1 or rmap[ty][tx] > minn[0]):
                rmap[ty][tx] = minn[0]+1

    return min_neighbour(rmap, source)

def move_towards_creature(one, other, map_width, map_height, method_check_blocks):

    path = find_shortest_path(other.position,
                              one.position,
                              map_width,
                              map_height,
                              method_check_blocks)

    if path is None:
        return

    (dx, dy) = path[1]
    one.move(dx, dy)


def take_turn(monster, player, map_width, map_height, method_check_blocks):
    if monster.died:
        return

    messages = MessagesBorg()
    if monster.confused_turns > 0:
        messages.add('The ' + monster.name + ' is confused!', libtcod.red)

        (xi, yi) = monster.position
        (dx, dy) = (random.randint(-1, 1), random.randint(-1, 1))
        final_pos = (xi + dx, yi + dy)

        if method_check_blocks(final_pos) is False:
            monster.move(dx, dy)

        monster.confused_turns -= 1

        if monster.confused_turns == 0:
            messages.add('The ' + monster.name + ' is no longer confused!',
                         libtcod.red)

    else:
        #move towards player if far away
        if monster.distance_to(player) > 1:
            move_towards_creature(monster, player, map_width, map_height, method_check_blocks)
        #close enough, attack! (if the player is still alive.)
        elif player.hp > 0:
            monster.attack(player)

if __name__ == "__main__":

    validity_method = lambda x: x in ((6, 2),
                                      (6, 3),
                                      (6, 4),
                                      (6, 5),
                                      (7, 2),
                                      (7, 4))

    plr = (5, 3)
    orc = (7, 3)

    while orc != plr:
        p = find_shortest_path(plr, orc, 25, 10, validity_method)
        print p
        orc = (orc[0] + p[1][0], orc[1] + p[1][1])

        raw_input()
