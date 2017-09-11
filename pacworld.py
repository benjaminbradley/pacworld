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
from pacdisplay import Pacdisplay
from player import Player

INPUT_KEYBOARD = 'kb'
INPUT_JOYSTICK = 'joy'
JOYSTICK_NOISE_LEVEL = 0.1

MAX_RANDOM_SEED = 65535


# Our main game class
class Pacworld:
	
	def __init__(self):
		logging.basicConfig(format='%(asctime)-15s:%(levelname)s:%(filename)s#%(funcName)s(): %(message)s', level=logging.DEBUG, filename='log/pacworld.log')
		logging.debug("Initializing Pacworld()...")
		
		# Make the display size a member of the class
		#self.displaySize = (640, 480)
		self.windowed_resolution = (800,600)
		self.display = Pacdisplay(self.windowed_resolution)
		#self.displaySize = (1024, 768)
		self.character_size = int(self.display.getDisplaySize()[0] / 10)
		
		# Initialize pygame
		pygame.init()
		# capture current screen res for fullscreen mode
		self.fullscreen_resolution = (display.Info().current_w, display.Info().current_h)
		
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
			logging.info("joystick present, using joystick for input")
			self.input_mode = INPUT_JOYSTICK
		
		if self.input_mode == INPUT_JOYSTICK:
			self.joystick = pygame.joystick.Joystick(0)
			self.joystick.init()
			self.button_status = []
			self.num_buttons = self.joystick.get_numbuttons()
			for i in range( self.num_buttons ):
				self.button_status.append(self.joystick.get_button(i))
			self.num_axes = self.joystick.get_numaxes()
			if(self.num_axes == 4):
				self.joy_axis_x = 2
				self.joy_axis_y = 3

		# Set the window title
		pygame.display.set_caption("WORKING NAME: Pacworld")
		
		# Create the window
		self.surface = pygame.display.set_mode(self.display.getDisplaySize())
		self.is_fullscreen = False
		font = pygame.font.Font(None, 30)
		textBitmap = font.render("Generating world...", True, colors.WHITE)
		#textRect = textBitmap.get_rect().width
		#print "DEBUG: textRect is: {0}".format(textRect)
		textWidth = textBitmap.get_rect().width
		self.surface.blit(textBitmap, [self.display.getDisplaySize()[0]/2 - textWidth/2, self.display.getDisplaySize()[1]/2])
		pygame.display.update()
		
		
		# if no random seed was given, make one up:
		if(len(sys.argv) > 1):
			# cool seeds: 24669
			# ? 36097
			self.crazySeed = int(sys.argv[1])
			logging.info("USING CHOSEN SEED: {0}".format(self.crazySeed))
		else:
			self.crazySeed = random.randint(0, MAX_RANDOM_SEED)
			logging.info("USING RANDOM SEED: {0}".format(self.crazySeed))
		
		SCALE_FACTOR = 3	# total map is SCALE_FACTOR^2 times the screen size


		random.seed(self.crazySeed)

		mapSize = [SCALE_FACTOR*x for x in self.display.getDisplaySize()]
		
		gridSize = int(self.character_size * 1.5)
		gridDisplaySize = (int(mapSize[0] / gridSize), int(mapSize[1] / gridSize))	# assumes square grid cells
		logging.debug("gridDisplaySize is {0}".format(gridDisplaySize))

		# Create the world, passing through the grid size
		theworld = World(gridDisplaySize)
		
		# Create the world map, passing through the display size and world map
		self.map = Map(mapSize, self.display, self.character_size, theworld)
		art = theworld.addArt(self.map)
		shapes = self.map.addShapes()
		self.sprites = sprite.Group(shapes, art)

		# Create the player object and add it's shape to a sprite group
		self.player = Player()
		self.player.selectShape(self.map.shapes[0])	# just grab the first shape for the player

		self.map.player = self.player
		#self.player.shape.mapTopLeft = [int(5.5*self.map.grid_cellwidth-self.shape.side_length/2), int(5.5*self.map.grid_cellheight-self.shape.side_length/2)]
		
		logging.info("USING RANDOM SEED: {0}".format(self.crazySeed))

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
			
			# Update the sprites
			self.sprites.update(curtime)

			# Draw the background
			self.map.draw(self.surface)
			
			# draw the sprites
			#print "DEBUG: drawing shape via sprite group. shape rect is: {0}".format(self.shape.rect)
			# draw the shape by itself onto the display. it's always there.
			self.player.shape.draw(self.surface)
			windowRect = self.map.player.shape.getWindowRect()
			# NOTE: we only want to show the art that is currently onscreen, and it needs to be shifted to its correct position
			for artpiece in self.player.shape.art_onscreen():
				# if artpiece is on the screen, we will draw it
				#logging.debug("drawing art at {0}".format(artpiece.rect))
				artpiece.draw(self.surface, windowRect)
			
			# draw any other shapes that are currently onscreen
			for shape in self.map.shapes:
				# if artpiece is on the screen, we will draw it
				if not shape.onScreen(windowRect): continue
				#logging.debug("drawing shape {0} at {1}".format(shape.id, shape.mapTopLeft))
				shape.draw(self.surface)
			
			
			# Update the full display surface to the screen
			pygame.display.update()
			
			# display debug if enabled
			pygame.display.set_caption("fps: " + str(int(self.clock.get_fps())))

			# Limit the game to 30 frames per second
			self.clock.tick(30)
			
			# advance frame counter
			pacglobal.nextframe()


	def toggleFullscreen(self):
		screen = pygame.display.get_surface()
		bits = screen.get_bitsize()
		if self.is_fullscreen:
			self.is_fullscreen = False
			flags = screen.get_flags() & ~pygame.FULLSCREEN
			self.display.setDisplaySize(self.windowed_resolution)
		else:
			self.is_fullscreen = True
			flags = screen.get_flags() | pygame.FULLSCREEN
			self.display.setDisplaySize(self.fullscreen_resolution)
		pygame.display.quit()
		pygame.display.init()
		self.surface = pygame.display.set_mode(self.display.getDisplaySize(),flags,bits)


	def handleEvents(self):
		
		# Handle events, starting with the quit event
		for event in pygame.event.get():
			if event.type == QUIT:
				pygame.quit()
				sys.exit()

			if(self.input_mode == INPUT_JOYSTICK):
				# check for joystick movement
				joy_value_y = round(self.joystick.get_axis( self.joy_axis_y ))
				joy_value_x = round(self.joystick.get_axis( self.joy_axis_x ))
				logging.debug("joystick movement = {0},{1}".format(joy_value_x, joy_value_y))
				# -1 = left, 1 = right
				if(joy_value_y == 1):	# -1 = up, down = 1
					self.player.shape.startMove(DIR_DOWN)
				elif(joy_value_y == -1):
					self.player.shape.startMove(DIR_UP)
				else:	# joy_value_y == 0
					self.player.shape.stopMove(DIR_DOWN)
					self.player.shape.stopMove(DIR_UP)
				if(joy_value_x == 1):
					self.player.shape.startMove(DIR_RIGHT)
				elif(joy_value_x == -1):
					self.player.shape.startMove(DIR_LEFT)
				else:	# joy_value_x == 0
					self.player.shape.stopMove(DIR_RIGHT)
					self.player.shape.stopMove(DIR_LEFT)
				
				# Possible joystick actions: JOYAXISMOTION JOYBALLMOTION JOYBUTTONDOWN JOYBUTTONUP JOYHATMOTION
				if event.type == pygame.JOYBUTTONDOWN:
					#logging.debug("Joystick button pressed.")
					for i in range( self.num_buttons ):
						if(self.joystick.get_button(i) and not self.button_status[i]):
							self.button_status[i] = True
							logging.debug("joystick Button "+str(i+1)+" pressed.")
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
								logging.info("That was RANDOM SEED {0}. Hope you had fun.".format(self.crazySeed))
								logging.debug("Quitting program.")
								pygame.quit()
								sys.exit()
							
				if event.type == pygame.JOYBUTTONUP:
					#logging.debug("Joystick button released.")
					for i in range( self.num_buttons ):
						if(not self.joystick.get_button(i) and self.button_status[i]):
							self.button_status[i] = False
							#logging.debug("Button "+str(i+1)+" released.")
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
					elif event.key == K_f:	# toggle fullscreen
						self.toggleFullscreen()
						self.player.shape.updatePosition()
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
					elif event.key == K_SPACE:
						# DEBUG - activate autonomosity
						nearby_shapes = self.map.nearShapes(self.player.shape.getCenter(), self.map.character_size * 1.5, self.player.shape)
						if len(nearby_shapes) > 0:
							#logging.debug("Shapes near to S#{0}: {1}".format(self.id, nearby_shapes))
							receiver = nearby_shapes[0]
							receiver.autonomous = not receiver.autonomous
							logging.debug("toggling autonomy for shape #{0}, now {1}".format(receiver.id, receiver.autonomous))
						else:
							logging.debug("no nearby shapes")
			
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
