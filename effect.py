import pygame
import logging

from pacsounds import Pacsounds,getPacsound
import colors


BURST_EFFECT = 1	# solo sprite effect
TRANSFER_EFFECT = 2	# sprite to sprite effect


BURST_EFFECT_NUMFRAMES = 6
TRANSFER_EFFECT_NUMFRAMES = 14



class Effect():
	def __init__(self, type, option_value):
		self.type = type
		
		# initialize subsystems
		self.sound = getPacsound()
		
		fps = 10
		self.animate_delay = 1000 / fps
		self.animate_last_update = 0
		self.animate_frame = 0
		
		# initialize animation timer
		if self.type == BURST_EFFECT:
			if option_value == None:
				sound_volume = 1.0
			else:
				sound_volume = option_value
			self.animate_numframes = BURST_EFFECT_NUMFRAMES
			# play burst sound
			if self.sound != None and sound_volume > 0: self.sound.play('3roboditzfade', sound_volume)
		elif self.type == TRANSFER_EFFECT:
			if option_value == None:	## REQUIRED PARAMETER!
				logger.critical("can't call a TRANSFER effect with no target!")
				return False
			self.target = option_value
			self.animate_numframes = TRANSFER_EFFECT_NUMFRAMES
			logging.debug("initialized transfer effect")


	def draw(self, image):
		lineWidth = 2	# default, may be adjusted later
		if self.type == BURST_EFFECT:
			final_radius = image.get_width() / 2
			#print "DEBUG: Effect.draw(): frame={0}, numframe={1}, radius={2}".format(self.animate_frame, self.animate_numframes, final_radius)
			burst_radius = int(float(self.animate_frame) / float(self.animate_numframes) * final_radius)
			if burst_radius < lineWidth: lineWidth = burst_radius
			gradpercent = float(self.animate_frame) / float(self.animate_numframes)
			grad_color = [int(gradpercent*c) for c in colors.WHITE]
			#print "DEBUG: Effect.draw() in burstEffect: burst_radius = {0}, gradpercent = {1}, grad_color={2}".format(burst_radius, gradpercent, grad_color)
			pygame.draw.circle(image, grad_color, (final_radius,final_radius), burst_radius, lineWidth)
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
	
	def update(self, ticks):
		if ticks - self.animate_last_update > self.animate_delay:
			self.animate_frame += 1
			if self.animate_frame >= self.animate_numframes:
				return False	# end the effect, only go through it once
			self.animate_last_update = ticks
		return True
		
