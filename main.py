import libtcodpy as libtcod
from objects import *
from dungeon import *
 
#actual size of the window
SCREEN_WIDTH = 80
SCREEN_HEIGHT = 50
 
LIMIT_FPS = 20  #20 frames-per-second maximum
 
player = Player(SCREEN_WIDTH/2, SCREEN_HEIGHT/2)
dungeon = LevelController()

def move_player(dx,dy):
   player.move(dx,dy)
   dungeon.compute_fov(player.get_position())
 
def handle_keys():
   #key = libtcod.console_check_for_keypress()  #real-time
   key = libtcod.console_wait_for_keypress(True)  #turn-based
            
   if key.vk == libtcod.KEY_ESCAPE:
      return True  #exit game
                
   #movement keys
   if libtcod.console_is_key_pressed(libtcod.KEY_UP):
      move_player(0,-1)

   elif libtcod.console_is_key_pressed(libtcod.KEY_DOWN):
      move_player(0,1)

   elif libtcod.console_is_key_pressed(libtcod.KEY_LEFT):
      move_player(-1,0)

   elif libtcod.console_is_key_pressed(libtcod.KEY_RIGHT):
      move_player(1,0)


#############################################
# Initialization & Main Loop
#############################################

libtcod.console_set_custom_font('./resources/fonts/arial10x10.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)
libtcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, 'mprl', False)
libtcod.sys_set_fps(LIMIT_FPS)
con = libtcod.console_new(SCREEN_WIDTH, SCREEN_HEIGHT)

while not libtcod.console_is_window_closed():

   #render the screen
   dungeon.view.draw(con)
   player.view.draw(con)
 
   #blit the contents of "console" to the root console
   libtcod.console_blit(con, 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, 0, 0, 0)   
   libtcod.console_flush()
       
   player.view.clear(con)
           
   #handle keys and exit game if needed
   exit = handle_keys()
   if exit:
      break
