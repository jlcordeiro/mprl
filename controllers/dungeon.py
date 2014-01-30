import libtcodpy as libtcod
from utils import euclidean_distance
import random
import views.dungeon
import models.dungeon
from items import ItemFactory
from creatures import MonsterFactory
from config import *
from messages import *

class Level:
    def __init__(self):
        self._model = models.dungeon.Level()
        self._view = views.dungeon.Level(self._model)

        self._model.generate()
        self.set_fov()

    def move_player(self, dx, dy):
        x, y = self._model.move_player(dx, dy)

        libtcod.map_compute_fov(self._view.fov_map,
                                x,
                                y,
                                TORCH_RADIUS,
                                FOV_LIGHT_WALLS,
                                FOV_ALGO)

        for y in range(MAP_HEIGHT):
            for x in range(MAP_WIDTH):
                if self.is_in_fov((x, y)):
                    self._model.tiles[x][y].explored = True

    def is_blocked(self, pos):
        return self._model.is_blocked(pos)

    def is_in_fov(self, pos):
        return libtcod.map_is_in_fov(self._view.fov_map, pos[0], pos[1]) 

    def set_fov(self):
        for y in range(MAP_HEIGHT):
            for x in range(MAP_WIDTH):
                is_transparent = not self._model.tiles[x][y].block_sight
                is_walkable = not self._model.tiles[x][y].blocked
                libtcod.map_set_properties(self._view.fov_map,
                                           x,
                                           y,
                                           is_transparent,
                                           is_walkable)


    def clear_ui(self, con):
        self._view.clear(con)

        self.player.clear_ui(con)

        for monster in self._model.monsters:
            monster.clear_ui(con)

        for item in self._model.items:
            item.clear_ui(con)

    def draw_ui(self, con, draw_outside_fov):
        self._view.draw(con, draw_outside_fov)
        self.player.draw_ui(con)

    def closest_monster_to_player_in_fov(self, max_range):
        closest_enemy = self._model.closest_monster_to_player(max_range)

        if closest_enemy is None:
            return None

        x, y = closest_enemy.position
        if self.is_in_fov((x, y)):
            return closest_enemy

        return None 

    @property
    def player(self):
        return self._model.player

    def get_monsters(self):
        return self._model.monsters

    def take_item_from_player(self, item):
        self.player.drop_item(item)
        self._model.items.append(item)

    def give_item_to_player(self):
        for item in self._model.items:
            if item.position == self.player.position:
                if self.player.pick_item(item) is True:
                    self._model.items.remove(item)

    def monsters_in_area(self, pos, radius):
        return [m for m in self._model.monsters
                if euclidean_distance(pos, m.position) <= radius]

    def climb_stairs(self):
        valid_pos = (self._model.stairs_up_pos, self._model.stairs_down_pos)

        messages = MessagesBorg()
        if self.player.position not in valid_pos:
            messages.add('There are no stairs here.', libtcod.orange)
        else:
            messages.add('You walk down fake stairs..', libtcod.green)

    def __take_turn_monster(self, monster):
        previous_pos = monster.position

        messages = MessagesBorg()
        if monster.confused_turns > 0:
            monster.confused_move()

            if method_check_blocks(monster.position) is False:
                monster.move(new_pos = previous_pos)
        else:
            #move towards player if far away
            if monster.distance_to(self.player) >= 2:
                path = self._model.get_path_to_player(monster)
                if path is not None and not self.is_blocked(path):
                    monster.move(new_pos=path)
            #close enough, attack! (if the player is still alive.)
            elif self.player.hp > 0:
                monster.attack(self.player)


    def take_turn(self):
        self._model.compute_path()

        for monster in self.get_monsters():
            #a basic monster takes its turn. If you can see it, it can see you
            if not monster.died and self.is_in_fov(monster.position):
                self.__take_turn_monster(monster)
