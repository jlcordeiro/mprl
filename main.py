import libtcodpy as libtcod
from path import take_turn
from config import *
from messages import *
from platform.ui import *
from platform.keyboard import *
import controllers.creatures
import controllers.dungeon

DRAW_NOT_IN_FOV = False

game_state = 'playing'
player_action = None

dungeon = controllers.dungeon.Dungeon()

HP_BAR = UIBar('HP', libtcod.darker_red, libtcod.light_red)

def aim():
    (x, y) = dungeon.player.position

    while True:
        dungeon.aim_target = (x, y)
        draw_everything()

        flush()
        dungeon.clear_ui(con)

        #turn-based
        key = wait_keypress()

        if key_is_escape(key):
            dungeon.aim_target = None
            return

        if key.vk == libtcod.KEY_ENTER:
            dungeon.aim_target = (x, y)
            return

        if key_is_up_move(key):
            y -= 1
        elif key_is_down_move(key):
            y += 1
        elif key_is_left_move(key):
            x -= 1
        elif key_is_right_move(key):
            x += 1


def handle_keys():
    global DRAW_NOT_IN_FOV

    #turn-based
    key = wait_keypress()

    if key_is_escape(key):
        return "exit"

    if game_state == 'playing':
        #movement keys
        if key_is_up_move(key):
            dungeon.move_player(0, -1)

        elif key_is_down_move(key):
            dungeon.move_player(0, 1)

        elif key_is_left_move(key):
            dungeon.move_player(-1, 0)

        elif key_is_right_move(key):
            dungeon.move_player(1, 0)

        elif key_is_upleft_move(key):
            dungeon.move_player(-1, -1)

        elif key_is_upright_move(key):
            dungeon.move_player(1, -1)

        elif key_is_downleft_move(key):
            dungeon.move_player(-1, 1)

        elif key_is_downright_move(key):
            dungeon.move_player(1, 1)

        elif chr(key.c) == 'i':
            chosen_item = inventory_menu(con,
                                         "Press the key next to an item " +
                                         " to use it," +
                                         "or any other to cancel.\n")

            if chosen_item is not None:
                item_range = chosen_item.affects_range
                affected_monsters = []

                if chosen_item.who_is_affected == 'aim':
                    aim()
                    affected_monsters = dungeon.monsters_in_area(dungeon.aim_target,
                                                                 item_range)

                elif chosen_item.who_is_affected == 'closest':
                    closest_one = dungeon.closest_monster_to_player(item_range)
                    if closest_one is not None:
                        affected_monsters.append(closest_one)

                if chosen_item.cast(dungeon.player, affected_monsters) is True:
                    dungeon.player.remove_item(chosen_item)

        elif chr(key.c) == 'd':
            #show the inventory; if an item is selected, drop it
            chosen_item = inventory_menu(con,
                                         "Press the key next to an item " +
                                         "to drop it," +
                                         "or any other to cancel.\n")
            if chosen_item is not None:
                dungeon.take_item_from_player(chosen_item)

        elif chr(key.c) == 'g':
            #pick up an item
            dungeon.give_item_to_player()
        else:
            if chr(key.c) == 'v':
                DRAW_NOT_IN_FOV = not DRAW_NOT_IN_FOV
            elif chr(key.c) in ('>', '<'):
                dungeon.climb_stairs()

            return 'did-not-take-turn'



def inventory_menu(console, header):
    #show a menu with each item of the inventory as an option
    items = dungeon.player.items
    options = [i.name for i in items]
    if len(options) == 0:
        messages.add('Inventory is empty.', libtcod.orange)
        return

    index = menu(console, header, options, INVENTORY_WIDTH, SCREEN_WIDTH, SCREEN_HEIGHT)

    #if an item was chosen, return it
    if index is None:
        return None

    return items[index]

def draw_everything():
    #render the screen
    dungeon.draw_ui(con, DRAW_NOT_IN_FOV)

    #prepare to render the GUI panel
    libtcod.console_set_default_background(panel, libtcod.black)
    libtcod.console_clear(panel)

    #show the player's stats
    HP_BAR.update(dungeon.player.hp, dungeon.player.max_hp)
    HP_BAR.draw(panel, 1, 1, BAR_WIDTH)

    #print the game messages, one line at a time
    y = 1
    for (line, color) in messages.get_all():
        libtcod.console_set_default_foreground(panel, color)
        libtcod.console_print_ex(panel,
                                 MSG_X, y,
                                 libtcod.BKGND_NONE,
                                 libtcod.LEFT,
                                 line)
        y += 1

def flush():
    #blit the contents of "console" to the root console
    libtcod.console_blit(con, 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, 0, 0, 0)

    #blit the contents of "panel" to the root console
    libtcod.console_blit(panel,
                         0,
                         0,
                         SCREEN_WIDTH,
                         PANEL_HEIGHT,
                         0,
                         0,
                         PANEL_Y)

    libtcod.console_flush()

#############################################
# Initialization & Main Loop
#############################################

flags = libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD
libtcod.console_set_custom_font('./resources/fonts/arial10x10.png', flags)
libtcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, 'mprl', False)
libtcod.sys_set_fps(LIMIT_FPS)
con = libtcod.console_new(MAP_WIDTH, MAP_HEIGHT)
panel = libtcod.console_new(SCREEN_WIDTH, PANEL_HEIGHT)

dungeon.move_player(0, 0)

messages = MessagesBorg()
messages.add('Welcome stranger!', libtcod.red)

while not libtcod.console_is_window_closed():
    draw_everything()
    flush()

    dungeon.clear_ui(con)

    #handle keys and exit game if needed
    player_action = handle_keys()
    if player_action == "exit":
        break

    #let monsters take their turn
    if game_state == "playing" and player_action != 'did-not-take-turn':
        dungeon.take_turn()

    if dungeon.player.died and game_state != 'dead':
        messages.add("YOU DIED!", libtcod.red)
        game_state = 'dead'
