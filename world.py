import random
import copy

# map symbols
HPATH_SYMBOL = '='
VPATH_SYMBOL = '|'
INTERSECTION_SYMBOL = '+'
FIELD_SYMBOL = '/'
ROOM_SYMBOL = 'O'
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
RENDER_ORDER = {
	TYPE_PATH : 1,
	TYPE_INTERSECTION : 2,
	TYPE_FIELD : 3,
	TYPE_ROOM : 4,
}

SIDE_N = 0
SIDE_E = 1
SIDE_S = 2
SIDE_W = 3
SIDES = [SIDE_N, SIDE_E, SIDE_S, SIDE_W]

# helper functions
def get_random_value(sizes):
	#picking a size:
	#inputs: size ranges
	#	- gather all weighted values within size ranges
	#	- pick a random value based on all of the weights

	weights = []
	values = []
	
	if 'small' in sizes:
		# "small" size, sidelength distribution:
		#20% 1d
		weights.append(20)
		values.append(1)
		#50% 2d
		weights.append(50)
		values.append(2)
		#30% 3d
		weights.append(30)
		values.append(3)
	
	if 'medium' in sizes:	#"medium" size sidelength distribution:
		#4d	50%
		weights.append(50)
		values.append(4)
		#5d	50%
		weights.append(50)
		values.append(5)

	if 'large' in sizes:	#"large" size sidelength distribution:
		#6d	30%
		weights.append(30)
		values.append(6)
		#7d	40% 
		weights.append(40)
		values.append(7)
		#8d	30%
		weights.append(30)
		values.append(8)

	# add total of all weights
	total_weights = sum(weights)	# reduce(lambda x, y: x + y, weights)
	weighted_result = random.randint(0, total_weights)
	
	result_index = None
	used_weights = 0
	for i in range(len(values)):
		#print "DEBUG: i={0}, in range({1})".format(i, len(values))
		if (used_weights <= weighted_result and weighted_result <= used_weights + weights[i]):
			result_index = i
			break
		used_weights += weights[i]
	
	if result_index == None:
		print "ERROR: no results! total_weights = {0}, used_weights={1}, weighted_result={2}".format(total_weights, used_weights, weighted_result)
		return 0
		
	#print "DEBUG: get_random_value(): result_index={0}, values array={1}".format(result_index, values)
	
	#print "DEBUG: result_index={0}, in range({1})".format(result_index, len(values))
	# pick a result from the available weights
	#print "DEBUG: get_random_value(): returning {0}".format(values[result_index])
	return values[result_index]
# END OF get_random_value()

def makeIntersectionObject(path1, path2, position):
	#FIXME: assumes that exactly one path is vertical and one path is horizontal
	if path1['direction_h']:
		hpath = path1
		vpath = path2
	else:
		hpath = path2
		vpath = path1
	newObject = {
		'type' : TYPE_INTERSECTION,
		'top' : position[1],
		'left' : position[0],
		'symbol' : INTERSECTION_SYMBOL,
		'hpath' : hpath,
		'vpath' : vpath,
	}
	return newObject


def getsymbol(obj, pos):
	#print "DEBUG: getsymbol({0}, {1})".format(obj, pos)
	if obj['type'] == TYPE_ROOM:
		if 'doors' in obj.keys() and pos in obj['doors'].values():
			return 'D'
		elif pos[1] == obj['top']:
			if pos[0] == obj['left']:
				return 'r'
			elif pos[0] == obj['left'] + obj['width'] - 1:	# right
				return '7'
			else:
				return '-'
		elif pos[1] == obj['top'] + obj['height'] - 1:	# bottom
			if pos[0] == obj['left']:
				return 'L'
			elif pos[0] == obj['left'] + obj['width'] - 1:	# right
				return 'j'
			else:
				return '-'
		elif pos[0] == obj['left']:
			return 'b'
		elif pos[0] == obj['left'] + obj['width'] - 1:	# right
			return 'd'
		return '_'
	else:
		return obj['symbol']


