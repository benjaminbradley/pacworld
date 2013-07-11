#!/usr/bin/env python

import pygame # Provides what we need to make a game
import sys # Gives us the sys.exit function to close our program
import random # Can generate random positions for the pong ball
import pygame.mixer	# sounds!

from pygame.locals import *
from pygame import *

# define colors
BLACK = (0, 0, 0)
BALLCOLOR = (255,255,0)
RADIUS_MINIMUM = 5
RADIUS_MAXIMUM = 140

JOYSTICK_NOISE_LEVEL = 0.1

NUM_SOUND_CHANNELS = 1
SOUNDS = {
	'3robobeat' : 'sounds/132394__blackie666__robofart.wav',
	'3roboditzfade' : 'sounds/135377__blackie666__nomnomnom.wav'
}
sound_data = {}	# hash of shortname (above) to Sound data
sound_channels = []

print "loaded libraries"

# Our main game class
class ShapeTest:
	
	def __init__(self):
		
		# Make the display size a member of the class
		self.displaySize = (640, 480)
		
		# Initialize pygame
		pygame.init()
		
		# initialize the sound mixer
		#pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=4096)
		pygame.mixer.init(48000, -16, 1, 1024)
		pygame.mixer.set_num_channels(NUM_SOUND_CHANNELS)
		print("DEBUG: Initializing "+str(NUM_SOUND_CHANNELS)+" sound channels...")
		global sound_channels
		for i in range(NUM_SOUND_CHANNELS):
			print("DEBUG: Initializing sound channel "+str(i+1))
			sound_channels.append(pygame.mixer.Channel(i))
		
		for sound_name in SOUNDS.keys():
			sound_data[sound_name] = pygame.mixer.Sound(SOUNDS[sound_name])
			print "DEBUG: loaded sound '{0}' from {1}: {2} sec".format(sound_name, SOUNDS[sound_name], sound_data[sound_name].get_length())
		
		print "DEBUG: sound_channels.len = {0}".format(len(sound_channels))
		sound_channels[0].play(sound_data['3robobeat'])
		
		# Create a clock to manage time
		self.clock = pygame.time.Clock()
		
		# Initialize the joysticks
		pygame.joystick.init()
		
		# Get count of joysticks
		joystick_count = pygame.joystick.get_count()
		if joystick_count == 0:
			print "no joysticks found"
			exit()

		self.joystick = pygame.joystick.Joystick(0)
		self.joystick.init()
		self.button_status = []
		self.num_buttons = self.joystick.get_numbuttons()
		for i in range( self.num_buttons ):
			self.button_status.append(self.joystick.get_button(i))
		
		# Set the window title
		display.set_caption("Shape Test")
		
		# Create the window
		self.display = display.set_mode(self.displaySize)
			
		# Create the background, passing through the display size
		self.background = Background(self.displaySize)

		# Create a single ball and add it to a sprite group
		self.ball = Ball(self.displaySize)
		self.sprites = sprite.Group(self.ball)

	def run(self):
		# Runs the game loop
		
		while True:
			# The code here runs when every frame is drawn
			#print "looping"
			
			# Handle Events
			self.handleEvents()
			
			# Draw the background
			self.background.draw(self.display)
			
			# Update and draw the sprites
			self.sprites.update(pygame.time.get_ticks())
			self.sprites.draw(self.display)
			
			# Check for collisions
			#
			
			# Update the full display surface to the screen
			display.update()
			
			# Limit the game to 30 frames per second
			self.clock.tick(30)
			
	def handleEvents(self):
		
		# Handle events, starting with the quit event
		for event in pygame.event.get():
			if event.type == QUIT:
				pygame.quit()
				sys.exit()

			# Possible joystick actions: JOYAXISMOTION JOYBALLMOTION JOYBUTTONDOWN JOYBUTTONUP JOYHATMOTION
			if event.type == pygame.JOYBUTTONDOWN:
				print("Joystick button pressed.")
				for i in range( self.num_buttons ):
					if(self.joystick.get_button(i) and not self.button_status[i]):
						self.button_status[i] = True
						print "Button "+str(i+1)+" pressed."
						if(i == 0):
							self.ball.startBurst()
						elif(i == 4):
							self.ball.sizeDown()
						elif(i == 5):
							self.ball.sizeUp()
						elif(i == 8):
							self.ball.reset()
						elif(i == 9):	# button 10 triggers program exit
							print "Quitting program."
							pygame.quit()
							sys.exit()
							
			if event.type == pygame.JOYBUTTONUP:
				print("Joystick button released.")
				for i in range( self.num_buttons ):
					if(not self.joystick.get_button(i) and self.button_status[i]):
						self.button_status[i] = False
						print "Button "+str(i+1)+" released."
			
			fbVec = 0
			fbAxis = round(self.joystick.get_axis(0), 3)
			if(abs(fbAxis) > JOYSTICK_NOISE_LEVEL):
				print "fbAxis is: "+str(fbAxis)
				if fbAxis < -JOYSTICK_NOISE_LEVEL:
					# move ball up
					fbVec = -1
				elif fbAxis > JOYSTICK_NOISE_LEVEL:
					# move ball down
					fbVec = 1
				else: # fbAxis within JOYSTICK_NOISE_LEVEL of 0
					fbVec = 0
			
			lrVec = 0
			lrAxis = round(self.joystick.get_axis(1), 3)
			if(abs(lrAxis) > JOYSTICK_NOISE_LEVEL):
				print "lrAxis is: "+str(lrAxis)
				if lrAxis < -JOYSTICK_NOISE_LEVEL:
					# move ball left
					lrVec = -1
				elif lrAxis > JOYSTICK_NOISE_LEVEL:
					# move to right
					lrVec = 1
				else: # fbAxis within JOYSTICK_NOISE_LEVEL of 0
					lrVec = 0
			
			self.ball.vector = (lrVec, fbVec)
			
			
			#if event.type == KEYDOWN:
				# Find which key was pressed and start moving appropriate bat
				#if event.key == K_s:
				#elif event.key == K_w:
				#if event.key == K_DOWN:
				#elif event.key == K_UP:
			
			#if event.type == KEYUP:
				#if event.key == K_s or event.key == K_w:
				#	self.player1Bat.stopMove()
				#elif event.key == K_DOWN or event.key == K_UP:
				#	self.player2Bat.stopMove()
				
