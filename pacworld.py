#!/usr/bin/env python

import pygame # Provides what we need to make a game
import sys # Gives us the sys.exit function to close our program
import random # Can generate random positions for the pong ball
import pygame.mixer	# sounds!

from pygame.locals import *
from pygame import *

from shape import Shape
from shape import *
from map import Map
import colors

JOYSTICK_NOISE_LEVEL = 0.1

NUM_SOUND_CHANNELS = 1
SOUNDS = {
	'3robobeat' : 'sounds/132394__blackie666__robofart.wav',
	'3roboditzfade' : 'sounds/135377__blackie666__nomnomnom.wav'
}
sound_data = {}	# hash of shortname (above) to Sound data
sound_channels = []

print "DEBUG: loaded libraries"

# Our main game class
class Pacworld:
	
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
		display.set_caption("Map Test")
		
		# Create the window
		self.display = display.set_mode(self.displaySize)
			
		# Create the background, passing through the display size
		self.map = Map(self.displaySize)

		# Create a single shape and add it to a sprite group
		self.shape = Shape(self.displaySize, 3)
		self.shape.bg = self.map
		self.sprites = sprite.Group(self.shape)

	def run(self):
		# Runs the game loop
		
		while True:
			# The code here runs when every frame is drawn
			#print "looping"
			
			# Handle Events
			self.handleEvents()
			
			# Draw the background
			self.map.draw(self.display, self.shape.mapCenter)
			
			# Update and draw the sprites
			self.sprites.update(pygame.time.get_ticks())
			self.shape.draw(self.display)
			
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

			
			if event.type == KEYDOWN:
				# Find which key was pressed
				#if event.key == K_s:
				#elif event.key == K_w:
				if event.key == K_DOWN:
					self.shape.startMove(DIR_DOWN)
				elif event.key == K_UP:
					self.shape.startMove(DIR_UP)
				elif event.key == K_RIGHT:
					self.shape.startMove(DIR_RIGHT)
				elif event.key == K_LEFT:
					self.shape.startMove(DIR_LEFT)
				elif event.key == K_ESCAPE:
					pygame.quit()
					sys.exit()
			
			
			if event.type == KEYUP:
				if event.key == K_DOWN:
					self.shape.stopMove(DIR_DOWN)
				elif event.key == K_UP:
					self.shape.stopMove(DIR_UP)
				elif event.key == K_RIGHT:
					self.shape.stopMove(DIR_RIGHT)
				elif event.key == K_LEFT:
					self.shape.stopMove(DIR_LEFT)
				#if event.key == K_s or event.key == K_w:
				#	self.player1Bat.stopMove()
				#elif event.key == K_DOWN or event.key == K_UP:
				#	self.player2Bat.stopMove()
		# end for (events)
		
		# movement should be smooth, so not tied to event triggers
		fbAxis = round(self.joystick.get_axis(0), 3)
		if(abs(fbAxis) > JOYSTICK_NOISE_LEVEL):
			print "fbAxis is: "+str(fbAxis)
			self.shape.move(0, fbAxis * self.shape.linearSpeed)
		
		lrAxis = round(self.joystick.get_axis(1), 3)
		if(abs(lrAxis) > JOYSTICK_NOISE_LEVEL):
			print "lrAxis is: "+str(lrAxis)
			self.shape.move(lrAxis * self.shape.linearSpeed, 0)

			
if __name__ == '__main__':
	game = Pacworld()
	game.run()
