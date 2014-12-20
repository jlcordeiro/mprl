import libtcodpy as libtcod
from utils import euclidean_distance
import random
import views.dungeon
import common.models.dungeon
from objects import ItemFactory
from creatures import MonsterFactory
from controllers.creatures import attack
from views.objects import draw_object, erase_object
from common.utilities.geometry import Point
from config import *
from messages import *

class Dungeon(object):
    def __init__(self):
        self._model = common.models.dungeon.Dungeon()
        self._view = views.dungeon.Level(self._model)
   
    @property
    def __clevel(self):
        """ Return the current level. """
        return self._model.current_level

    @property
    def player(self):
        return self._model.player

    def move_player(self, dx, dy):
        self._model.move_player(dx, dy)

    def closest_monster_to_player(self, max_range):
        pos = self.player.position
        return self.__clevel.closest_monster_to_pos(pos, max_range)

    def is_blocked(self, pos):
        return self.__clevel.is_blocked(pos)

    def __take_turn_monster(self, monster):
        previous_pos = monster.position

        messages = MessagesBorg()

        if monster.confused_turns > 0:
            monster.confused_move()

            if self.is_blocked(monster.position) is False:
                monster.position = previous_pos

            return

        #not confused

        #close enough, attack! (if the player is still alive.)
        if euclidean_distance(self.player.position, monster.position) < 2 and self.player.hp > 0:
            attack(monster, self.player)
            return

        #if the monster sees the player, update its target position
        if self.__clevel.is_in_fov(monster.position):
            monster.target_pos = self.player.position

        if monster.target_pos not in (None, monster.position):
            #move towards player if far away
            if euclidean_distance(monster.position, monster.target_pos) >= 2:
                path = self.__clevel.get_path_to_pos(monster, monster.target_pos)
                if path is not None and not self.is_blocked(path):
                    monster.position = Point(path[0], path[1])

    def take_turn(self):
        self.__clevel.compute_path()

        for monster in self.__clevel.monsters:
            #a basic monster takes its turn. If you can see it, it can see you
            if not monster.died:
                self.__take_turn_monster(monster)

    def take_item_from_player(self, item):
        messages = MessagesBorg()
        messages.add('You dropped a ' + item.name + '.', libtcod.yellow)
        self.player.remove_item(item)
        item.position = self.player.position
        self.__clevel.items.append(item)

    def give_item_to_player(self):
        messages = MessagesBorg()
        for item in self.__clevel.items:
            if item.position == self.player.position:
                if self.player.add_item(item) is True:
                    messages.add('You picked up a ' + item.name + '! (' + item.key + ')', libtcod.green)
                    self.__clevel.items.remove(item)
                else:
                    messages.add('Your inventory is full, cannot pick up ' +
                             item.name + '.', libtcod.red)

    def monsters_in_area(self, pos, radius):
        return [m for m in self.__clevel.monsters
                if euclidean_distance(pos, m.position) <= radius]

    def climb_stairs(self):
        messages = MessagesBorg()

        pos = self.player.position
        stairs = next((s for s in self.__clevel.stairs if s.position == pos), None)

        if stairs == None:
            messages.add('There are no stairs here.', libtcod.orange)
            return

        messages.add('You climb some stairs..', libtcod.green)
        self._model.current_level = stairs.destiny
        self.move_player(0, 0)

    def clear_ui(self, con):
        self._view.clear(con)
        erase_object(con, self.player)

    def draw_ui(self, con, draw_outside_fov):
        self._view.draw(con, draw_outside_fov)

        draw_object(con, self.player)

    def draw_name(self, con, x, y):
        self._view.draw_name(con, x, y)
