import string

ITEM_KEYS = string.ascii_lowercase

ITEM_TYPE_OPTIONS = {
        "cast": [('u', "(U)se"), ('d', "(D)rop")],
        "melee": [('r', "Equip in (r)ight hand"), ('l', "Equip in (l)eft hand"), ('d', "(D)rop")],
        "armour": [('w', "(W)ear"), ('d', "(D)rop")]
        }

#actual size of the window
SCREEN_WIDTH = 80
SCREEN_HEIGHT = 40
PANEL_HEIGHT = 5
PANEL_Y = SCREEN_HEIGHT - PANEL_HEIGHT

BAR_WIDTH = 20
MSG_X = BAR_WIDTH + 2
MSG_WIDTH = SCREEN_WIDTH - MSG_X
MSG_HEIGHT = PANEL_HEIGHT - 1

LIMIT_FPS = 20  # 20 frames-per-second maximum

NUM_LEVELS = 3
MAP_WIDTH = 80
MAP_HEIGHT = 35
ROOM_MAX_SIZE = 20
ROOM_MIN_SIZE = 6
MAX_ROOMS = 20
FOV_ALGO = 0  # default FOV algorithm
FOV_LIGHT_WALLS = True
TORCH_RADIUS = 20
MAX_ROOM_MONSTERS = 3
MAX_ROOM_ITEMS = 4

INVENTORY_WIDTH = 50

#spell values
HEAL_AMOUNT = 4
LIGHTNING_DAMAGE = 20
LIGHTNING_RANGE = 5
CONFUSE_RANGE = 8
CONFUSE_NUM_TURNS = 10
FIREBALL_RADIUS = 3
FIREBALL_DAMAGE = 12

#weapon/armour values
STICK_DMG = 7
STICK_DEF = 0

CROWBAR_DMG = 12
CROWBAR_DEF = 2

WOODEN_SHIELD_DMG = 1
WOODEN_SHIELD_DEF = 4

CLOAK_DMG = 0
CLOAK_DEF = 3
