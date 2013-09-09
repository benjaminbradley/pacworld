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
				
		elif self.type == TRANSFER_EFFECT:
			final_radius = image.get_width()
			midpoint = self.animate_numframes / 2
			if self.animate_frame < midpoint:
				# first half of animation - getting bigger
				burst_radius = int(float(self.animate_frame) / float(midpoint) * final_radius)
			else:
				# second half of animation - getting smaller
				burst_radius = int(float(self.animate_numframes - self.animate_frame) / float(midpoint) * final_radius)
				#if burst_radius < 0: burst_radius = 0

			logging.debug("drawing transfer effect with burst_radius = {0}".format(burst_radius))
			if burst_radius < lineWidth: lineWidth = burst_radius
			gradpercent = float(self.animate_frame) / float(self.animate_numframes)
			grad_color = [int(gradpercent*c) for c in colors.PINK]

			#TODO: move it around!
			origin_x = image.get_width() / 2
			origin_y = image.get_height() / 2
			#target_x = self.target.rect.centerx
			#target_y = self.target.rect.centery
			#curx = origin_x + (gradpercent * (target_x - origin_x))
			#cury = origin_y + (gradpercent * (target_y - origin_y))
			pygame.draw.circle(image, grad_color, (origin_x,origin_y), burst_radius, 0)
		else:
			logger.critical("unknown effect type: {0}".format(self.type))

