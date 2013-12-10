import libtcodpy as libtcod
from config import *
from dungeon import *
from messages import *
import controllers.creatures
import controllers.dungeon

game_state = 'playing'
player_action = None

dungeon = controllers.dungeon.Level()
(x, y) = dungeon.get_unblocked_pos()
player = controllers.creatures.Player(x, y)


def move_player(dx, dy):

    player.move(dx, dy)

    for monster in dungeon.model.monsters:
        if monster.position == player.position and monster.blocks:
            player.attack(monster)
            player.move(-dx, -dy)

    if dungeon.is_blocked(player.position):
        player.move(-dx, -dy)

    dungeon.update(player.position)


def closest_monster(max_range):
    #find closest enemy, up to a maximum range, and in the player's FOV
    closest_enemy = None
    closest_dist = max_range + 1

    for monster in dungeon.model.monsters:
        x, y = monster.position
        if libtcod.map_is_in_fov(dungeon.view.fov_map, x, y):
            #calculate distance between this object and the player
            dist = monster.distance_to(player)
            if dist < closest_dist:
                closest_enemy = monster
                closest_dist = dist

    return closest_enemy


def render_bar(x, y, total_width, name, value, maximum, bar_color, back_color):
    #render a bar (HP, experience, etc). first calculate the width of the bar
    bar_width = int(float(value) / maximum * total_width)

    #render the background first
    libtcod.console_set_default_background(panel, back_color)
    libtcod.console_rect(panel,
                         x,
                         y,
                         total_width,
                         1,
                         False,
                         libtcod.BKGND_SCREEN)

    #now render the bar on top
    libtcod.console_set_default_background(panel, bar_color)
    if bar_width > 0:
        libtcod.console_rect(panel,
                             x,
                             y,
                             bar_width,
                             1,
                             False,
                             libtcod.BKGND_SCREEN)

    #finally, some centered text with the values
    libtcod.console_set_default_foreground(panel, libtcod.white)
    libtcod.console_print_ex(panel,
                             x + total_width / 2,
                             y,
                             libtcod.BKGND_NONE,
                             libtcod.CENTER,
                             name + ': ' + str(value) + '/' + str(maximum))


def handle_keys():
    #turn-based
    key = libtcod.console_wait_for_keypress(True)

    if key.vk == libtcod.KEY_ESCAPE:
        return "exit"

    if game_state == 'playing':
        #movement keys
        if libtcod.console_is_key_pressed(libtcod.KEY_UP):
            move_player(0, -1)

        elif libtcod.console_is_key_pressed(libtcod.KEY_DOWN):
            move_player(0, 1)

        elif libtcod.console_is_key_pressed(libtcod.KEY_LEFT):
            move_player(-1, 0)

        elif libtcod.console_is_key_pressed(libtcod.KEY_RIGHT):
            move_player(1, 0)

        elif chr(key.c) == 'i':
            chosen_item = inventory_menu(con,
                                         "Press the key next to an item " +
                                         " to use it," +
                                         "or any other to cancel.\n")
            if chosen_item is not None:
                affected_monsters = []

                if chosen_item.who_is_affected == 'closest':
                    closest_one = closest_monster(chosen_item.affects_range)

                    if closest_one is not None:
                        affected_monsters.append(closest_one)

                if chosen_item.cast(player, affected_monsters) is True:
                    player.model.inventory.remove(chosen_item)

        elif chr(key.c) == 'd':
            #show the inventory; if an item is selected, drop it
            chosen_item = inventory_menu(con,
                                         "Press the key next to an item " +
                                         "to drop it," +
                                         "or any other to cancel.\n")
            if chosen_item is not None:
                player.drop_item(chosen_item)
                dungeon.model.items.append(chosen_item)

        elif chr(key.c) == 'g':
            #pick up an item
            for item in dungeon.model.items:
                if item.position == player.position:
                    if player.pick_item(item) is True:
                        dungeon.model.items.remove(item)

        else:
            return 'did-not-take-turn'


