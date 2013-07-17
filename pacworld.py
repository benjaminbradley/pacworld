#!/usr/bin/env python

import pygame # Provides what we need to make a game
import sys # Gives us the sys.exit function to close our program
import random # Can generate random positions for the pong ball

from pygame.locals import *
from pygame import *

from shape import Shape
from shape import *
from map import Map
import colors
from pacsounds import Pacsounds

INPUT_KEYBOARD = 'kb'
INPUT_JOYSTICK = 'joy'
JOYSTICK_NOISE_LEVEL = 0.1


print "DEBUG: loaded libraries"

# Our main game class
class Pacworld:
	
	def __init__(self):
		
		# Make the display size a member of the class
		self.displaySize = (640, 480)
		
		# Initialize pygame
		pygame.init()
		
		self.sound = Pacsounds()
		
		# Create a clock to manage time
		self.clock = pygame.time.Clock()
		
		# Initialize the joysticks (if present)
		pygame.joystick.init()
		
		# Get count of joysticks
		joystick_count = pygame.joystick.get_count()
		self.input_mode = None
		if joystick_count == 0:
			print "WARN: no joysticks found, using keyboard for input"
			self.input_mode = INPUT_KEYBOARD
		else:
			self.input_mode = INPUT_JOYSTICK
		
		if self.input_mode == INPUT_JOYSTICK:
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
		self.shape.sound = self.sound
		
		# play a "startup" sound
		self.sound.play('3robobeat')
	

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

			if(self.input_mode == INPUT_JOYSTICK):
				# Possible joystick actions: JOYAXISMOTION JOYBALLMOTION JOYBUTTONDOWN JOYBUTTONUP JOYHATMOTION
				if event.type == pygame.JOYBUTTONDOWN:
					print("Joystick button pressed.")
					for i in range( self.num_buttons ):
						if(self.joystick.get_button(i) and not self.button_status[i]):
							self.button_status[i] = True
							print "Button "+str(i+1)+" pressed."
							if(i == 0):
								self.shape.startBurst()
							elif(i == 4):
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
			# end of : input_mode == INPUT_JOYSTICK

			if(self.input_mode == INPUT_KEYBOARD):
				if event.type == KEYDOWN:
					# Find which key was pressed
					#if event.key == K_s:
					#elif event.key == K_w:
					if event.key == K_SPACE:
						self.shape.startBurst()
					elif event.key == K_DOWN:
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
			# end of (INPUT_KEYBOARD)
		# end for (events)
		
		# movement should be smooth, so not tied to event triggers
		if(self.input_mode == INPUT_JOYSTICK):
			fbAxis = round(self.joystick.get_axis(0), 3)
			if(abs(fbAxis) > JOYSTICK_NOISE_LEVEL):
				#print "DEBUG: fbAxis is: "+str(fbAxis)
				self.shape.move(0, fbAxis * self.shape.linearSpeed)
		
			lrAxis = round(self.joystick.get_axis(1), 3)
			if(abs(lrAxis) > JOYSTICK_NOISE_LEVEL):
				#print "DEBUG: lrAxis is: "+str(lrAxis)
				self.shape.move(lrAxis * self.shape.linearSpeed, 0)

			
if __name__ == '__main__':
	game = Pacworld()
	game.run()
