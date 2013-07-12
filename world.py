import random
import copy

# map symbols
HPATH_SYMBOL = '='
VPATH_SYMBOL = '|'
SYMBOL_CLEAR = '.'

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

		# step 1: generate pathways
		
		#	goal is to have between 2s+o and s+2o total length of pathways
		a = int(shortside + 2*longside)
		b = int(2*shortside + longside)
		minTotalPaths = min(a,b)
		maxTotalPaths = max(a,b)
		curTotalPaths = 0
		
		numPaths_longWays = 0
		numPaths_shortWays = 0
		
		while(curTotalPaths < minTotalPaths):
			print "DEBUG: World.__init__(): current total paths ({0}) not in range {1}..{2}".format(curTotalPaths, minTotalPaths, maxTotalPaths)
			
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
			#	minimum length o/2 (where o is the longest of h or w)
			#	maximum length s (where s is the shortest of h or w)
			#minPath = int(shortside)
			#maxPath = int(longside)
			#path_len = 0
			#while(path_len < minPath or maxPath < path_len):
			#	path_len = get_random_value('small')
			
			path_len = get_random_value(['medium','large'])
			print "DEBUG: World.__init__(): pathway size is {0} long by {1} wide".format(path_len, path_width)
			
			
			# placement
			if(pathDir_h):	# horizontal placement
				top = random.randint(0, self.rows-path_width)
				left = random.randint(0, self.cols-path_len)
			else:	# vertical placement
				top = random.randint(0, self.rows-path_len)
				left = random.randint(0, self.cols-path_width)

			newPath = {
				'type' : 'path',
				'top' : top,
				'left' : left,
				'direction_h' : pathDir_h,
				'width' : path_width,
				'length' : path_len
			}
			#print "DEBUG: World.__init__(): new path placed at {0},{1}".format(left,top)
			print "DEBUG: World.__init__(): new path: {0}".format(newPath)

			# check for obustructions, correct if possible
			if(self.addObject(newPath)):
				# place if successful
				self.objects.append(newPath)
				curTotalPaths += newPath['length']


			# DEBUG: show current map
			print "DEBUG: World.__init__(): world grid is:\n{0}".format(self.to_s())
			
			#if(len(self.objects) > 5): exit()

		# step 2. generate fields
		#	if two or more pathways could be connected with a field, do it


		# step 3. populate rooms around fields and pathways
		#	- each door must lead to either a field, a pathway, or another room

		# step 4. place rocks
		#	- 4 or 5 randomly around the map? maybe skip this step? or it's used to identify inaccessible enclosed spaces?
	
	
	def addObject(self, newObject):
		# copy current grid
		newGrid = copy.deepcopy(self.grid)
		
		if(newObject['type'] == 'path'):
			x = newObject['left']
			y = newObject['top']
			if(newObject['length'] <= 0):
				print "ERROR: path length must be greater than 0!"
				exit()
			#print "DEBUG: adding path, ranging i to {0}...".format(newObject['length'])
			for i in range(newObject['length']):
				#print "DEBUG: ranging j to {0}...".format(newObject['width'])
				for j in range(newObject['width']):
					if newObject['direction_h']:
						posx = x + i
						posy = y + j
						path_symbol = HPATH_SYMBOL
					else:
						posx = x + j
						posy = y + i
						path_symbol = VPATH_SYMBOL
					# check for obstructions
					if self.grid[posy][posx] != SYMBOL_CLEAR:
						print "WARN: path obstructed at {0},{1}".format(posx,posy)
						#TODO
						#	ok for large pathways to intersect in the middle, medium pathways should only touch at corners at their ends
						return False
					else:
						# no obstructions, continue:
						print "DEBUG: added new symbol at {0},{1}".format(posx,posy)
						newGrid[posy][posx] = path_symbol
		else:
			print "PROGRAM ERROR: Unknown type {0}".format(newObject['type'])
			exit()
		
		# if everything works out ok, save the new grid
		self.grid = newGrid
		#print "DEBUG: object added, new grid is: \n{0}".format(self.to_s())
		return True	# success

	def to_s(self):
		"""converts world grid to a string for display to console"""
		gridstr = ''
		for row in self.grid:
			rowstr = ''.join(row)
			gridstr += rowstr+"\n"
		return gridstr



if __name__ == '__main__':
	gridDisplaySize = (10, 20)
	#gridDisplaySize = (20, 40)
	
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
	print "final world map is:"
	print themap.to_s()



#EOF