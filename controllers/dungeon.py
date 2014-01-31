import libtcodpy as libtcod
from utils import euclidean_distance
import random
import views.dungeon
import models.dungeon
from items import ItemFactory
from creatures import MonsterFactory
from config import *
from messages import *

class Dungeon:
    def __init__(self):
        self._model = models.dungeon.Dungeon()
        self._view = views.dungeon.Level()
    
    @property
    def player(self):
        return self._model.player

    @property
    def __clevel(self):
        """ Return the current level. """
        return self._model.levels[self._model.current_level]

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
                monster.move(new_pos = previous_pos)
        else:
            #move towards player if far away
            if monster.distance_to(self.player.position) >= 2:
                path = self.__clevel.get_path_to_pos(monster, self.player.position)
                if path is not None and not self.is_blocked(path):
                    monster.move(new_pos=path)
            #close enough, attack! (if the player is still alive.)
            elif self.player.hp > 0:
                monster.attack(self.player)

    def take_turn(self):
        self.__clevel.compute_path()

        for monster in self.__clevel.monsters:
            #a basic monster takes its turn. If you can see it, it can see you
            if not monster.died and self.__clevel.is_in_fov(monster.position):
                self.__take_turn_monster(monster)

    def take_item_from_player(self, item):
        self.player.drop_item(item)
        self.__clevel.items.append(item)

    def give_item_to_player(self):
        for item in self.__clevel.items:
            if item.position == self.player.position:
                if self.player.pick_item(item) is True:
                    self.__clevel.items.remove(item)

    def monsters_in_area(self, pos, radius):
        return [m for m in self.__clevel.monsters
                if euclidean_distance(pos, m.position) <= radius]

    def climb_stairs(self):
        messages = MessagesBorg()
        if self.player.position == self.__clevel.stairs_up_pos:
            messages.add('You climb up some stairs..', libtcod.green)
            self._model.current_level -= 1
            self.player.move(new_pos = self.__clevel.stairs_down_pos)
            self.move_player(0, 0)
        elif self.player.position == self.__clevel.stairs_down_pos:
            messages.add('You climb down some stairs..', libtcod.green)
            self._model.current_level += 1
            self.player.move(new_pos = self.__clevel.stairs_up_pos)
            self.move_player(0, 0)
        else:
            messages.add('There are no stairs here.', libtcod.orange)

    def clear_ui(self, con):
        self._view.clear(con, self.__clevel)

        self.player.clear_ui(con)

        for monster in self.__clevel.monsters:
            monster.clear_ui(con)

        for item in self.__clevel.items:
            item.clear_ui(con)

    def draw_ui(self, con, draw_outside_fov):
        self._view.draw(con, self.__clevel, draw_outside_fov)
        self.player.draw_ui(con)

