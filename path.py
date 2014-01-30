import random
import libtcodpy as libtcod
from messages import *

def move_towards_creature(one, other, map_width, map_height, path):

    onex, oney = one.position
    otherx, othery = other.position
    libtcod.path_compute(path, onex, oney, otherx, othery)

    if libtcod.path_is_empty(path):
        return

    next_pos = libtcod.path_get(path, 0)
    one.move(new_pos=next_pos)


def take_turn(monster, player, map_width, map_height, method_check_blocks, path):
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
            move_towards_creature(monster, player, map_width, map_height, path)
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
  

    width, height = 150, 100


    while orc != plr:

        rmap = build_path_map(plr, width, height, validity_method)
        p = min_neighbour(rmap, orc)

#            printed = rmap
#            for idx1, rr in enumerate(rmap):
#                for idx2, r in enumerate(rr):
#                    if r is None:
#                        printed[idx1][idx2] = -1
#
#            for rr in printed:
#                pass
#                print "\t".join(map(str,rr))

        orc = (orc[0] + p[1][0], orc[1] + p[1][1])
