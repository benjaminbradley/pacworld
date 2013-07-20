import pygame
#from pygame.locals import *
from pygame import *

import colors

WALL_LINE_WIDTH = 8

# The class for a blocking wall
class Wall(sprite.Sprite):

	def __init__(self, mapSize, point1, point2):
		# Initialize the sprite base class
		super(Wall, self).__init__()

		# Get the display size for working out collisions later
		self.mapSize = mapSize

		# Set our image to a new surface, the size of the screen rectangle
		self.image = Surface(mapSize)

		# Fill the image with a green colour (specified as R,G,B)
		self.image.fill(colors.BLACK)
		self.image.set_colorkey(colors.BLACK, RLEACCEL)	# set the background to transparent

		# Get width proportionate to display size
		print "DEBUG: Wall.__init__(): creating new wall from {0} to {1}".format(point1, point2)
		# draw the line on the surface
		self.rect = pygame.draw.line(self.image, colors.BLUE, point1, point2, WALL_LINE_WIDTH)
		#print "DEBUG: Wall.__init__(): wall rect is {0}".format(self.rect)
		# grab a bitmask for collision detection
		self.mask = pygame.mask.from_surface(self.image)
		#print "DEBUG: wall mask is {0}".format(self.mask)

	def draw(self, display):
		# Draw the background to the display that has been passed in
		display.blit(self.image, (0,0))
				
