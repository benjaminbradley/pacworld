#!/usr/bin/env python

import pygame # Provides what we need to make a game
import sys # Gives us the sys.exit function to close our program
import random # Can generate random positions for the pong ball
import pygame.mixer	# sounds!

from pygame.locals import *
from pygame import *

from shape import Shape

# define colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BALLCOLOR = (255,255,0)

JOYSTICK_NOISE_LEVEL = 0.1

NUM_SOUND_CHANNELS = 1
SOUNDS = {
	'3robobeat' : 'sounds/132394__blackie666__robofart.wav',
	'3roboditzfade' : 'sounds/135377__blackie666__nomnomnom.wav'
}
sound_data = {}	# hash of shortname (above) to Sound data
sound_channels = []

print "DEBUG: loaded libraries"


def wait4space():
	done = False
	while not done:
		# Handle events, starting with the quit event
		for event in pygame.event.get():
			if event.type == QUIT:
				pygame.quit()
				sys.exit()
			if event.type == KEYDOWN:
				if event.key == K_SPACE:
					done = True

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
			print "ERROR: no joysticks found"
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

		# Create a single shape and add it to a sprite group
		self.shape = Shape(self.displaySize, 3)
		self.shape.bg = self.background
		self.sprites = sprite.Group(self.shape)

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
						if(i == 4):
							self.shape.sizeDown()
						elif(i == 5):
							self.shape.sizeUp()
						elif(i == 6):
							self.shape.lessSides()
						elif(i == 7):
							self.shape.moreSides()
						elif(i == 8):
							self.shape.reset()
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
		# end for (events)
		
		# movement should be smooth, so not tied to event triggers
		fbAxis = round(self.joystick.get_axis(0), 3)
		if(abs(fbAxis) > JOYSTICK_NOISE_LEVEL):
			print "fbAxis is: "+str(fbAxis)
			if fbAxis < -JOYSTICK_NOISE_LEVEL:
				self.shape.moveFwd()
			elif fbAxis > JOYSTICK_NOISE_LEVEL:
				self.shape.moveBack()
			#else: # fbAxis within JOYSTICK_NOISE_LEVEL of 0
			#	fbVec = 0
		
		#lrVec = 0
		lrAxis = round(self.joystick.get_axis(1), 3)
		if(abs(lrAxis) > JOYSTICK_NOISE_LEVEL):
			print "lrAxis is: "+str(lrAxis)
			if lrAxis < -JOYSTICK_NOISE_LEVEL:
				self.shape.rotateLeft()
			elif lrAxis > JOYSTICK_NOISE_LEVEL:
				self.shape.rotateRight()
			#else: # fbAxis within JOYSTICK_NOISE_LEVEL of 0
			#	lrVec = 0
		
		#self.shape.vector = (lrVec, fbVec)
		
# The class for a blocking wall
class Wall(sprite.Sprite):

	def __init__(self, displaySize, point1, point2):
		# Initialize the sprite base class
		super(Wall, self).__init__()

		# Get the display size for working out collisions later
		self.displaySize = displaySize

		# Set our image to a new surface, the size of the screen rectangle
		self.image = Surface(displaySize)

		# Fill the image with a green colour (specified as R,G,B)
		self.image.fill(BLACK)
		self.image.set_colorkey(BLACK, RLEACCEL)	# set the background to transparent

		# Get width proportionate to display size
		lineWidth = displaySize[0] / 80
		print "DEBUG: creating new wall from {0} to {1}".format(point1, point2)
		# draw the line on the surface
		self.rect = pygame.draw.line(self.image, WHITE, point1, point2, lineWidth)
		print "DEBUG: wall rect is {0}".format(self.rect)
		# grab a bitmask for collision detection
		self.mask = pygame.mask.from_surface(self.image)
		print "DEBUG: wall mask is {0}".format(self.mask)

	def draw(self, display):
		# Draw the background to the display that has been passed in
		display.blit(self.image, (0,0))
				
# The class for the background
class Background:
	
	def __init__(self, displaySize):
		
		# Set our image to a new surface, the size of the screen rectangle
		self.image = Surface(displaySize)
		
		# Fill the image with a green colour (specified as R,G,B)
		self.image.fill(BLACK)
		
		self.walls = [] # List to hold the walls
		
		# draw a border, registering each line as a wall
		topLt = (100, 50)
		#topRt = (displaySize[0]-1, 0)
		topRt = (500, 50)
		#botLt = (0, displaySize[1]-1)
		botLt = (100, 400)
		#botRt = (displaySize[0]-1, displaySize[1]-1)
		botRt = (500, 400)
		wallDefs = (
			(topLt, topRt),
			(topRt, botRt),
			(botRt, botLt),
			(botLt, topLt)
			)
		for wallPoints in wallDefs:
			self.walls.append( Wall(displaySize, wallPoints[0], wallPoints[1]) )
		
	def draw(self, display):
		# Draw the background to the display that has been passed in
		display.blit(self.image, (0,0))
		for wall in self.walls:
			wall.draw(display)

	def wallCollision(self, target):
		for wall in self.walls:
			a = wall
			b = target
			#We calculate the offset of the second mask relative to the first mask.
			offset_x = b.rect.left
			offset_y = b.rect.top
			# See if the two masks at the offset are overlapping.
			if a.mask.overlap(b.mask, (offset_x, offset_y)):
				print "DEBUG: collision detected with wall {0}!".format(wall)
				print "DEBUG: target top/bottom, left/right is: {0}, {1}; {2}, {3}".format(target.rect.top, target.rect.bottom, target.rect.left, target.rect.right)
				print "DEBUG: wall top/bottom, left/right is: {0}, {1}; {2}, {3}".format(wall.rect.top, wall.rect.bottom, wall.rect.left, wall.rect.right)
				print "DEBUG: offset x,y is: {0}, {1}".format(offset_x, offset_y)
				return True
		return False
	
			
if __name__ == '__main__':
	game = ShapeTest()
	game.run()
