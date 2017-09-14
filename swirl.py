import pygame
from pygame import *
import logging
import random

import effect
from effect import Effect
import colors

LOOK_CIRCLE = 1
LOOK_LINE = 2
LOOKS = [LOOK_CIRCLE, LOOK_LINE]

class Swirl(sprite.Sprite):
	
	def __init__(self, effect_type):
		# Initialize the sprite base class
		super(Swirl, self).__init__()
		
		self.effect_type = effect_type
		self.look = LOOKS[random.randint(0,len(LOOKS)-1)]
	
	def activate(self, shape):
		shape.effects[self.effect_type] = Effect(self.effect_type)
		shape.makeSprite()

	def draw(self, image, position, active = False):
		lineWidth = 1	# default, may be adjusted later
		if active:
			color = colors.PINK2
		else:
			color = colors.WHITE
		if self.effect_type == effect.BURST_EFFECT:
			if self.look == LOOK_CIRCLE:
				# draw a tiny circle
				radius = 3
				pygame.draw.circle(image, color, position, radius, lineWidth)
			elif self.look == LOOK_LINE:
				# draw a straight line
				length = 4
				start_pos = (position[0] - length/2, position[1])
				end_pos = (position[0] + length/2, position[1])
				lineWidth = 2
				pygame.draw.line(image, color, start_pos, end_pos, lineWidth)
				
		else:
			logger.critical("unknown effect type: {0}".format(self.type))

