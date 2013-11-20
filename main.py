import libtcodpy as libtcod
from config import *
from dungeon import *
from messages import *
 
game_state = 'playing'
player_action = None

dungeon = LevelController()
(x,y) = dungeon.get_unblocked_pos()
player = Player(x,y)

def move_player(dx,dy):

   player.move(dx,dy)

   for monster in dungeon.model.monsters:
      if monster.get_position() == player.get_position() and monster.blocks():
         player.attack(monster)
         player.move(-dx,-dy)
   
   if dungeon.is_blocked(player.get_position()):
      player.move(-dx,-dy)
   
   dungeon.update(player.get_position())

def render_bar(x, y, total_width, name, value, maximum, bar_color, back_color):
   #render a bar (HP, experience, etc). first calculate the width of the bar
   bar_width = int(float(value) / maximum * total_width)

   #render the background first
   libtcod.console_set_default_background(panel, back_color)
   libtcod.console_rect(panel, x, y, total_width, 1, False, libtcod.BKGND_SCREEN)

   #now render the bar on top
   libtcod.console_set_default_background(panel, bar_color)
   if bar_width > 0:
      libtcod.console_rect(panel, x, y, bar_width, 1, False, libtcod.BKGND_SCREEN)

   #finally, some centered text with the values
   libtcod.console_set_default_foreground(panel, libtcod.white)
   libtcod.console_print_ex(panel, x + total_width / 2, y, libtcod.BKGND_NONE, libtcod.CENTER,name + ': ' + str(value) + '/' + str(maximum))


def handle_keys():
   #key = libtcod.console_check_for_keypress()  #real-time
   key = libtcod.console_wait_for_keypress(True)  #turn-based
            
   if key.vk == libtcod.KEY_ESCAPE:
      return "exit"
                
   if game_state == 'playing':
      #movement keys
      if libtcod.console_is_key_pressed(libtcod.KEY_UP):
         move_player(0,-1)

      elif libtcod.console_is_key_pressed(libtcod.KEY_DOWN):
         move_player(0,1)

      elif libtcod.console_is_key_pressed(libtcod.KEY_LEFT):
         move_player(-1,0)

      elif libtcod.console_is_key_pressed(libtcod.KEY_RIGHT):
         move_player(1,0)

      elif chr(key.c) == 'g':
         #pick up an item
         for item in dungeon.model.items:  #look for an item in the player's tile
            if item.get_position() == player.get_position():
               if player.pick_item(item) is True:
                  dungeon.model.items.remove(item)

      else:
         return 'did-not-take-turn'


#############################################
# Initialization & Main Loop
#############################################

libtcod.console_set_custom_font('./resources/fonts/arial10x10.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)
libtcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, 'mprl', False)
libtcod.sys_set_fps(LIMIT_FPS)
con = libtcod.console_new(MAP_WIDTH, MAP_HEIGHT)
panel = libtcod.console_new(SCREEN_WIDTH, PANEL_HEIGHT)

move_player(0,0)

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
      libtcod.console_print_ex(panel, MSG_X, y, libtcod.BKGND_NONE, libtcod.LEFT, line)
      y += 1
    
   #show the player's stats
   render_bar(1, 1, BAR_WIDTH, 'HP', player.model.hp, player.model.max_hp,
                     libtcod.light_red, libtcod.darker_red)
    
   #blit the contents of "panel" to the root console
   libtcod.console_blit(panel, 0, 0, SCREEN_WIDTH, PANEL_HEIGHT, 0, 0, PANEL_Y)

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
         if monster.ai is not None:
            #a basic monster takes its turn. If you can see it, it can see you
            (owner_x,owner_y) = monster.get_position()
            if libtcod.map_is_in_fov(dungeon.view.fov_map, owner_x, owner_y):
               monster.ai.take_turn(monster,player,dungeon.is_blocked)

   if player.has_died():
      messages.add("YOU DIED!",libtcod.red)
      game_state = 'dead'

