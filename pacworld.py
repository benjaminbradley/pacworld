#!/usr/bin/env python

import pygame # Provides what we need to make a game
import sys # Gives us the sys.exit function to close our program
import random
import logging

from pygame.locals import *
from pygame import *

import pacglobal
#import colors
from shape import Shape
from shape import *
from map import Map
import world
from world import World
from pacsounds import Pacsounds,getPacsound
from player import Player

INPUT_KEYBOARD = 'kb'
INPUT_JOYSTICK = 'joy'
JOYSTICK_NOISE_LEVEL = 0.1

MAX_RANDOM_SEED = 65535


# Our main game class
class Pacworld:
	
	def __init__(self):
		logging.basicConfig(format='%(asctime)-15s:%(levelname)s:%(filename)s#%(funcName)s(): %(message)s', level=logging.DEBUG)	# filename='myapp.log'
		logging.debug("Initializing Pacworld()...")
		
		# Make the display size a member of the class
		#self.displaySize = (640, 480)
		self.displaySize = (800,600)
		#self.displaySize = (1024, 768)
		self.character_size = self.displaySize[0] / 10
		
		# Initialize pygame
		pygame.init()
		
		self.sound = getPacsound()
		
		# Create a clock to manage time
		self.clock = pygame.time.Clock()
		
		# Initialize the joysticks (if present)
		pygame.joystick.init()
		
		# Get count of joysticks
		joystick_count = pygame.joystick.get_count()
		self.input_mode = None
		if joystick_count == 0:
			logging.warning("no joysticks found, using keyboard for input")
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
		display.set_caption("WORKING NAME: Pacworld")
		
		# Create the window
		self.display = display.set_mode(self.displaySize)
		font = pygame.font.Font(None, 30)
		textBitmap = font.render("Generating world...", True, colors.WHITE)
		#textRect = textBitmap.get_rect().width
		#print "DEBUG: textRect is: {0}".format(textRect)
		textWidth = textBitmap.get_rect().width
		self.display.blit(textBitmap, [self.displaySize[0]/2 - textWidth/2, self.displaySize[1]/2])
		display.update()
		
		
		# if no random seed was given, make one up:
		if(True):
			crazySeed = random.randint(0, MAX_RANDOM_SEED)
			logging.info("USING RANDOM SEED: {0}",format(crazySeed))
		else:
			# cool seeds: 24669 
			crazySeed = 24669
			logging.info("USING CHOSEN SEED: {0}",format(crazySeed))
		
		SCALE_FACTOR = 2


		random.seed(crazySeed)

		mapSize = [SCALE_FACTOR*x for x in self.displaySize]
		
		gridSize = int(self.character_size * 1.5)
		gridDisplaySize = (mapSize[0] / gridSize, mapSize[1] / gridSize)	# assumes square grid cells
		logging.debug("gridDisplaySize is {0}".format(gridDisplaySize))

		# Create the world, passing through the grid size
		theworld = World(gridDisplaySize)
		
		# Create the world map, passing through the display size and world map
		self.map = Map(mapSize, self.displaySize, self.character_size, theworld)
		art = theworld.addArt(self.map)
		shapes = self.map.addShapes()
		self.sprites = sprite.Group(shapes, art)

		# Create the player object and add it's shape to a sprite group
		self.player = Player()
		self.player.shape = self.map.shapes[0]	# just grab the first shape for the player

		self.map.player = self.player
		#self.player.shape.mapCenter = [int(5.5*self.map.grid_cellwidth-self.shape.side_length/2), int(5.5*self.map.grid_cellheight-self.shape.side_length/2)]
		
		logging.info("USING RANDOM SEED: {0}".format(crazySeed))

		# play a "startup" sound
		self.sound.play('3robobeat')
	

	def run(self):
		# Runs the game loop
		
		while True:
			# The code here runs when every frame is drawn
			curtime = pygame.time.get_ticks()
			#print "looping"
			
			# Handle Events
			self.handleEvents()
			
			# update the map
			self.map.update(curtime)
			
			# Draw the background
			self.map.draw(self.display)
			
			# Update and draw the sprites
			self.sprites.update(curtime)
			#print "DEBUG: drawing shape via sprite group. shape rect is: {0}".format(self.shape.rect)
			# draw the shape by itself onto the display. it's always there.
			self.player.shape.draw(self.display)
			windowRect = self.map.getWindowRect()
			# NOTE: we only want to show the art that is currently onscreen, and it needs to be shifted to its correct position
			for artpiece in self.map.arts:
				# if artpiece is on the screen, we will draw it
				if not artpiece.onScreen(windowRect): continue
				#print "DEBUG: drawing art at {0}".format(artpiece.rect)
				artpiece.draw(self.display, windowRect)
			
			# draw any other shapes that are currently onscreen
			for shape in self.map.shapes:
				# if artpiece is on the screen, we will draw it
				if not shape.onScreen(windowRect): continue
				#logging.debug("drawing shape {0} at {1}".format(shape.id, shape.mapCenter))
				shape.draw(self.display)
			
			
			# Update the full display surface to the screen
			display.update()
			
			# Limit the game to 30 frames per second
			self.clock.tick(30)
			
			# advance frame counter
			pacglobal.nextframe()
			
	def handleEvents(self):
		
		# Handle events, starting with the quit event
		for event in pygame.event.get():
			if event.type == QUIT:
				pygame.quit()
				sys.exit()

			if(self.input_mode == INPUT_JOYSTICK):
				# Possible joystick actions: JOYAXISMOTION JOYBALLMOTION JOYBUTTONDOWN JOYBUTTONUP JOYHATMOTION
				if event.type == pygame.JOYBUTTONDOWN:
					logging.debug("Joystick button pressed.")
					for i in range( self.num_buttons ):
						if(self.joystick.get_button(i) and not self.button_status[i]):
							self.button_status[i] = True
							logging.debug("Button "+str(i+1)+" pressed.")
							if(i == 0):	# "bottom" button
								self.player.shape.tryAsk()
							elif(i == 1):	# "right" button
								self.player.shape.trySwirlRight()
							elif(i == 2):	# "left" button
								self.player.shape.trySwirlLeft()
							elif(i == 3):	# "top" button
								self.player.shape.tryGive()
							elif(i == 4):
								self.player.shape.sizeDown()
							elif(i == 5):
								self.player.shape.sizeUp()
							elif(i == 6):
								self.player.shape.lessSides()
							elif(i == 7):
								self.player.shape.moreSides()
							elif(i == 8):
								self.player.shape.reset()
							elif(i == 9):	# button 10 triggers program exit
								logging.debug("Quitting program.")
								pygame.quit()
								sys.exit()
							
				if event.type == pygame.JOYBUTTONUP:
					logging.debug("Joystick button released.")
					for i in range( self.num_buttons ):
						if(not self.joystick.get_button(i) and self.button_status[i]):
							self.button_status[i] = False
							logging.debug("Button "+str(i+1)+" released.")
			# end of : input_mode == INPUT_JOYSTICK

			if(self.input_mode == INPUT_KEYBOARD):
				if event.type == KEYDOWN:
					# Find which key was pressed
					#if event.key == K_s:
					#elif event.key == K_w:
					if event.key == K_w:	# "top" button
						self.player.shape.tryGive()
					elif event.key == K_a:	# "left" button
						self.player.shape.trySwirlLeft()
					elif event.key == K_s:	# "bottom" button
						self.player.shape.tryAsk()
					elif event.key == K_d:	# "right" button
						self.player.shape.trySwirlRight()
					elif event.key == K_DOWN:
						self.player.shape.startMove(DIR_DOWN)
					elif event.key == K_UP:
						self.player.shape.startMove(DIR_UP)
					elif event.key == K_RIGHT:
						self.player.shape.startMove(DIR_RIGHT)
					elif event.key == K_LEFT:
						self.player.shape.startMove(DIR_LEFT)
					elif event.key == K_t:	# NOTE: "teleport" effect - FOR DEBUG ONLY ??
						self.player.shape.reset()
					elif event.key == K_ESCAPE:
						pygame.quit()
						sys.exit()
			
			
				if event.type == KEYUP:
					if event.key == K_DOWN:
						self.player.shape.stopMove(DIR_DOWN)
					elif event.key == K_UP:
						self.player.shape.stopMove(DIR_UP)
					elif event.key == K_RIGHT:
						self.player.shape.stopMove(DIR_RIGHT)
					elif event.key == K_LEFT:
						self.player.shape.stopMove(DIR_LEFT)
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
				self.player.shape.move(0, fbAxis * self.player.shape.linearSpeed)
		
			lrAxis = round(self.joystick.get_axis(1), 3)
			if(abs(lrAxis) > JOYSTICK_NOISE_LEVEL):
				#print "DEBUG: lrAxis is: "+str(lrAxis)
				self.player.shape.move(lrAxis * self.player.shape.linearSpeed, 0)

			
if __name__ == '__main__':
	game = Pacworld()
	game.run()