# The class to create a symbolic 'world', will be translated into a map
class World():
	
	def __init__(self, gridDisplaySize):
		# input: gridDisplaySize - the world is created as a 2-dimensional grid according with HxW as passed in
		# variables:
		#	grid - a grid of strings, each string identifying the contents of each grid square
		# output:
		#	objects - an array of the objects existing in the world map, with their characteristics
		# 
		
		# initialize world attributes
		(self.rows, self.cols) = gridDisplaySize
		self.totalArea = self.rows * self.cols
		# initialize data storage variables
		self.grid = [[SYMBOL_CLEAR for x in xrange(self.cols)] for x in xrange(self.rows)]
		
		# calculate intermediary vars
		shortside = min(self.rows, self.cols)
		longside = max(self.rows, self.cols)
		longdir_is_h = (shortside == self.rows)	# true = horizontal
		
				
		###################################################
		# generate a new world according to the algorithm
		###################################################
		
		self.objects = [] # List to hold the objects generated in the world (pathways, fields, etc)
		self.objectId_autoIncrement = 0
		
		# test intersection code
		#print self.addObject({
		#	'type' : TYPE_PATH,
		#	'top' : 1,
		#	'left' : 10,
		#	'direction_h' : False,
		#	'width' : 1,
		#	'length' : 15
		#})
		#print self.addObject({
		#	'type' : TYPE_PATH,
		#	'top' : 5,
		#	'left' : 1,
		#	'direction_h' : True,
		#	'width' : 1,
		#	'length' : 15
		#})
		#print "DEBUG: World.__init__(): world grid is:\n{0}".format(self.to_s())
		#exit()

		# step 1: generate pathways
		
		#	goal is to have between 2s+o and s+2o total length of pathways
		a = int(shortside + 2*longside)
		b = int(2*shortside + longside)
		minTotalPaths = min(a,b)
		maxTotalPaths = max(a,b)
		#curTotalPaths = 0
		#TODO: cleanup vars above
		curTotalPathArea = 0
		minPathArea = int(self.totalArea*PATH_AREA_MIN/100)
		numPaths_longWays = 0
		numPaths_shortWays = 0


		#while(curTotalPaths < minTotalPaths):
		#	print "DEBUG: World.__init__(): current total paths ({0}) not in range {1}..{2}".format(curTotalPaths, minTotalPaths, maxTotalPaths)
		while(curTotalPathArea < minPathArea):
			print "DEBUG: World.__init__(): current total path area ({0}, {1}%) hasn't met minimum path area ({2}, {3}%)".format(curTotalPathArea, int(100*curTotalPathArea/self.totalArea), int(self.totalArea*PATH_AREA_MIN/100), PATH_AREA_MIN)
			
			# create a new path & add to the world
			
			# generate random pathway
			
			# path direction:
			pathDir_h = (random.randint(0,1) == 1)	# random dir is binary, T=horizontal
			#		a maximum of 2 (or 3 with a separation clause?) pathways may be parallel to s
			if numPaths_shortWays >= 2 and (pathDir_h != longdir_is_h):
				#		the others must be parallel to o
				print "DEBUG: World.__init__(): too many shortWays ({0}) paths, forcing longways".format(numPaths_shortWays)
				pathDir_h = longdir_is_h
						
			if(pathDir_h): pathName='horizontal'
			else: pathName='vertical'
			print "DEBUG: World.__init__(): pathway direction will be {0}".format(pathName)
			
			# path Width
			path_width = get_random_value('small')
			
			# path length
			#minPath = int(shortside)	#	minimum length o/2 (where o is the longest of h or w)
			minPath = 4
			#	maximum length s (where s is the shortest of h or w)
			maxPath = int(longside)
			path_len = random.randint(minPath,maxPath)
			#while(path_len < minPath or maxPath < path_len):
			#	path_len = get_random_value('small')
			#path_len = get_random_value(['medium','large'])
			print "DEBUG: World.__init__(): pathway size is {0} long by {1} wide".format(path_len, path_width)
			
			
			# placement
			if(pathDir_h):	# horizontal placement
				top = random.randint(0, self.rows-path_width)
				if path_len > self.cols: path_len = self.cols
				if self.cols == path_len: left = 0
				else: left = random.randint(0, self.cols-path_len)
			else:	# vertical placement
				if path_len > self.rows: path_len = self.rows
				if self.rows == path_len: top = 0
				else: top = random.randint(0, self.rows-path_len)
				left = random.randint(0, self.cols-path_width)

			newPath = {
				'type' : TYPE_PATH,
				'top' : top,
				'left' : left,
				'direction_h' : pathDir_h,
				'width' : path_width,
				'length' : path_len
			}
			#print "DEBUG: World.__init__(): new path placed at {0},{1}".format(left,top)
			#print "DEBUG: World.__init__(): new path: {0}".format(newPath)

			# check for obustructions, correct if possible
			if(self.addObject(newPath)):
				# place if successful
				self.objects.append(newPath)
				#curTotalPaths += newPath['length']
				curTotalPathArea += newPath['length'] * newPath['width']
				if pathDir_h == longdir_is_h:
					numPaths_longWays += 1
				else:
					numPaths_shortWays += 1
				#print "DEBUG: World.__init__(): {0} shortWays paths, {1} longways paths".format(numPaths_shortWays, numPaths_longWays)


			# DEBUG: show current map
			#print "DEBUG: World.__init__(): world grid is:\n{0}".format(self.to_s())
			
			#if(len(self.objects) > 5): exit()

		# step 2. generate fields
		# basic implementation: randomly place fields
		curTotalFieldArea = 0
		minFieldArea = int(self.totalArea*FIELD_AREA_MIN/100)

		while(curTotalFieldArea < minFieldArea):
			#print "DEBUG: World.__init__(): current total field area ({0}, {1}%) hasn't met minimum ({2}, {3}%)".format(curTotalFieldArea, int(100*curTotalFieldArea/self.totalArea), int(self.totalArea*FIELD_AREA_MIN/100), PATH_AREA_MIN)
			
			# create a new field & add to the world
			
			# generate random field
			
			# field Size
			field_sidelength = get_random_value(['medium', 'large'])
			# it will be square
			
			#print "DEBUG: World.__init__(): field size is {0} square".format(field_sidelength)
			
			# placement
			if field_sidelength >= self.rows or field_sidelength >= self.cols: field_sidelength = min(self.rows, self.cols) -1	# just in case
			#else: 
			top = random.randint(0, self.rows-field_sidelength)
			left = random.randint(0, self.cols-field_sidelength)

			newField = {
				'type' : TYPE_FIELD,
				'top' : top,
				'left' : left,
				'width' : field_sidelength,
				'height' : field_sidelength,
				'symbol' : FIELD_SYMBOL
			}
			#print "DEBUG: World.__init__(): new path placed at {0},{1}".format(left,top)
			#print "DEBUG: World.__init__(): new path: {0}".format(newPath)

			# check for obustructions, correct if possible
			if(self.addObject(newField)):
				# place if successful
				self.objects.append(newField)
				#curTotalPaths += newPath['length']
				curTotalFieldArea += newField['width'] * newField['height']
				#print "DEBUG: World.__init__(): {0} shortWays paths, {1} longways paths".format(numPaths_shortWays, numPaths_longWays)

			# DEBUG: show current map
			#print "DEBUG: World.__init__(): world grid is:\n{0}".format(self.to_s())
		
		#TODO:
		#	if two or more pathways could be connected with a field, do it
		

		# step 3. populate rooms around fields and pathways
		#	- each door must lead to either a field, a pathway, or another room
		curTotalRoomArea = 0
		minRoomArea = int(self.totalArea*ROOM_AREA_MIN/100)
		
		while(curTotalRoomArea < minRoomArea):
			print "DEBUG: World.__init__(): current total room area ({0}, {1}%) hasn't met minimum room area ({2}, {3}%)".format(curTotalRoomArea, int(100*curTotalRoomArea/self.totalArea), int(self.totalArea*ROOM_AREA_MIN/100), ROOM_AREA_MIN)
			
			# create a new room & add to the world
			
			# generate random room
			
			# room dimensions
			room_width = get_random_value(['small', 'medium'])
			room_height = get_random_value(['small', 'medium'])
			
			print "DEBUG: World.__init__(): room size is {0} high by {1} wide".format(room_height, room_width)
			
			# placement
			if room_width > self.rows: room_width = self.rows
			if self.rows == room_height: top = 0
			else: top = random.randint(0, self.rows-room_height)
			left = random.randint(0, self.cols-room_width)

			newRoom = {
				'type' : TYPE_ROOM,
				'top' : top,
				'left' : left,
				'width' : room_width,
				'height' : room_height,
				'symbol' : ROOM_SYMBOL,
				'doors' : {},	# dictionary of side(int) to (X,Y) tuple of ints
			}
			#print "DEBUG: World.__init__(): new room placed at {0},{1}".format(left,top)
			#print "DEBUG: World.__init__(): new room: {0}".format(newRoom)
			
			room_area = newRoom['height'] * newRoom['width']
			# check for obustructions
			if(self.addObject(newRoom)):
				# place if successful
				self.objects.append(newRoom)
				curTotalRoomArea += room_area
			
			# determine orientation (place door(s))
			
			# a door is a square on the outside edge of the room which has adjacent a path or field (or intersection)
			door_placed = False
			roomLeft = newRoom['left']
			roomRight = newRoom['left']+newRoom['width']-1
			roomTop = newRoom['top']
			roomBottom = newRoom['top']+newRoom['height']-1
			print "DEBUG: World.__init(): room:top={0}, bottom={1}, left={2}, right={3}".format(roomTop, roomBottom, roomLeft, roomRight)
			squares_checked = {}	# hash of X,Y coordinates to boolean, dictionary
			while not door_placed:
				# pick a side to pick a random square from
				# side: 0 = North, 1 = East, South, West
				if newRoom['width'] == 1:
					if random.randint(0,1) == 0:	side = 1
					else: side = 3
					total_edge_squares = newRoom['height']
				elif newRoom['height'] == 1:
					if random.randint(0,1) == 0:	side = 0
					else: side = 2
					total_edge_squares = newRoom['width']
				else:
					side = random.randint(0,3)
					total_edge_squares = newRoom['width'] * 2 + newRoom['height'] * 2 - 4
					print "DEBUG: World.__init(): total_edge_squares={0}".format(total_edge_squares)
				# choose a random square on that side
				if side == 0:
					doorx = random.randint(roomLeft, roomRight)
					doory = roomTop
				elif side == 1:
					doorx = roomRight
					doory = random.randint(roomTop, roomBottom)
				elif side == 2:
					doorx = random.randint(roomLeft, roomRight)
					doory = roomBottom
				elif side == 3:
					doorx = roomLeft
					doory = random.randint(roomTop, roomBottom)
				#TODO: prefer not to place doors on a corner
				#print "DEBUG: World.__init(): room:trying door at {0},{1}".format(doorx, doory)
				
				# only check each square once
				index = str(doorx)+'x'+str(doory)
				if index in squares_checked.keys():
					#print "DEBUG: already checked square {0}".format(index)
					continue
				else:
					squares_checked[index] = True	# mark this square as checked
					if(len(squares_checked.keys()) == total_edge_squares):
						print "DEBUG: checked all possible room squares, none qualify... will need to place randomly."
						# if a door is not placed by any other means, do so now by random selection:
						#TODO
						newRoom['doors'][0] = (roomLeft, roomTop)
						door_placed = True
				
				# it should not be against the edge of the map
				if doorx == 0 or doorx == self.cols-1 or doory == 0 or doory == self.rows-1:
					#print "DEBUG: door placed against map edge, aborting"
					continue
				
				# VALIATION RULE: the door must be adjacent to a pathway or field
				# get the adjacent square type
				if side == 0:
					adj_doorx = doorx
					adj_doory = roomTop-1
				elif side == 1:
					adj_doorx = roomRight+1
					adj_doory = doory
				elif side == 2:
					adj_doorx = doorx
					adj_doory = roomBottom+1
				elif side == 3:
					adj_doorx = roomLeft-1
					adj_doory = doory

				adjacent_square = self.grid[adj_doory][adj_doorx]
				
				if adjacent_square == None:
					#print "DEBUG: adjacent square is undefined, disallowing door"
					continue
				if adjacent_square['type'] not in [TYPE_PATH, TYPE_FIELD, TYPE_INTERSECTION, TYPE_ROOM]:
					# not a qualifying adjacentcy type
					#print "DEBUG: adjacent square is not allowed ({0})",format(adjacent_square['type'])
					continue
				
				if adjacent_square['type'] == TYPE_ROOM:
					# if a door is placed next to another room, that room will automatically get a door as well in the adjacent square
					adj_doorside = (side + 2) % 4
					adjacent_square['doors'][adj_doorside] = (adj_doorx, adj_doory)

				#TODO: chance for a room to have 2 doors
				
				# update the grid with the door location
				newRoom['doors'][side] = (doorx, doory)
				door_placed = True

			# DEBUG: show current map
			#print "DEBUG: World.__init__(): world grid is:\n{0}".format(self.to_s())
		
		

		# step 4. place rocks
		#	- 4 or 5 randomly around the map? maybe skip this step? or it's used to identify inaccessible enclosed spaces?
	
	
	def addObject(self, newObject):
		# copy current grid
		newGrid = copy.deepcopy(self.grid)
		
		if(newObject['type'] == TYPE_FIELD):
			basex = newObject['left']
			basey = newObject['top']
			if(newObject['width'] <= 0):
				print "ERROR: field width must be greater than 0!"
				exit()
			for w in range(newObject['width']):
				posx = basex + w
				for h in range(newObject['height']):
					posy = basey + h
				
					# check for obstructions
					if self.grid[posy][posx] != SYMBOL_CLEAR:
						#print "WARN: field obstructed at {0},{1}".format(posx,posy)
						obstruction = self.grid[posy][posx]
						if obstruction['type'] in [TYPE_PATH, TYPE_INTERSECTION]:
							# field overwrites paths and intersections
							newGrid[posy][posx] = newObject
							continue
							
						# otherwise, obstruction kills the road
						return False
					else:
						# no obstructions, continue:
						
						#print "DEBUG: added new symbol at {0},{1}".format(posx,posy)
						newGrid[posy][posx] = newObject
			
			
		elif(newObject['type'] == TYPE_PATH):
			x = newObject['left']
			y = newObject['top']
			if(newObject['length'] <= 0):
				print "ERROR: path length must be greater than 0!"
				exit()
			#print "DEBUG: adding path, ranging i to {0}...".format(newObject['length'])
			adjacent_paths = {}	# dictionary of object IDs (for easy uniquifying)
			intersected_paths = {} # dictionary of object IDs (for easy uniquifying)
			for i in range(newObject['length']):
				# check for adjacencies
				if newObject['direction_h']:
					adjx = x + i
					adjy1 = y - 1
					adjy2 = y + newObject['width']
					if adjy1 >= 0 and self.grid[adjy1][adjx] != None and self.grid[adjy1][adjx]['type'] == TYPE_PATH:
						#print "WARN: adjacent path at {0},{1}".format(adjx,adjy1)
						adjacent_paths[self.grid[adjy1][adjx]['id']] = True
					elif adjy2 < self.rows and self.grid[adjy2][adjx] != None and self.grid[adjy2][adjx]['type'] == TYPE_PATH:
						#print "WARN: adjacent path at {0},{1}".format(adjx,adjy2)
						adjacent_paths[self.grid[adjy2][adjx]['id']] = True
				else:
					adjy = y + i
					adjx1 = x - 1
					adjx2 = x + newObject['width']
					if adjx1 >= 0 and self.grid[adjy][adjx1] != None and self.grid[adjy][adjx1]['type'] == TYPE_PATH:
						#print "WARN: adjacent path at {0},{1}".format(adjx1,adjy)
						adjacent_paths[self.grid[adjy][adjx1]['id']] = True
					elif adjx2 < self.cols and self.grid[adjy][adjx2] != None and self.grid[adjy][adjx2]['type'] == TYPE_PATH:
						#print "WARN: adjacent path at {0},{1}".format(adjx2,adjy)
						adjacent_paths[self.grid[adjy][adjx2]['id']] = True
				
				#print "DEBUG: ranging j to {0}...".format(newObject['width'])
				for j in range(newObject['width']):
					if newObject['direction_h']:
						posx = x + i
						posy = y + j
						newObject['symbol'] = HPATH_SYMBOL
					else:
						posx = x + j
						posy = y + i
						newObject['symbol'] = VPATH_SYMBOL
					# check for obstructions
					if self.grid[posy][posx] != SYMBOL_CLEAR:
						#print "WARN: path obstructed at {0},{1}".format(posx,posy)
						obstruction = self.grid[posy][posx]
						if obstruction['type'] == TYPE_INTERSECTION:
							#print "DEBUG: obstruction is an intersection, ignored at {0},{1}".format(posx,posy)
							# intersection is a freebie, unchanged, but does not block
							continue
						if obstruction['type'] in [TYPE_PATH]:
							#	ok for large pathways to intersect in the middle
							im_large =  (newObject['length'] >= LARGE_PATH_MIN)
							its_large = (obstruction['length'] >= LARGE_PATH_MIN)
							if im_large and its_large:
								#print "DEBUG: testing intersection of 2 large paths"
								# intersection should be at least INTERSECTION_MIN_OVERLAP=4 away from either end for both pathways
								# NOTE: intersection point should be adjusted by path width
								# check current path
								if i < INTERSECTION_MIN_OVERLAP: return False
								if i > newObject['length']-INTERSECTION_MIN_OVERLAP: return False
								# check other path
								if newObject['direction_h']:	# new path is horizontal, obstruction is vertical
									# check 'top' end first
									if posy < obstruction['top']+INTERSECTION_MIN_OVERLAP: return False
									# check bottom
									if posy > obstruction['top']+obstruction['length']-INTERSECTION_MIN_OVERLAP: return False
								else:	# new path NOT horizontal, so obstruction is horizontal
									# check left
									if posx < obstruction['left']+INTERSECTION_MIN_OVERLAP: return False
									# check right
									if posx > obstruction['left']+obstruction['length']-INTERSECTION_MIN_OVERLAP: return False
								
								# all qualifiers passed for large-large intersection, make it so!
								#print "DEBUG: intersection happening at {0},{1}".format(posx, posy)
								newGrid[posy][posx] = makeIntersectionObject(newObject, obstruction, (posx, posy))
								intersected_paths[obstruction['id']] = True
								continue
							
							
							# medium pathways should only touch at corners at their ends
							#TODO
							
						# otherwise, obstruction kills the road
						return False
					else:
						# no obstructions, continue:
						
						#print "DEBUG: added new symbol at {0},{1}".format(posx,posy)
						newGrid[posy][posx] = newObject
					

			# check cumulative obstructions
			if len(adjacent_paths) > 0 and len(adjacent_paths) != len(intersected_paths):
				print "DEBUG: more adjacent paths ({0}) than intersections ({1}), throwing out".format(len(adjacent_paths), len(intersected_paths))
				return False

		
		elif(newObject['type'] == TYPE_ROOM):
			basex = newObject['left']
			basey = newObject['top']
			if(newObject['width'] <= 0):
				print "ERROR: room width must be greater than 0!"
				exit()
			if(newObject['height'] <= 0):
				print "ERROR: room height must be greater than 0!"
				exit()
			for w in range(newObject['width']):
				posx = basex + w
				for h in range(newObject['height']):
					posy = basey + h
					
					# check for obstructions
					if self.grid[posy][posx] != SYMBOL_CLEAR:
						# all obstructions kill a room
						return False
						
					else:
						# no obstructions, continue:
						
						#print "DEBUG: added new symbol at {0},{1}".format(posx,posy)
						newGrid[posy][posx] = newObject
				# end for h in height
			# end for w in width
			
		else:
			print "PROGRAM ERROR: Unknown type {0}".format(newObject['type'])
			exit()
		
		# if everything works out ok, save the new grid
		self.grid = newGrid
		self.objectId_autoIncrement += 1
		newObject['id'] = self.objectId_autoIncrement
		print "DEBUG: '{0}' object added, new objId is: {1}".format(newObject['type'], newObject['id'])
		#print "DEBUG: object added, new grid is: \n{0}".format(self.to_s())
		return True	# success

	def to_s(self):
		"""converts world grid to a string for display to console"""
		gridstr = '_'
		for i in range(self.cols):	# add number ruler at top
			gridstr += str(i%10)
		gridstr += "\n"
		for i,row in enumerate(self.grid):
			disprow = [ SYMBOL_BACKGROUND if obj == SYMBOL_CLEAR else getsymbol(obj, (j, i)) for j,obj in enumerate(row) ]
			rowstr = ''.join(disprow)
			gridstr += str(i%10)+rowstr+str(i%10)+"\n"
		gridstr += "_"
		for i in range(self.cols):	# add number ruler at bottom
			gridstr += str(i%10)
		return gridstr



if __name__ == '__main__':
	# if no random seed was given, make one up:
	crazySeed = random.randint(0, MAX_RANDOM_SEED)
	random.seed(crazySeed)
	
	#gridDisplaySize = (10, 40)
	gridDisplaySize = (20, 40)
	#gridDisplaySize = (35, 100)
	
	'''
	print "random number tests..."
	for size in ['small', 'medium', 'large']:
		for time in range(10):
			print "a {0} random number is: {1}".format(size, get_random_value([size]))
	for time in range(5):
		print "a random number in small-med: {0}".format(get_random_value(['small', 'medium']))
	for time in range(5):
		print "a random number in med-large: {0}".format(get_random_value(['medium', 'large']))
	for time in range(10):
		print "a random number in small-large: {0}".format(get_random_value(['small', 'large']))
	exit()
	'''
	
	# Create the world, passing through the display size
	themap = World(gridDisplaySize)

	# show the final product
	print "USING RANDOM SEED: {0}",format(crazySeed)
	print "final world map is:"
	print themap.to_s()



#EOF