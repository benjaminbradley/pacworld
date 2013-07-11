import sys
import pygame
from pygame import *

from wall import Wall
import colors

# The class for the background
class Map(sprite.Sprite):
	
	def __init__(self, displaySize):
		# Initialize the sprite base class
		super(Map, self).__init__()
		
		# Set our image to a new surface, the size of the World Map
		self.displaySize = displaySize
		#self.mapSize = [4*x for x in displaySize]
		self.mapSize = list(displaySize)
		print "DEBUG: Map.__init__(): mapSize is {0}".format(self.mapSize)
		self.image = Surface(self.mapSize)
		
		# Fill the image with a green colour (specified as R,G,B)
		self.image.fill(colors.BLACK)
		
		self.walls = [] # List to hold the walls
		
		# draw a border, registering each line as a wall
		topLt = (0, 0)
		topRt = (self.mapSize[0], 0)
		botLt = (0, self.mapSize[1])
		botRt = (self.mapSize[0], self.mapSize[1])
		wallDefs = (
			(topLt, topRt),
			(topRt, botRt),
			(botRt, botLt),
			(botLt, topLt),
			( (displaySize[0], displaySize[1]/2), (displaySize[0], displaySize[1]) ),
			( (displaySize[0]*2, 0), (displaySize[0]*2, displaySize[1]/2) ),
			( (displaySize[0]/2, displaySize[1]), (displaySize[0]*2, displaySize[1]) ),
			( (displaySize[0]*2, displaySize[1]/2), (displaySize[0]*2, displaySize[1]) ),
			( (displaySize[0], displaySize[1]*2), (displaySize[0], displaySize[1]*2) ),
			)
		for wallPoints in wallDefs:
			# create the wall def
			wall = Wall(self.mapSize, wallPoints[0], wallPoints[1])
			# add to walls array
			self.walls.append( wall )
			# draw on image
			wall.draw(self.image)
		
		# Create the sprite rectangle from the image
		self.rect = self.image.get_rect()
		
		
	def draw(self, display, center):
		# Draw a subsurface of the world map
		# with dimensions of the displaySize
		# centered on the position defined as center (within limits)
		# to the display that has been passed in
		windowLeft = center[0] - self.displaySize[0]/2
		if windowLeft < 0: windowLeft = 0
		if windowLeft+self.displaySize[0] >= self.mapSize[0]: windowLeft = self.mapSize[0]-self.displaySize[0]-1
		windowTop = center[1] - self.displaySize[1]/2
		if windowTop < 0: windowTop = 0
		if windowTop+self.displaySize[1] >= self.mapSize[1]: windowTop = self.mapSize[1]-self.displaySize[1]-1
		
		#print "DEBUG: Map.draw(): map size is {0}".format(self.image.get_size())
		#print "DEBUG: Map.draw(): center for drawwindow is at {0}, resulting in screenWindow dimensions {1}".format(center, screenWindow)
		screenImage = self.image.subsurface( windowLeft, windowTop, self.displaySize[0], self.displaySize[1] )
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
				print "DEBUG: Map.wallCollision(): collision detected with wall {0}!".format(wall)
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
	map = Map(displaySize)

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