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

    def move_player(self, dx, dy):
        self._model.move_player(dx, dy)

    def closest_monster_to_player(self, max_range):
        pos = self.player.position
        return self._model.level.closest_monster_to_pos(pos, max_range)

    def is_blocked(self, pos):
        return self._model.level.is_blocked(pos)

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
                path = self._model.level.get_path_to_pos(monster, self.player.position)
                if path is not None and not self.is_blocked(path):
                    monster.move(new_pos=path)
            #close enough, attack! (if the player is still alive.)
            elif self.player.hp > 0:
                monster.attack(self.player)

    def take_turn(self):
        self._model.level.compute_path()

        for monster in self._model.level.monsters:
            #a basic monster takes its turn. If you can see it, it can see you
            if not monster.died and self._model.level.is_in_fov(monster.position):
                self.__take_turn_monster(monster)

    def take_item_from_player(self, item):
        self.player.drop_item(item)
        self._model.level.items.append(item)

    def give_item_to_player(self):
        for item in self._model.level.items:
            if item.position == self.player.position:
                if self.player.pick_item(item) is True:
                    self._model.level.items.remove(item)

    def monsters_in_area(self, pos, radius):
        return [m for m in self._model.level.monsters
                if euclidean_distance(pos, m.position) <= radius]

    def climb_stairs(self):
        valid_pos = (self._model.level.stairs_up_pos,
                     self._model.level.stairs_down_pos)

        messages = MessagesBorg()
        if self.player.position not in valid_pos:
            messages.add('There are no stairs here.', libtcod.orange)
        else:
            messages.add('You walk down fake stairs..', libtcod.green)

    def clear_ui(self, con):
        self._view.clear(con, self._model.level)

        self.player.clear_ui(con)

        for monster in self._model.level.monsters:
            monster.clear_ui(con)

        for item in self._model.level.items:
            item.clear_ui(con)

    def draw_ui(self, con, draw_outside_fov):
        self._view.draw(con, self._model.level, draw_outside_fov)
        self.player.draw_ui(con)

