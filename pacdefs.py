import logging

######### WORLD #########

# map symbols
HPATH_SYMBOL = '='
VPATH_SYMBOL = '|'
INTERSECTION_SYMBOL = '+'
FIELD_SYMBOL = '/'
ROOM_SYMBOL = 'O'
ART_SYMBOL = '&'
ROCK_SYMBOL = 'X'
PATH_SYMBOLS = [HPATH_SYMBOL, VPATH_SYMBOL]
SYMBOL_BACKGROUND = ' '
SYMBOL_CLEAR = None
LARGE_PATH_MIN = 8
INTERSECTION_MIN_OVERLAP=1
MAX_RANDOM_SEED = 65535

PATH_AREA_MIN = 20  # percent of total world map area
FIELD_AREA_MIN = 20  # ditto above
ROOM_AREA_MIN = 30  # ditto

TYPE_PATH = 'path'
TYPE_INTERSECTION = 'pathcross'
TYPE_FIELD = 'field'
TYPE_ROOM = 'room'
TYPE_ART = 'art'
TYPE_ROCK = 'rock'
TYPE_CHARACTER = 'char'  # NOTE: NOT in RENDER_ORDER, not rendered on world map
RENDER_ORDER = {
  TYPE_ROCK: 1,
  TYPE_FIELD : 2,
  TYPE_PATH : 1,
  TYPE_INTERSECTION : 3,
  TYPE_ROOM : 4,
  TYPE_ART : 5,
}
WORLD_OBJ_TYPES = RENDER_ORDER.keys()

SIDE_N = 0
SIDE_E = 1
SIDE_S = 2
SIDE_W = 3
SIDES = [SIDE_N, SIDE_E, SIDE_S, SIDE_W]

def opposite_side(side):
  # assumes an even number of sides
  opposite = (side + (len(SIDES)/2)) % len(SIDES)
  return opposite


# graphics
WALL_LINE_WIDTH = 8  # pixel width for drawing

MAX_SWIRL_SATURATION_PERCENT = 90 # when world reaches this swirl saturation, it is remade
MAX_WORLD_REGEN_TIME = 600 # max time that a world will go without being regenerated...

# sound
NEARBY_SOUND_PERCENT = 0.2
ONSCREEN_SOUND_PERCENT = 0.5


# art
STYLE_TREE = 0
STYLE_SPIRAL = 1
STYLE_MANDALA = 2
STYLES = [STYLE_TREE, STYLE_SPIRAL, STYLE_MANDALA]


# debug flags
DEBUG_SHAPE_SHOWID = False
DEBUG_ART_SHOWID = False
DEBUG_ROOM_SHOWID = False
DEBUG_NUMSWIRLS = False
DEBUG_FRAMESPEED = False
DEBUG_SHOWGRID = False
