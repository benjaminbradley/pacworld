import pygame
from pygame import *
import logging
import random

import effect
from effect import Effect
import colors

LOOK_CIRCLE = 1
LOOK_LINE = 2
LOOK_LT = 3
LOOKS = [LOOK_CIRCLE, LOOK_LINE, LOOK_LT]

class Swirl(sprite.Sprite):
	
	def __init__(self, effect_type):
		# Initialize the sprite base class
		super(Swirl, self).__init__()
		
		self.effect_type = effect_type
		self.look = LOOKS[random.randint(0,len(LOOKS)-1)]
	
	def activate(self, shape, dir_up):
		shape.effects[self.effect_type] = Effect(self.effect_type)
		if(self.look == LOOK_LINE):
			if(dir_up): shape.moreSides()
			else: shape.lessSides()
		elif(self.look == LOOK_CIRCLE):
			if(dir_up): shape.sizeUp()
			else: shape.sizeDown()
		elif(self.look == LOOK_LT):
			if(dir_up): shape.colorUp()
			else: shape.colorDn()
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
			elif self.look == LOOK_LT:
				# draw an angle
				length = 4
				start1_pos = (position[0] - length/2, position[1]-length)
				start2_pos = (position[0] - length/2, position[1]+length)
				end_pos = (position[0] + length/2, position[1])
				lineWidth = 2
				pygame.draw.line(image, color, start1_pos, end_pos, lineWidth)
				pygame.draw.line(image, color, start2_pos, end_pos, lineWidth)
				
		else:
			logger.critical("unknown effect type: {0}".format(self.type))

