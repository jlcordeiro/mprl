import libtcodpy as libtcod
from config import *
from messages import *
from platform.ui import *
from platform.keyboard import *
from utilities.geometry import Rect
import controllers.creatures
import controllers.dungeon

DRAW_NOT_IN_FOV = False

game_state = 'playing'
player_action = None

dungeon = controllers.dungeon.Dungeon()


HP_RECT = Rect(1, 1, BAR_WIDTH, 1)
HP_BAR = UIBar('HP', libtcod.darker_red, libtcod.light_red)

gap = (SCREEN_WIDTH - INVENTORY_WIDTH)
SCREEN_RECT = Rect(gap/2, gap/2, INVENTORY_WIDTH, SCREEN_HEIGHT - gap)

def aim():
    (x, y) = dungeon.player.position

    while True:
        dungeon.aim_target = (x, y)
        draw_everything()

        #turn-based
        key = wait_keypress()

        if key_is_escape(key):
            dungeon.aim_target = None
            return

        if key.vk == libtcod.KEY_ENTER:
            dungeon.aim_target = (x, y)
            return

        movement = get_key_direction(key)
        if movement is not None:
            dx, dy = movement
            (x, y) = (x + dx, y + dy)


def handle_keys():
    global DRAW_NOT_IN_FOV

    #turn-based
    key = wait_keypress()

    if key_is_escape(key):
        return "exit"

    if game_state == 'playing':
        #movement keys
        movement = get_key_direction(key)
        if movement is not None:
            dx, dy = movement
            dungeon.move_player(dx, dy)

        elif chr(key.c) == 'i':
            chosen_item = inventory_menu(con)

            if chosen_item is None:
                return

            if chosen_item.type == "cast":
                item_range = chosen_item.range
                affected_monsters = []

                if chosen_item.who_is_affected == 'aim':
                    aim()
                    affected_monsters = dungeon.monsters_in_area(dungeon.aim_target,
                                                                 item_range)

                elif chosen_item.who_is_affected == 'closest':
                    closest_one = dungeon.closest_monster_to_player(item_range)
                    if closest_one is not None:
                        affected_monsters.append(closest_one)

                if chosen_item.use(dungeon.player, affected_monsters) is True:
                    dungeon.player.remove_item(chosen_item)

            elif chosen_item.type == "melee":
                dungeon.player.equip(chosen_item)

        elif chr(key.c) == 'd':
            #show the inventory; if an item is selected, drop it
            chosen_item = inventory_menu(con)
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

def inventory_menu(console):
    #show a menu with each item of the inventory as an option
    items = dungeon.player.items
    options = [i.name for i in items]
    if len(options) == 0:
        messages.add('Inventory is empty.', libtcod.orange)
        return

    header = "Press the key next to an item to drop it, or any other to cancel.\n"
    index = option_menu(console, header, options, SCREEN_RECT)

    #if an item was chosen, return it
    if index is None:
        return None

    return items[index]

def flush():
    #blit the contents of "console" to the root console
    libtcod.console_blit(con, 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, 0, 0, 0)

    #blit the contents of "panel" to the root console
    libtcod.console_blit(panel, 0, 0, SCREEN_WIDTH, PANEL_HEIGHT, 0, 0, PANEL_Y)

    libtcod.console_flush()
    dungeon.clear_ui(con)

def draw_everything():
    #render the screen
    dungeon.draw_ui(con, DRAW_NOT_IN_FOV)

    #prepare to render the GUI panel
    libtcod.console_set_default_background(panel, libtcod.black)
    libtcod.console_clear(panel)

    #show the player's stats
    HP_BAR.update(dungeon.player.hp, dungeon.player.max_hp)
    HP_BAR.draw(panel, HP_RECT)

    libtcod.console_print_ex(panel, 1, 2, libtcod.BKGND_NONE, libtcod.LEFT,
                             "Attack: " + str(dungeon.player.power))

    libtcod.console_print_ex(panel, 1, 3, libtcod.BKGND_NONE, libtcod.LEFT,
                             "Defense: " + str(dungeon.player.defense))

    #print the game messages, one line at a time
    y = 1
    for (line, color) in messages.get_all():
        libtcod.console_set_default_foreground(panel, color)
        libtcod.console_print_ex(panel, MSG_X, y,
                                 libtcod.BKGND_NONE, libtcod.LEFT,
                                 line)
        y += 1

    flush()

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
