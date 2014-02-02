import libtcodpy as libtcod
from config import *

color_none = libtcod.Color(0, 0, 0)
color_dark_wall = libtcod.Color(0, 0, 200)
color_light_wall = libtcod.Color(200, 200, 200)
color_dark_ground = libtcod.Color(0, 0, 70)
color_light_ground = libtcod.Color(0, 25, 50)


class Level:
    def __init__(self):
        self.bkgd = libtcod.BKGND_NONE

    def __draw_items(self, console, model, draw_not_in_fov=False):
        for item in model.items:
            (x, y) = item.position
            if libtcod.map_is_in_fov(model.fov_map, x, y) or draw_not_in_fov:
                item.draw_ui(console)

    def __draw_monsters(self, console, model, draw_dead=False, draw_not_in_fov=False):
        #go through all monsters
        for monster in model.monsters:
            (x, y) = monster.position
            if libtcod.map_is_in_fov(model.fov_map, x, y) or draw_not_in_fov:
                if draw_dead == monster.died:
                    monster.draw_ui(console)

    def draw(self, console, model, draw_not_in_fov=False):
        #go through all tiles, and set their background color
        for y in range(MAP_HEIGHT):
            for x in range(MAP_WIDTH):
                wall = model.tiles[x][y].block_sight
                visible = libtcod.map_is_in_fov(model.fov_map, x, y)
                explored = model.tiles[x][y].explored

                color = color_none
                if visible or draw_not_in_fov:
                    color = color_light_wall if wall else color_light_ground
                elif explored:
                    color = color_dark_wall if wall else color_dark_ground

                libtcod.console_set_char_background(console,
                                                    x,
                                                    y,
                                                    color,
                                                    libtcod.BKGND_SET)



                # draw stairs
                if visible or draw_not_in_fov:
                    if (x, y) == model.stairs_up_pos:
                        libtcod.console_put_char(console, x, y, '<', self.bkgd)
                    elif (x, y) == model.stairs_down_pos:
                        libtcod.console_put_char(console, x, y, '>', self.bkgd)

        # start by drawing the monsters that have died
        self.__draw_monsters(console, model, True, draw_not_in_fov)

        #then the items on the floor
        self.__draw_items(console, model, draw_not_in_fov)

        #and finally, the monsters that are still alive
        self.__draw_monsters(console, model, False, draw_not_in_fov)

        #draw temporary artifacts
        for artifact in model.temp_artifacts:
            x, y = artifact[0]
            libtcod.console_put_char(console, x, y, artifact[1], self.bkgd)

    def clear(self, console, model):
        #erase the character that represents this object
        (x, y) = model.stairs_up_pos
        libtcod.console_put_char(console, x, y, ' ', self.bkgd)

        (x, y) = model.stairs_down_pos
        libtcod.console_put_char(console, x, y, ' ', self.bkgd)

        #decrement the turns left for each temporary artifact
        #if it becomes 0, remove them
        for artifact in model.temp_artifacts:
            x, y = artifact[0]
            libtcod.console_put_char(console, x, y, ' ', self.bkgd)
