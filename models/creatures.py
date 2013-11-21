from objects import ObjectModel

class Creature(ObjectModel):
   def __init__(self,x,y,hp,defense,power):
      super(Creature, self).__init__(x,y,True)
      self.max_hp = hp
      self.hp = hp
      self.defense = defense
      self.power = power

class Orc(Creature):
   def __init__(self,x,y):
      super(Orc, self).__init__(x,y,10,0,3)

class Troll(Creature):
   def __init__(self,x,y):
      super(Troll, self).__init__(x,y,16,1,4)

class Player(Creature):
   def __init__(self,x,y):
      super(Player, self).__init__(x,y,30,2,5)
      self.inventory = []