# The class for the background
class Background:
	
	def __init__(self, displaySize):
		
		# Set our image to a new surface, the size of the screen rectangle
		self.image = Surface(displaySize)
		
		# Fill the image with a green colour (specified as R,G,B)
		self.image.fill(BLACK)
		
		# Get width proportionate to display size
		lineWidth = displaySize[0] / 80
		
		# Create a rectangle to make the white line
		lineRect = Rect(0, 0, lineWidth, displaySize[1])
		lineRect.centerx  = displaySize[0] / 2
		draw.rect(self.image, (255, 255, 255), lineRect)
		
	def draw(self, display):
			
		# Draw the background to the display that has been passed in
		display.blit(self.image, (0,0))


# The class for the ball
class Ball(sprite.Sprite):
	
	def __init__(self, displaySize):
			
		# Initialize the sprite base class
		super(Ball, self).__init__()
		
		# Get the display size for working out collisions later
		self.displaySize = displaySize
		
		self.color = BALLCOLOR
		
		# Get a radius value proportionate to the display size
		self.radius = displaySize[0] / 30
		self.outlineWidth = 4
		
		# initialize effects
		self.in_burstEffect = False
		
		self.makeSprite()
			
		# Work out a speed
		self.speed = displaySize[0] / 110

		# Reset the ball
		self.reset()
	
	def makeSprite(self):
		diameter = self.radius + self.radius
		# Create an image for the sprite
		self.image = Surface((diameter, diameter))
		self.image.fill(BLACK)
		self.image.set_colorkey(BLACK, RLEACCEL)	# set the background to transparent
		pygame.draw.circle(self.image, self.color, (self.radius,self.radius), self.radius, self.outlineWidth)
		
		# draw any effects
		if self.in_burstEffect:
			width = 2
			print "frame={0}, numframe={1}, radius={2}".format(self.burstEffect_frame, self.burstEffect_numframes, self.radius)
			burst_radius = int(float(self.burstEffect_frame) / float(self.burstEffect_numframes) * self.radius)
			if width > burst_radius: width = burst_radius
			gradcolor = int(float(self.burstEffect_frame) / float(self.burstEffect_numframes) * 255)
			print "in burstEffect: burst_radius = {0}, gradcolor = {1}".format(burst_radius, gradcolor)
			grey_color = (gradcolor, gradcolor, gradcolor)
			pygame.draw.circle(self.image, grey_color, (self.radius,self.radius), burst_radius, width)
		
		# save old rect's location
		if hasattr(self, 'rect'):
			self.curctr = (self.rect.centerx, self.rect.centery)
			#print "saving curctr as "+str(self.curctr)
		
		# Create the sprites rectangle from the image
		self.rect = self.image.get_rect()
		# put the sprite back where it was
		if hasattr(self, 'curctr'):
			#print "setting centerx/y as "+str(self.curctr)
			(self.rect.centerx, self.rect.centery) = self.curctr
	
	def reset(self):
		
		# Start the ball directly in the centre of the screen
		self.rect.centerx = self.displaySize[0] / 2
		self.rect.centery = self.displaySize[1] / 2
		
		self.vector = (0, 0)
	
	def update(self, t):
		
		# Check if the ball has hit a wall
		if self.rect.midtop[1] <= 0:
			# Hit top side
			self.reflectVector()
		elif self.rect.midleft[0] <= 0:
			# Hit left side
			#self.reset()
			self.reflectVector()
		elif self.rect.midright[0] >= self.displaySize[0]:
			#self.reset()
			self.reflectVector()
		elif self.rect.midbottom[1] >= self.displaySize[1]:
			# Hit bottom side
			self.reflectVector()
		
		# Move in the direction of the vector
		self.rect.centerx += (self.vector[0] * self.speed)
		self.rect.centery += (self.vector[1] * self.speed)
		
		# check for and update sprite animations
		if self.in_burstEffect:
			print "DEBUG: t={0}, lastUpdate={1}, frame={2}".format(t, self.burstEffect_last_update, self.burstEffect_frame)
			if t - self.burstEffect_last_update > self.burstEffect_delay:
				self.burstEffect_frame += 1
				if self.burstEffect_frame >= self.burstEffect_numframes:
					self.in_burstEffect = False	# end the effect, only go through it once
				self.burstEffect_last_update = t
			self.makeSprite()
		
		
	
	def startBurst(self):
		fps = 10
		# initialize animation timer
		self.in_burstEffect = True
		#self.burstEffect_start = pygame.time.get_ticks()
		self.burstEffect_delay = 1000 / fps
		self.burstEffect_last_update = 0
		self.burstEffect_frame = 0
		self.burstEffect_numframes = 8
		# play burst sound
		global sound_channels
		print "DEBUG: playing sound 3roboditzfade: {0} sec".format(sound_data['3roboditzfade'].get_length())
		print "DEBUG: sound_channels.len = {0}".format(len(sound_channels))
		sound_channels[0].play(sound_data['3roboditzfade'])
		


	def sizeUp(self):
		print "old radius="+str(self.radius)
		self.radius *= 1.1
		if self.radius > RADIUS_MAXIMUM:
			self.radius = RADIUS_MAXIMUM
		self.speed = self.radius / 3.5
		print "new radius="+str(self.radius)
		self.makeSprite()

	def sizeDown(self):
		print "old radius="+str(self.radius)
		self.radius *= 0.9
		if(self.radius < RADIUS_MINIMUM):
			self.radius = RADIUS_MINIMUM
		self.speed = self.radius / 3.5
		print "new radius="+str(self.radius)
		self.makeSprite()
	
	def reflectVector(self):
		
		# Gets the current angle of the ball and reflects it, for bouncing
		# off walls
		deltaX = self.vector[0]
		deltaY = - self.vector[1]
		self.vector = (deltaX, deltaY)
		
		
	def batCollisionTest(self, bat):
	
		# Check if the ball has had a collision with the bat
		if Rect.colliderect(bat.rect, self.rect):
			
			# Work out the difference between the start and end points
			deltaX = self.rect.centerx - bat.rect.centerx
			deltaY = self.rect.centery - bat.rect.centery
			
			# Make the values smaller so it's not too fast
			deltaX = deltaX / 12
			deltaY = deltaY / 12
			
			# Set the balls new direction
			self.vector = (deltaX, deltaY)
			
if __name__ == '__main__':
	game = ShapeTest()
	game.run()
