import pygame
import logging

from pacsounds import Pacsounds,getPacsound
import colors


BURST_EFFECT = 1	# solo sprite effect
TRANSFER_EFFECT = 2	# sprite to sprite effect

EFFECT_VOLUME = 1
EFFECT_TARGET = 2
EFFECT_SOURCE = 3

BURST_EFFECT_NUMFRAMES = 6
TRANSFER_EFFECT_NUMFRAMES = 14



class Effect():
	def __init__(self, type, option_dict = {}):
		self.type = type
		
		# initialize subsystems
		self.sound = getPacsound()
		
		fps = 10
		self.animate_delay = 1000 / fps
		self.animate_last_update = 0
		self.animate_frame = 0
		
		# initialize animation timer
		if self.type == BURST_EFFECT:
			if EFFECT_VOLUME not in option_dict.keys() or option_dict[EFFECT_VOLUME] == None:
				sound_volume = 1.0
			else:
				sound_volume = option_dict[EFFECT_VOLUME]
			self.animate_numframes = BURST_EFFECT_NUMFRAMES
			# play burst sound
			if self.sound != None and sound_volume > 0: self.sound.play('3roboditzfade', sound_volume)
		elif self.type == TRANSFER_EFFECT:
			if option_dict[EFFECT_TARGET] == None:	## REQUIRED PARAMETER!
				logger.critical("can't call a TRANSFER effect with no target!")
				return False
			self.target = option_dict[EFFECT_TARGET]
			if option_dict[EFFECT_SOURCE] == None:	## REQUIRED PARAMETER!
				logger.critical("can't call a TRANSFER effect with no source!")
				return False
			self.source = option_dict[EFFECT_SOURCE]
			self.animate_numframes = TRANSFER_EFFECT_NUMFRAMES
			logging.debug("initialized transfer effect")

	def calcFrame(self):
		final_radius = (self.target.rect.width + self.target.rect.height) / 2
		midpoint = self.animate_numframes / 2
		if self.animate_frame < midpoint:
			# first half of animation - getting bigger
			self.frame_burst_radius = int(float(self.animate_frame) / float(midpoint) * final_radius)
		else:
			# second half of animation - getting smaller
			self.frame_burst_radius = int(float(self.animate_numframes - self.animate_frame) / float(midpoint) * final_radius)
			#if burst_radius < 0: burst_radius = 0

		self.frame_gradpercent = float(self.animate_frame) / float(self.animate_numframes)
		#old: center on source (?)
		#origin_x = image.get_width() / 2
		#origin_y = image.get_height() / 2
		# move the center of the effect between the source and the target over the course of the animation
		source_x = self.source.rect.centerx
		source_y = self.source.rect.centery
		#target_x = self.target.rect.centerx
		target_x = self.target.mapCenter[0] + self.target.rect.width/2
		#target_y = self.target.rect.centery
		target_y = self.target.mapCenter[1] + self.target.rect.height/2
		logging.debug("source center is {0}, target center is {1}".format(self.source.rect.center, self.target.rect.center))
		self.frame_origin_x = source_x + (self.frame_gradpercent * (target_x - source_x))
		self.frame_origin_y = source_y + (self.frame_gradpercent * (target_y - source_y))


	def draw(self, image, windowRect = None):
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
			self.calcFrame()
			logging.debug("drawing transfer effect with burst_radius {0} at {1}".format(self.frame_burst_radius, (self.frame_origin_x, self.frame_origin_y)))
			grad_color = [int(self.frame_gradpercent*c) for c in colors.PINK]
			# NOTE: map effects are drawn directly onto the display !!! coordinates must be localized to the screen
			# calculate frame screen position from map position
			screenpos = (self.frame_origin_x - windowRect[0], self.frame_origin_y - windowRect[1])
			pygame.draw.circle(image, grad_color, screenpos, self.frame_burst_radius, 0)
		else:
			logger.critical("unknown effect type: {0}".format(self.type))
	
	def update(self, ticks):
		if ticks - self.animate_last_update > self.animate_delay:
			self.animate_frame += 1
			if self.animate_frame >= self.animate_numframes:
				return False	# end the effect, only go through it once
			self.animate_last_update = ticks
		return True
		
	def onScreen(self, windowRect):
		windowRight = windowRect.left + windowRect.width
		windowBottom = windowRect.top + windowRect.height
		# if effect is on the screen, we will draw it
		if self.type == TRANSFER_EFFECT:
			self.calcFrame()
			logging.debug("calculated transfer effect with burst_radius {0} at {1}".format(self.frame_burst_radius, (self.frame_origin_x, self.frame_origin_y)))
			effectLeft = self.frame_origin_x - self.frame_burst_radius
			effectRight = self.frame_origin_x + self.frame_burst_radius
			effectTop = self.frame_origin_y - self.frame_burst_radius
			effectBottom = self.frame_origin_y + self.frame_burst_radius
			if effectLeft > windowRight: return False
			if effectRight < windowRect.left: return False
			if effectBottom < windowRect.top: return False
			if effectTop > windowBottom: return False
			return True	# effect IS on the screen

		return None #unhandled, should not be called in this case

