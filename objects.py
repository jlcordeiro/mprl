import random
import libtcodpy as libtcod
from messages import *
import controllers.objects

def move_towards_creature(one, other, method_check_blocks):
   (x1, y1) = one.position
   (x2, y2) = other.position

   #return the distance to another object
   distance = one.distance_to(other)
    
   #normalize it to length 1 (preserving direction), then round it and
   #convert to integer so the movement is restricted to the map grid
   dx = int(round((x2 - x1) / distance))
   dy = int(round((y2 - y1) / distance))

   if method_check_blocks((x1+dx,y1+dy)) == False:
      one.move(dx, dy)
 
def take_turn( monster, player, method_check_blocks ):
   if monster.died:
      return

   messages = MessagesBorg()
   if monster.confused_turns > 0:
      messages.add('The ' + monster.name + ' is confused!', libtcod.red)

      (xi, yi) = monster.position
      final_pos = ( xi+random.randint(-1, 1), yi+random.randint(-1, 1))

      if method_check_blocks( final_pos ) == False:
         monster.move(dx, dy)

      monster.confused_turns -= 1
      
      if monster.confused_turns == 0:
         messages.add('The ' + self.name + ' is no longer confused!', libtcod.red)

   else:
      #move towards player if far away
      if monster.distance_to(player) >= 2:
         move_towards_creature(monster,player,method_check_blocks)
      #close enough, attack! (if the player is still alive.)
      elif player.model.hp > 0:
         monster.attack(player)