def menu(con, header, options, width):
    if len(options) > 26:
        raise ValueError('Cannot have a menu with more than 26 options.')

    #calculate total height for the header (after auto-wrap)
    header_height = libtcod.console_get_height_rect(con,
                                                    0,
                                                    0,
                                                    width,
                                                    SCREEN_HEIGHT,
                                                    header)
    height = len(options) + header_height

    #create an off-screen console that represents the menu's window
    window = libtcod.console_new(width, height)

    #print the header, with auto-wrap
    libtcod.console_set_default_foreground(window, libtcod.white)
    libtcod.console_print_rect_ex(window,
                                  0,
                                  0,
                                  width,
                                  height,
                                  libtcod.BKGND_NONE,
                                  libtcod.LEFT,
                                  header)

    #print all the options
    y = header_height
    letter_index = ord('a')
    for option_text in options:
        text = '(' + chr(letter_index) + ') ' + option_text
        libtcod.console_print_ex(window,
                                 0,
                                 y,
                                 libtcod.BKGND_NONE,
                                 libtcod.LEFT,
                                 text)
        y += 1
        letter_index += 1

    #blit the contents of "window" to the root console
    x = SCREEN_WIDTH / 2 - width / 2
    y = SCREEN_HEIGHT / 2 - height / 2
    libtcod.console_blit(window, 0, 0, width, height, 0, x, y, 1.0, 0.7)

    #wait for a key-press
    libtcod.console_flush()
    key = libtcod.console_wait_for_keypress(True)

    #convert the ASCII code to an index;
    index = key.c - ord('a')
    #if it corresponds to an option, return it
    if index >= 0 and index < len(options):
        return index

    return None


def inventory_menu(console, header):
    #show a menu with each item of the inventory as an option
    if len(player.model.inventory) == 0:
        options = ['Inventory is empty.']
    else:
        options = [item.name for item in player.model.inventory]

    index = menu(console, header, options, INVENTORY_WIDTH)

    #if an item was chosen, return it
    if index is None or len(player.model.inventory) == 0:
        return None

    return player.model.inventory[index]

#############################################
# Initialization & Main Loop
#############################################

flags = libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD
libtcod.console_set_custom_font('./resources/fonts/arial10x10.png', flags)
libtcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, 'mprl', False)
libtcod.sys_set_fps(LIMIT_FPS)
con = libtcod.console_new(MAP_WIDTH, MAP_HEIGHT)
panel = libtcod.console_new(SCREEN_WIDTH, PANEL_HEIGHT)

move_player(0, 0)

messages = MessagesBorg()
messages.add('Welcome stranger!', libtcod.red)

while not libtcod.console_is_window_closed():
    #render the screen
    dungeon.view.draw(con)
    player.view.draw(con)

    #blit the contents of "console" to the root console
    libtcod.console_blit(con, 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, 0, 0, 0)

    #prepare to render the GUI panel
    libtcod.console_set_default_background(panel, libtcod.black)
    libtcod.console_clear(panel)

    #print the game messages, one line at a time
    y = 1
    for (line, color) in messages.get_all():
        libtcod.console_set_default_foreground(panel, color)
        libtcod.console_print_ex(panel,
                                 MSG_X,
                                 y,
                                 libtcod.BKGND_NONE,
                                 libtcod.LEFT,
                                 line)
        y += 1

    #show the player's stats
    render_bar(1, 1, BAR_WIDTH, 'HP', player.model.hp, player.model.max_hp,
               libtcod.light_red, libtcod.darker_red)

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

    player.view.clear(con)
    for monster in dungeon.model.monsters:
        monster.view.clear(con)

    #handle keys and exit game if needed
    key = handle_keys()
    if key == "exit":
        break

    #let monsters take their turn
    if game_state == "playing" and player_action != 'did-not-take-turn':
        for monster in dungeon.model.monsters:
            #a basic monster takes its turn. If you can see it, it can see you
            (owner_x, owner_y) = monster.position
            if libtcod.map_is_in_fov(dungeon.view.fov_map, owner_x, owner_y):
                take_turn(monster, player, dungeon.is_blocked)

    if player.died:
        messages.add("YOU DIED!", libtcod.red)
        game_state = 'dead'
