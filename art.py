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
		
		# aspects particular to this type of art
		self.burstFrequency = 3000	# pull this from somewhere ?
		self.lastBurst = 0
		
		
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
		windowRect = self.map.getWindowRect(self.map.shape.mapCenter)
		if self.onScreen(windowRect): soundvolume = 1.0
		elif self.nearScreen(windowRect): soundvolume = 0.3
		else: soundvolume = 0
		self.effects[effect.BURST_EFFECT] = Effect(effect.BURST_EFFECT, soundvolume)
		self.makeSprite()
	
	def update(self, t):
		#print "DEBUG: Art.update({0})".format(t)
		# check for periodic effects to start
		if self.lastBurst + self.burstFrequency < t:
			self.lastBurst = t
			self.startBurst()
		
		# check for current effects to continue
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
	
	def onScreen(self, windowRect):
		windowRight = windowRect.left + windowRect.width
		windowBottom = windowRect.top + windowRect.height
		# if artpiece is on the screen, we will draw it
		artLeft = self.left * self.map.grid_cellwidth
		artRight = artLeft + self.width * self.map.grid_cellwidth
		artTop = self.top * self.map.grid_cellheight
		artBottom = artTop + self.height * self.map.grid_cellheight
		if artLeft > windowRight: return False
		if artRight < windowRect.left: return False
		if artBottom < windowRect.top: return False
		if artTop > windowBottom: return False
		return True	# art IS on the screen
		
	def nearScreen(self, windowRect):
		"""This function assumes that onScreen has already failed.
		This function checks to see if the art is on a screen adjacent to this one"""
		adjWindowLeft = windowRect.left - windowRect.width
		adjWindowRight = windowRect.left + windowRect.width * 2
		adjWindowTop = windowRect.top - windowRect.height
		adjWindowBottom = windowRect.top + windowRect.height * 2
		# if artpiece is within this extended window, return true
		artLeft = self.left * self.map.grid_cellwidth
		artRight = artLeft + self.width * self.map.grid_cellwidth
		artTop = self.top * self.map.grid_cellheight
		artBottom = artTop + self.height * self.map.grid_cellheight
		if artLeft < adjWindowLeft: return False
		if artTop < adjWindowTop: return False
		if artRight > adjWindowRight: return False
		if artBottom > adjWindowBottom: return False
		return True	# art IS near the screen
	

	# idea: the "effects" are the abilities passed from the art piece to the shape.
	