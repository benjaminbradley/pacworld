import pygame


from pacsounds import Pacsounds
import colors


BURST_EFFECT = 1



BURST_EFFECT_NUMFRAMES = 6



class Effect():
	def __init__(self, type, sound_volume = 1.0):
		self.type = type
		
		# initialize subsystems
		self.sound = Pacsounds()
		
		fps = 10
		
		# initialize animation timer
		if self.type == BURST_EFFECT:
			self.in_burstEffect = True
			self.burstEffect_delay = 1000 / fps
			self.burstEffect_last_update = 0
			self.burstEffect_frame = 0
			self.burstEffect_numframes = BURST_EFFECT_NUMFRAMES
			# play burst sound
			if self.sound != None and sound_volume > 0: self.sound.play('3roboditzfade', sound_volume)


	def draw(self, image):
		if self.type == BURST_EFFECT:
			final_radius = image.get_width() / 2
			#print "DEBUG: Effect.draw(): frame={0}, numframe={1}, radius={2}".format(self.burstEffect_frame, self.burstEffect_numframes, final_radius)
			burst_radius = int(float(self.burstEffect_frame) / float(self.burstEffect_numframes) * final_radius)
			lineWidth = 2
			if burst_radius < lineWidth: lineWidth = burst_radius
			gradpercent = float(self.burstEffect_frame) / float(self.burstEffect_numframes)
			grad_color = [int(gradpercent*c) for c in colors.NEONBLUE]
			#print "DEBUG: Effect.draw() in burstEffect: burst_radius = {0}, gradpercent = {1}, grad_color={2}".format(burst_radius, gradpercent, grad_color)
			pygame.draw.circle(image, grad_color, (final_radius,final_radius), burst_radius, lineWidth)
	
	def update(self, ticks):
		if self.type == BURST_EFFECT:
			#print "DEBUG: Effect.advance() in burstEffect frame {0}".format(self.burstEffect_frame)
			if ticks - self.burstEffect_last_update > self.burstEffect_delay:
				self.burstEffect_frame += 1
				if self.burstEffect_frame >= self.burstEffect_numframes:
					return False	# end the effect, only go through it once
				self.burstEffect_last_update = ticks
			return True
		
