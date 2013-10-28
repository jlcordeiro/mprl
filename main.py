import libtcodpy as libtcod
from objects import *
 
#actual size of the window
SCREEN_WIDTH = 80
SCREEN_HEIGHT = 50
 
LIMIT_FPS = 20  #20 frames-per-second maximum
 
player = Player(SCREEN_WIDTH/2, SCREEN_HEIGHT/2)
 
def handle_keys():
   #key = libtcod.console_check_for_keypress()  #real-time
   key = libtcod.console_wait_for_keypress(True)  #turn-based
            
   if key.vk == libtcod.KEY_ENTER and key.lalt:
      #Alt+Enter: toggle fullscreen
      libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())
   elif key.vk == libtcod.KEY_ESCAPE:
      return True  #exit game
                
   #movement keys
   if libtcod.console_is_key_pressed(libtcod.KEY_UP):
      player.move(0,-1)

   elif libtcod.console_is_key_pressed(libtcod.KEY_DOWN):
      player.move(0,1)

   elif libtcod.console_is_key_pressed(libtcod.KEY_LEFT):
      player.move(-1,0)

   elif libtcod.console_is_key_pressed(libtcod.KEY_RIGHT):
      player.move(1,0)


#############################################
# Initialization & Main Loop
#############################################

libtcod.console_set_custom_font('./resources/fonts/arial10x10.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)
libtcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, 'python/libtcod tutorial', False)
libtcod.sys_set_fps(LIMIT_FPS)
con = libtcod.console_new(SCREEN_WIDTH, SCREEN_HEIGHT)

while not libtcod.console_is_window_closed():
       
   player.view.draw(con)

   libtcod.console_blit(con, 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, 0, 0, 0)   
   libtcod.console_flush()
       
   player.view.clear(con)
           
   #handle keys and exit game if needed
   exit = handle_keys()
   if exit:
      break
