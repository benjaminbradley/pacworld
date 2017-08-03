import sys
import random
import pygame
from pygame import *
import logging
import math

sys.path.append('art')
from DrawSpiral import DrawSpiral

import pacdefs
import world
import colors
import effect
from effect import *	# Effect, EFFECT_*
from swirl import Swirl


STYLE_DEFAULT = 0
STYLE_SPIRAL = 1
STYLES = [STYLE_DEFAULT, STYLE_SPIRAL]

BURST_FREQUENCY = 3000

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
		self.side_length = 60	#FIXME: get this number from somewhere more intelligent, maybe passed in, or calculated?
		self.width = 1#self.side_length
		self.height = 1#self.side_length
#		self.right = self.left + self.width
#		self.bottom = self.top + self.height
		self.type = pacdefs.TYPE_ART
		self.symbol = pacdefs.ART_SYMBOL
		self.doors = {}	# dictionary of side(int) to (X,Y) tuple of ints
		self.effects = {}	# dictionary of Effect.EFFECT_TYPE to Effect class
		self.angle = 0
		self.color = colors.PINK2
		#self.style = random.randint(0, len(STYLES))
		self.style = STYLE_SPIRAL	# testing
		self.jitter = pygame.time.get_ticks() + random.randint(0, BURST_FREQUENCY)
		#print "DEBUG: Art.__init__(): jitter={0}".format(self.jitter)
		
		if self.style == STYLE_SPIRAL:
			self.spiral_minRad = 3
			self.spiral_maxRad = self.spiral_curRad = int(float(self.side_length) / 2)
			self.spiral_curRot = math.pi
			self.spiral_startAngle = 0.0
			self.spiral_radStep = 2.0

		# make & capture the initial image for the art
		self.makeSprite()
		
		# calculated variables
		# x,y is the art piece's location on the map (left,top corner)
		xmargin = int((themap.grid_cellwidth - self.rect.width ) / 2)
		ymargin = int((themap.grid_cellheight - self.rect.height ) / 2)
		self.x = self.left * themap.grid_cellwidth + xmargin
		self.y = self.top * themap.grid_cellheight + ymargin
		#self.rect.top = (self.top - 0.5 )* self.map.grid_cellheight
		#self.rect.left = (self.left - 0.5) * self.map.grid_cellwidth
		self.rect.left = self.x
		self.rect.top = self.y
		
		# aspects particular to this type of art
		self.burstFrequency = BURST_FREQUENCY	# pull this from somewhere ?
		self.lastBurst = 0
		
		
	def makeSprite(self):
		# Create an image for the sprite
		self.image = Surface((self.side_length, self.side_length))
		self.image.fill(colors.BLACK)
		self.image.set_colorkey(colors.BLACK, RLEACCEL)	# set the background to transparent
		
		# draw the base sprite, in it's current state
		if self.style == STYLE_DEFAULT:
			radius = int(float(self.side_length) / 2)
			pygame.draw.circle(self.image, colors.BLACK, (radius,radius), radius+4)
			pygame.draw.circle(self.image, colors.WHITE, (radius,radius), radius+2)
			pygame.draw.circle(self.image, self.color, (radius,radius), radius, 2)
		elif self.style == STYLE_SPIRAL:
			#DrawSpiral(self.image, [radius,radius], radius = curRad, rotation = curRot, numSpokes = 5, clockwise = True, startAngle = startAngle)
			DrawSpiral(self.image, [self.spiral_maxRad,self.spiral_maxRad], self.spiral_curRad, self.spiral_curRot, 3, True, self.spiral_startAngle)

		
		
		for effect in self.effects.values():
			effect.draw(self.image)	# TODO: if it's the transfer effect, it should be drawn on the world map, right? where...
		
		# rotate image, if applicable
		if(self.angle != 0):
			self.image = pygame.transform.rotate(self.image, self.angle)

		# Create the sprites rectangle from the image, maintaining rect position if set
		oldrectpos = None
		if hasattr(self, 'rect'):
			oldrectpos = self.rect.center
		self.rect = self.image.get_rect()
		if oldrectpos:
			self.rect.center = oldrectpos

		# create a mask for the sprite (for collision detection)
		self.mask = pygame.mask.from_surface(self.image)
	
	
	def startEffect(self, effect_type, effect_options):
		# initialize effect variables
		#logging.debug("starting new effect, type: {0}".format(effect_type))
		self.effects[effect_type] = Effect(effect_type, effect_options)
		self.makeSprite()
	
	def getSwirl(self):
		# return the type of swirl that this art gives
		#TODO: make this variable depending on art type - coordinate with effect type used in .update() below?
		return Swirl(effect.BURST_EFFECT)


	def update(self, t):
		remakeSprite = False
		# animate base sprite
		if self.style == STYLE_SPIRAL:
			self.spiral_curRad += self.spiral_radStep
			if self.spiral_curRad <= self.spiral_minRad or self.spiral_curRad >= self.spiral_maxRad: self.spiral_radStep = -self.spiral_radStep
			self.spiral_curRot += 0.1
			self.spiral_startAngle -= 0.05
			remakeSprite = True
			
		
		# check for periodic effects to start
		if self.lastBurst + self.burstFrequency < t and self.jitter < t:
			self.lastBurst = t
			#logging.debug ("Art.update(): triggering burst for art #{0} starting at {1}".format(self.id, t))
			windowRect = self.map.player.shape.getWindowRect()
			if self.onScreen(windowRect): soundvolume = 1.0
			elif self.nearScreen(windowRect): soundvolume = 0.3
			else: soundvolume = 0
			self.startEffect(effect.BURST_EFFECT, {EFFECT_VOLUME: soundvolume})
		
		# check for current effects to continue
		completed_effects = []
		for effect_type in self.effects.keys():
			if self.effects[effect_type].update(t):
				remakeSprite = True
			else:
				completed_effects.append(effect_type)
				remakeSprite = True
		# clean up completed effects
		for effect_type in completed_effects:
			del self.effects[effect_type]	# FIXME: is more explicit garbage collection needed here?
		
		if remakeSprite: self.makeSprite()
	
	def draw(self, display, windowRect):
		#TODO: adjust blit dest by mapTopLeft
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
	
	def getCenter(self):
		return self.rect.center
