import libtcodpy as libtcod
from dungeon import *
 
#actual size of the window
SCREEN_WIDTH = 80
SCREEN_HEIGHT = 50
 
LIMIT_FPS = 20  #20 frames-per-second maximum
 
game_state = 'playing'
player_action = None

dungeon = LevelController()
(x,y) = dungeon.get_unblocked_pos()
player = Player(x,y)

def move_player(dx,dy):

   player.move(dx,dy)

   for monster in dungeon.model.monsters:
      if monster.get_position() == player.get_position() and monster.blocks():
         print 'The ' + monster.name + ' laughs at your puny efforts to attack him!'
         player.attack(monster)
         player.move(-dx,-dy)
   
   if dungeon.is_blocked(player.get_position()):
      player.move(-dx,-dy)
   
   dungeon.update(player.get_position())

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
      else:
         return 'did-not-take-turn'


#############################################
# Initialization & Main Loop
#############################################

libtcod.console_set_custom_font('./resources/fonts/arial10x10.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)
libtcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, 'mprl', False)
libtcod.sys_set_fps(LIMIT_FPS)
con = libtcod.console_new(SCREEN_WIDTH, SCREEN_HEIGHT)

move_player(0,0)

while not libtcod.console_is_window_closed():

   #render the screen
   dungeon.view.draw(con)
   player.view.draw(con)
 
   #blit the contents of "console" to the root console
   libtcod.console_blit(con, 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, 0, 0, 0)   

   #show the player's stats
   libtcod.console_set_default_foreground(con, libtcod.white)
   libtcod.console_print_ex(0, 1, SCREEN_HEIGHT - 2, libtcod.BKGND_NONE, libtcod.LEFT,
                 'HP: ' + str(player.model.hp) + '/' + str(player.model.max_hp))

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
      print "YOU DIED!"
      game_state = 'dead'

