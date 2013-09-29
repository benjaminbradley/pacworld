import logging

######### WORLD #########

# map symbols
HPATH_SYMBOL = '='
VPATH_SYMBOL = '|'
INTERSECTION_SYMBOL = '+'
FIELD_SYMBOL = '/'
ROOM_SYMBOL = 'O'
ART_SYMBOL = '&'
PATH_SYMBOLS = [HPATH_SYMBOL, VPATH_SYMBOL]
SYMBOL_BACKGROUND = ' '
SYMBOL_CLEAR = None
LARGE_PATH_MIN = 8
INTERSECTION_MIN_OVERLAP=1
MAX_RANDOM_SEED = 65535

PATH_AREA_MIN = 20	# percent of total world map area
FIELD_AREA_MIN = 20	# ditto above
ROOM_AREA_MIN = 30	# ditto

TYPE_PATH = 'path'
TYPE_INTERSECTION = 'pathcross'
TYPE_FIELD = 'field'
TYPE_ROOM = 'room'
TYPE_ART = 'art'
TYPE_CHARACTER = 'char'	# NOTE: NOT in RENDER_ORDER, not rendered on world map
RENDER_ORDER = {
	TYPE_PATH : 1,
	TYPE_INTERSECTION : 2,
	TYPE_FIELD : 3,
	TYPE_ROOM : 4,
	TYPE_ART : 5,
}
WORLD_OBJ_TYPES = RENDER_ORDER.keys()

SIDE_N = 0
SIDE_E = 1
SIDE_S = 2
SIDE_W = 3
SIDES = [SIDE_N, SIDE_E, SIDE_S, SIDE_W]

# graphics
WALL_LINE_WIDTH = 8	# pixel width for drawing


def opposite_side(side):
	# assumes an even number of sides
	opposite = (side + (len(SIDES)/2)) % len(SIDES)
	#logging.debug("opposite side of {0} is {1}".format(side, opposite))
	return opposite
