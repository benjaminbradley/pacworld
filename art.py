import pygame
from pygame import *

import world
import colors
import effect
from effect import Effect

#example art: a fractal tree which grows and withers
#example art: a spiral which rotates
#example art: an animated mandala

class Art(sprite.Sprite):
	def __init__(self, themap, left, top):
		# Initialize the sprite base class
		super(Art, self).__init__()
		# initialize art variables
		self.map = themap
		self.top = top
		self.left = left
		self.side_length = 60	#FIXME: get this number from somewhere more intelligent, maybe passed in?
		self.width = 1#self.side_length
		self.height = 1#self.side_length
#		self.right = self.left + self.width
#		self.bottom = self.top + self.height
		self.type = 'art'#FIXME World.TYPE_ART
		self.symbol = '&'#FIXME World.ART_SYMBOL,
		self.doors = {}	# dictionary of side(int) to (X,Y) tuple of ints
		self.effects = {}	# dictionary of Effect.EFFECT_TYPE to Effect class
		self.angle = 0
		self.color = colors.PINK2

		# make & capture the initial image for the art
		self.makeSprite()
		
		# calculated variables
		# x,y is the art piece's location on the map (left,top corner)
		xmargin = (themap.grid_cellwidth - self.rect.width ) / 2
		ymargin = (themap.grid_cellheight - self.rect.height ) / 2
		self.x = self.left * themap.grid_cellwidth + xmargin
		self.y = self.top * themap.grid_cellheight + ymargin
		#self.rect.top = (self.top - 0.5 )* self.map.grid_cellheight
		#self.rect.left = (self.left - 0.5) * self.map.grid_cellwidth
		
		
	def makeSprite(self):
		# Create an image for the sprite
		self.image = Surface((self.side_length, self.side_length))
		self.image.fill(colors.BLACK)
		self.image.set_colorkey(colors.BLACK, RLEACCEL)	# set the background to transparent
		radius = int(float(self.side_length) / 2)
		pygame.draw.circle(self.image, colors.BLACK, (radius,radius), radius+4)
		pygame.draw.circle(self.image, colors.WHITE, (radius,radius), radius+2)
		pygame.draw.circle(self.image, self.color, (radius,radius), radius, 2)
		
		for effect in self.effects.values():
			effect.draw(self.image)
		
		# rotate image, if applicable
		if(self.angle != 0):
			self.image = pygame.transform.rotate(self.image, self.angle)

		# Create the sprites rectangle from the image
		self.rect = self.image.get_rect()		

		# create a mask for the sprite (for collision detection)
		self.mask = pygame.mask.from_surface(self.image)
	
	def startBurst(self):
		self.effects[effect.BURST_EFFECT] = Effect(effect.BURST_EFFECT)
		self.makeSprite()
	
	def update(self, t):
		if effect.BURST_EFFECT in self.effects.keys():
			if self.effects[effect.BURST_EFFECT].update(t):
				self.makeSprite()
			else:
				del self.effects[effect.BURST_EFFECT]	# FIXME: is more explicit garbage collection needed here?
				self.makeSprite()
	
	def draw(self, display, windowRect):
		#TODO: adjust blit dest by mapCenter
		screenpos = (self.x - windowRect[0], self.y - windowRect[1])
		#print "DEBUG: Art.draw(): drawing image at {0}".format(screenpos)
		display.blit(self.image, screenpos)
	# end of Art.draw()
	
	# todo: draw the art piece on the map
	# todo: animate it
	# idea: the "effects" are the abilities passed from the art piece to the shape.
	