import sys
import pygame
from pygame import *

import wall
from wall import Wall
import colors
import world

# The class for the background
class Map(sprite.Sprite):
	
	def __init__(self, mapSize, displaySize, theworld):
		# Initialize the sprite base class
		super(Map, self).__init__()
		
		# Set our image to a new surface, the size of the World Map
		self.displaySize = displaySize
		self.mapSize = mapSize
		#self.mapSize = list(displaySize)
		print "DEBUG: Map.__init__(): mapSize is {0}".format(self.mapSize)
		self.image = Surface(self.mapSize)
		
		# Fill the image with a green colour (specified as R,G,B)
		self.image.fill(colors.BLACK)
		
		self.walls = [] # List to hold the walls
		
		self.world = theworld
		
		#print "DEBUG: Map.__init__(): rendering world:\n{0}".format(theworld.to_s())
		self.grid_cellheight = grid_cellheight = mapSize[1] / theworld.rows
		self.grid_cellwidth = grid_cellwidth = mapSize[0] / theworld.cols
		print "DEBUG: Map.__init__(): cell size is {0} wide x {1} high".format(grid_cellwidth, grid_cellheight)
		

		# NEXT: render the world map from the 'world' class argument
		
		for worldObj in sorted(theworld.objects, key=lambda obj: world.RENDER_ORDER[obj.type]):
			print "DEBUG: rendering the next world object: {0}".format(worldObj)
			if worldObj.type == world.TYPE_PATH:
				left = worldObj.left * grid_cellwidth
				top = worldObj.top * grid_cellheight
				if worldObj.direction_h:
					right = (worldObj.left+worldObj.length) * grid_cellwidth
					bottom = (worldObj.top+worldObj.width) * grid_cellheight
				else:
					right = (worldObj.left+worldObj.width) * grid_cellwidth
					bottom = (worldObj.top+worldObj.length) * grid_cellheight
				topLt = (left, top)
				topRt = (right, top)
				bottomLt = (left, bottom)
				bottomRt = (right, bottom)
				# draw a line down each side of the path
				if worldObj.direction_h:
					print "DEBUG: path line1 from {0} to {1}".format(topLt, topRt)
					pygame.draw.line(self.image, colors.GREEN, topLt, topRt, wall.WALL_LINE_WIDTH)
					pygame.draw.line(self.image, colors.GREEN, bottomLt, bottomRt, wall.WALL_LINE_WIDTH)
				else:
					print "DEBUG: path line1 from {0} to {1}".format(topLt, bottomLt)
					pygame.draw.line(self.image, colors.GREEN, topLt, bottomLt, wall.WALL_LINE_WIDTH)
					pygame.draw.line(self.image, colors.GREEN, topRt, bottomRt, wall.WALL_LINE_WIDTH)
				# note, these are NOT blocking walls
				width = right - left
				height = bottom - top
				rect = (left, top, width, height)
				pygame.draw.rect(self.image, (111,111,111), rect)
				

			elif worldObj.type == world.TYPE_ART:
				# let the sprite manager draw it
				pass

			elif worldObj.type == world.TYPE_INTERSECTION:
				# draw a grey rectangle
				left = worldObj.left * grid_cellwidth
				top = worldObj.top * grid_cellheight
				width = worldObj.width * grid_cellwidth
				height = worldObj.height * grid_cellheight
				#right = (worldObj['left']+worldObj['width']) * grid_cellwidth
				#bottom = (worldObj['top']+worldObj['length']) * grid_cellheight
				#topLt = (left, top)
				#topRt = (right, top)
				#bottomLt = (left, bottom)
				#bottomRt = (right, bottom)
				rect = (left, top, width, height)
				print "DEBUG: intersection rect at {0}".format(rect)
				pygame.draw.rect(self.image, (222,222,222), rect)

			elif worldObj.type == world.TYPE_FIELD:
				# draw a brown rectangle
				left = worldObj.left * grid_cellwidth
				top = worldObj.top * grid_cellheight
				width = worldObj.width * grid_cellwidth
				height = worldObj.height * grid_cellheight
				rect = (left, top, width, height)
				#print "DEBUG: field rect at {0}".format(rect)
				pygame.draw.rect(self.image, (160,82,45), rect)

			elif worldObj.type == world.TYPE_ROOM:
				# calculate corners & dimensions
				left = worldObj.left * grid_cellwidth
				top = worldObj.top * grid_cellheight
				width = worldObj.width * grid_cellwidth
				height = worldObj.height * grid_cellheight
				right = left + width
				bottom = top + height
				print "DEBUG: Map... rendering ROOM {4} [vert={0}..{1}, horiz={2}..{3}]".format(top,bottom,left,right,worldObj.id)
				# define interior & paint it
				rect = (left, top, width, height)
				#print "DEBUG: room rect at {0}".format(rect)
				pygame.draw.rect(self.image, colors.PINK, rect)
				#DEBUG MODE: draw the objectId in the middle
				font = pygame.font.Font(None, 20)
				textBitmap = font.render(str(worldObj.id), True, colors.BLACK)
				self.image.blit(textBitmap, [left+(width/2), top+(height/2)])
			    
				# draw 4 walls
				roomWalls = {}	# dictionary of side to array of wallDefs (each wallDef is a tuple of 2 points, each one an (x,y) tuple)
				# draw walls that have doors in them
				#NOTE: assumes no more than one door per wall
				num_doors = len(worldObj.doors.keys())
				if num_doors > 1: print "DEBUG: Map...multiple doors! Room has {0} doors.".format(num_doors)
				for side,doorpos in worldObj.doors.items():
					#need to keep track of which sides have been processed, 
					#add the defaults later for walls with no doors
					doorx = doorpos[0]
					doory = doorpos[1]
					print "DEBUG: Map... rendering ROOM {0} has a door at {1} on side {2}".format(worldObj.id,doorpos,side)
					if side == world.SIDE_N:
						doorLeft = doorx * grid_cellwidth
						doorRight = (doorx+1) * grid_cellwidth
						# add 2 walls, on either side of the door
						roomWalls[side] = []
						roomWalls[side].append([(left,top), (doorLeft,top)])
						roomWalls[side].append([(doorRight,top), (right,top)])
				
					if side == world.SIDE_E:
						doorTop = doory * grid_cellheight
						doorBottom = (doory+1) * grid_cellheight
						print "DEBUG: Map... rendering ROOM door top/bottom is {0}/{1}".format(doorTop,doorBottom)
						# add 2 walls, on either side of the door
						roomWalls[side] = []
						roomWalls[side].append([(right,top), (right,doorTop)])
						roomWalls[side].append([(right,doorBottom), (right,bottom)])
				
					if side == world.SIDE_S:
						doorLeft = doorx * grid_cellwidth
						doorRight = (doorx+1) * grid_cellwidth
						# add 2 walls, on either side of the door
						roomWalls[side] = []
						roomWalls[side].append([(left,bottom), (doorLeft,bottom)])
						roomWalls[side].append([(doorRight,bottom), (right,bottom)])
				
					if side == world.SIDE_W:
						doorTop = doory * grid_cellheight
						doorBottom = (doory+1) * grid_cellheight
						# add 2 walls, on either side of the door
						roomWalls[side] = []
						roomWalls[side].append([(left,top), (left,doorTop)])
						roomWalls[side].append([(left,doorBottom), (left,bottom)])
				# end of for each door (creating walls w/ doors)
					
				# check all directions and add a default wall if none is defined
				for side in world.SIDES:
					if side not in roomWalls.keys() or len(roomWalls[side]) == 0:
						print "DEBUG: Map... drawing default wall for side {0}".format(side)
						roomWalls[side] = []
						if side == world.SIDE_N: roomWalls[side].append([(left,top), (right,top)])
						if side == world.SIDE_E: roomWalls[side].append([(right,top), (right, bottom)])
						if side == world.SIDE_S: roomWalls[side].append([(right,bottom), (left,bottom)])
						if side == world.SIDE_W: roomWalls[side].append([(left,bottom), (left,top)])

				for walls in roomWalls.values():
					for wallPoints in walls:
						# create the wall def
						newwall = Wall(self.mapSize, wallPoints[0], wallPoints[1])
						# add to walls array
						self.walls.append( newwall )
						# draw on image
						newwall.draw(self.image)
				
		print "DEBUG: Map.__init__(): rendered world:\n{0}".format(theworld.to_s())
		

		# draw a border, registering each line as a wall
		topLt = (0, 0)
		topRt = (self.mapSize[0], 0)
		botLt = (0, self.mapSize[1])
		botRt = (self.mapSize[0], self.mapSize[1])
		wallDefs = [
			(topLt, topRt),
			(topRt, botRt),
			(botRt, botLt),
			(botLt, topLt)
		]
		for wallPoints in wallDefs:
			newwall = Wall(self.mapSize, wallPoints[0], wallPoints[1])	# create the wall def
			self.walls.append( newwall )	# add to walls array
			newwall.draw(self.image)	# draw on image

		
		# Create the sprite rectangle from the image
		self.rect = self.image.get_rect()
		
	
	def getWindowRect(self, center):
		"""get the rect for the display window containing the center point"""
		windowLeft = center[0] - self.displaySize[0]/2
		if windowLeft+self.displaySize[0] >= self.mapSize[0]: windowLeft = self.mapSize[0]-self.displaySize[0]-1
		if windowLeft < 0: windowLeft = 0
		windowTop = center[1] - self.displaySize[1]/2
		if windowTop+self.displaySize[1] >= self.mapSize[1]: windowTop = self.mapSize[1]-self.displaySize[1]-1
		if windowTop < 0: windowTop = 0
		return Rect(windowLeft, windowTop, self.displaySize[0], self.displaySize[1])
	
	def draw(self, display, center):
		# Draw a subsurface of the world map
		# with dimensions of the displaySize
		# centered on the position defined as center (within limits)
		# to the display that has been passed in
		
		#print "DEBUG: Map.draw(): map size is {0}".format(self.image.get_size())
		#print "DEBUG: Map.draw(): center for drawwindow is at {0}, resulting in a {1}x{2} window with topleft at {3},{4}".format(center, self.displaySize[0], self.displaySize[1], windowLeft, windowTop)
		screenImage = self.image.subsurface( self.getWindowRect(center) )
		display.blit(screenImage, (0,0))


	def wallCollision(self, target):
		for wall in self.walls:
			a = wall
			b = target
			#We calculate the offset of the second mask relative to the first mask.
			offset_x = b.mapCenter[0]
			offset_y = b.mapCenter[1]
			# See if the two masks at the offset are overlapping.
			if a.mask.overlap(b.mask, (offset_x, offset_y)):
				#print "DEBUG: Map.wallCollision(): collision detected with wall {0}!".format(wall.rect)
				#print "DEBUG: Map.wallCollision(): target top/bottom, left/right is: {0}, {1}; {2}, {3}".format(target.rect.top, target.rect.bottom, target.rect.left, target.rect.right)
				#print "DEBUG: Map.wallCollision(): wall top/bottom, left/right is: {0}, {1}; {2}, {3}".format(wall.rect.top, wall.rect.bottom, wall.rect.left, wall.rect.right)
				#print "DEBUG: Map.wallCollision(): offset x,y is: {0}, {1}".format(offset_x, offset_y)
				return True
		return False



if __name__ == '__main__':
	# Make the display size a member of the class
	displaySize = (640, 480)
	
	# Initialize pygame
	pygame.init()

	# Set the window title
	display.set_caption("Map Test")
	
	# Create the window
	window = display.set_mode(displaySize)
		
	# Create the background, passing through the display size
	mapSize = [4*x for x in displaySize]
	map = Map(mapSize, displaySize)

	# Draw the background
	map.draw(window, (10,10))
	display.update()

	done = False
	while not done:
		for event in pygame.event.get():
			if event.type == QUIT:
				pygame.quit()
				sys.exit()
			if event.type == KEYDOWN and event.key == K_DOWN:
				pygame.quit()
				sys.exit()



#EOF