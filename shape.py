import random
import pygame # Provides what we need to make a game
import sys # Gives us the sys.exit function to close our program
import math	# sin,cos,pi
import logging

#from pygame.locals import *
from pygame import *

import pacglobal
from pacsounds import Pacsounds,getPacsound
import colors
import effect
from effect import Effect
from swirl import Swirl
import world

MAX_SIDES = 10
SIZE_MINIMUM = 5
SIZE_MAXIMUM = 140
DIR_UP = 'u'
DIR_DOWN = 'd'
DIR_LEFT = 'l'
DIR_RIGHT = 'r'
DIRECTIONS = [DIR_UP, DIR_DOWN, DIR_LEFT, DIR_RIGHT]

BURST_EFFECT_NUMFRAMES = 6
ART_TOUCH_JITTER = 15	# time in game frames that re-touching the same art piece will not trigger a re-touch effect

# The class for Shapes
class Shape(sprite.Sprite):
	
	def __init__(self, displaySize, themap, shape_size, num_sides = 3):
		# Initialize the sprite base class
		super(Shape, self).__init__()
		
		self.type = world.TYPE_CHARACTER
		self.map = themap
		
		# Get the display size for working out collisions later
		self.displaySize = displaySize
		
		self.colorIdx = 0
		self.setColor()
		
		# Get a radius value proportionate to the display size
		self.side_length = shape_size
		self.num_sides = num_sides
		self.outlineWidth = 4
		self.angle = 0
		
		# data for helper functs startmove/stopmove for keyboard movement
		self.going_in_dir = {}	# hash of direction (DIR_* constants) to boolean
		for d in DIRECTIONS: self.going_in_dir[d] = False

		# Work out a speed
		self.setSpeed()

		# initialize effects
		self.effects = {}	# dictionary of Effect.EFFECT_TYPE to Effect class
		
		self.swirls = []	# array of swirls the shape has
		self.curSwirl = None	# array index pointer to "current" swirl
		#self.swirl_angle = 0	#TODO: rotate swirls inside the character
		#self.swirl_angle_delta = some random non-zero value between -20 and 20 (?)
		"""
		the swirls each have an x/y position
		----
		back to shape.py:
		give a swirl
		ask for a swirl
		swirl left
		swirl right
		----
		advanced:
		rotate swirls with swirl_angle
		different swirl rotation direction/speed with swirl_angle_delta
		"""

		# Reset the shape & create the first image
		self.reset()
		
		# experience variables
		self.last_touched_art = {}	# hash of art.id to ticks
		self.last_moved_frame = 0	# frame of last character movement
		
		# initialize subsystems
		self.sound = getPacsound()

	
	def setColor(self):
		self.color = colors.COLORWHEEL[self.colorIdx]
		self.eye_color = colors.YELLOW
	
	def colorUp(self):
		logging.debug("Shape.colorUp()")
		self.colorIdx += 1
		if(self.colorIdx >= len(colors.COLORWHEEL)):
			self.colorIdx = 0
		self.setColor()
		self.makeSprite()

	def colorDn(self):
		logging.debug("Shape.colorDn()")
		self.colorIdx -= 1
		if(self.colorIdx < 0):
			self.colorIdx = len(colors.COLORWHEEL)-1
		self.setColor()
		self.makeSprite()

	def setSpeed(self):
		''' sets the shape's speed based on its size '''
		self.linearSpeed = int(self.side_length / 8)
		self.rotationSpeed = self.linearSpeed
		logging.debug("linearSpeed is now {0}".format(self.linearSpeed))
	
	def makeSprite(self):
		# Create an image for the sprite
		self.image = Surface((self.side_length, self.side_length))
		self.image.fill(colors.BLACK)
		self.image.set_colorkey(colors.BLACK, RLEACCEL)	# set the background to transparent
		if(self.num_sides == 1):
			# dot
			radius = self.outlineWidth + self.outlineWidth
			center = int(float(self.side_length) / 2)
			pygame.draw.circle(self.image, self.color, (center,center), radius, 0)
			pygame.draw.line(self.image, (63,63,63), (center,center), (self.side_length, center), 1)
		elif(self.num_sides == 2):
			# a single line
			y = int(float(self.side_length) / 2)
			pygame.draw.line(self.image, self.color, (0, y), (self.side_length, y), self.outlineWidth)
		elif(self.num_sides > MAX_SIDES):
			radius = int(float(self.side_length) / 2)
			pygame.draw.circle(self.image, self.color, (radius,radius), radius, self.outlineWidth)
		else:
			# todo: generate points around the outside of the circle
			pointlist = []
			for i in range(self.num_sides):
				r = int(float(self.side_length-self.outlineWidth)/2)
				theta = 2 * math.pi * float(i) / float(self.num_sides)
				x = r + int(r * math.cos(theta))
				y = r + int(r * math.sin(theta))
				#print "adding point at {0},{1}".format(x,y)
				pointlist.append((x,y))
			pygame.draw.polygon(self.image, self.color, pointlist, self.outlineWidth)

		# draw any effects
		for effect in self.effects.values():
			effect.draw(self.image)
		
		# draw the "eye" direction indicator
		radius = self.outlineWidth + self.outlineWidth
		center = int(float(self.side_length) / 2)
		pygame.draw.circle(self.image, self.eye_color, (self.side_length-radius, center), radius, self.outlineWidth)
		
		
		# rotate image, if applicable
		if(self.angle != 0):
			self.image = pygame.transform.rotate(self.image, self.angle)

		# get position of old rect
		oldx = None
		if hasattr(self, 'rect'):
			oldx = self.rect.left
			oldy = self.rect.top
		# Create the sprites rectangle from the image
		self.rect = self.image.get_rect()
		# restore position of rect
		if oldx != None:
			self.rect.top = oldy
			self.rect.left = oldx
		
		# create a mask for the sprite (for collision detection)
		self.mask = pygame.mask.from_surface(self.image)
	
	def reset(self):
		# put us in a random square to start
		starty = self.map.grid_cellheight * random.randint(0, self.map.world.rows-1)
		startx = self.map.grid_cellwidth * random.randint(0, self.map.world.cols-1)
		# Start the shape directly in the centre of the screen
		self.mapCenter = [startx, starty]
		self.startMapCenter = self.mapCenter
		self.imageCenter = list(self.mapCenter)
		# reset other attributes as well
		self.angle = 0
		self.makeSprite()
		self.updatePosition()

	def update(self, t):
		# check for on-going movement (for kb input)
		if self.going_in_dir[DIR_DOWN]:
			self.moveDown()
		elif self.going_in_dir[DIR_UP]:
			self.moveUp()
		# once for each axis
		if self.going_in_dir[DIR_LEFT]:
			self.moveLeft()
		elif self.going_in_dir[DIR_RIGHT]:
			self.moveRight()
		
		# check movement during this update cycle and update angle appropriately
		newAngle = None
		if self.startMapCenter != self.mapCenter:
			dx = self.startMapCenter[0] - self.mapCenter[0]
			dy = self.startMapCenter[1] - self.mapCenter[1]
			#print "DEBUG: Shape.update(): self.startMapCenter={0}, mapCenter={1}, dx={2}, dy={3}".format(self.startMapCenter, self.mapCenter, dx, dy)
			GRAPHIC_BASE_ANGLE = 90
			if(dx == 0):
				if(dy > 0): newAngle = GRAPHIC_BASE_ANGLE
				else: newAngle = 180+GRAPHIC_BASE_ANGLE
			elif(dy == 0):
				if(dx > 0): newAngle = 90+GRAPHIC_BASE_ANGLE
				else: newAngle = 270+GRAPHIC_BASE_ANGLE
			else:
				# Tangent: tan(theta) = Opposite / Adjacent
				theta = math.atan(float(dy)/float(dx))
				# 2*pi rad = 360 deg
				deg = theta * 180 / math.pi
				newDeg = int(deg+GRAPHIC_BASE_ANGLE)
				#print "DEBUG: Shape.update(): self.theta={0}, deg={1}".format(theta, newDeg)
				if(dy < 0):
					newDeg += 180
				newAngle = newDeg
		
		# set starting mapCenter for the top of the next update cycle
		self.startMapCenter = list(self.mapCenter)
		
		if newAngle != None:
			self.setAngle(newAngle)	# should happen after the object position is updated for movement so that collision detection test is accurate


		# check for and update sprite animations
		if effect.BURST_EFFECT in self.effects.keys():
			if not self.effects[effect.BURST_EFFECT].update(t):
				del self.effects[effect.BURST_EFFECT]	# FIXME: is more explicit garbage collection needed here?
			self.makeSprite()
	

	def updatePosition(self):
		self.imageCenter = list(self.mapCenter)
		if self.mapCenter[0] < self.displaySize[0]/2:
			self.imageCenter[0] = self.mapCenter[0]
		elif self.mapCenter[0] > self.map.mapSize[0]-self.displaySize[0]/2:
			self.imageCenter[0] = self.displaySize[0] - (self.map.mapSize[0]-self.mapCenter[0])
		else: 
			self.imageCenter[0] = self.displaySize[0]/2

		if self.mapCenter[1] < self.displaySize[1]/2:
			self.imageCenter[1] = self.mapCenter[1]
		elif self.mapCenter[1] > self.map.mapSize[1]-self.displaySize[1]/2:
			self.imageCenter[1] = self.displaySize[1] - (self.map.mapSize[1]-self.mapCenter[1])
		else: 
			self.imageCenter[1] = self.displaySize[1]/2
		
		self.rect.top = self.imageCenter[1]
		self.rect.left = self.imageCenter[0]
		#print "DEBUG: Shape.updatePosition(): rect is: {0}".format(self.rect)

	def draw(self, display):
		#print "DEBUG: drawing image at {0}".format(self.imageCenter)
		display.blit(self.image, self.imageCenter)
	# end of Shape.draw()



	def receiveSwirl(self, swirl):
		#TODO: prevent duplicate swirls
		self.swirls.append(swirl)
		self.curSwirl = len(self.swirls) - 1	# change current to the new one
		logging.debug("got a new swirl effect type {0}, total {1} swirls now".format(swirl.effect_type, len(self.swirls)))
	
	def activateSwirl(self):
		# checks to make sure we do have at least one swirl
		if self.curSwirl == None or len(self.swirls) == 0: return False
		self.swirls[self.curSwirl].activate(self)
		return True
	
	
	def tryAsk(self):
		logging.debug("tryAsk")
		#TODO
		self.sound.play('ask')
		
	def tryGive(self):
		logging.debug("tryGive")
		self.activateSwirl()
		#TODO
		self.sound.play('give')

	def trySwirlRight(self):
		logging.debug("trySwirlRight")
		#TODO
		pass
	
	def trySwirlLeft(self):
		logging.debug("trySwirlLeft")
		#TODO
		pass
	

	def touchArt(self, art):
		#logging.debug("shape #{0} is touching art #{1}".format(self.id, art.id))
		frames = pacglobal.get_frames()
		# check the last time we touched this art
		if art.id in self.last_touched_art.keys():
			last_touched = self.last_touched_art[art.id]
			self.last_touched_art[art.id] = frames
			#logging.debug("art was touched at {0}, now={1}, last move at {2}".format(last_touched, frames, self.last_moved_frame))
			if self.last_moved_frame == last_touched:
				#logging.debug("still mid-touch")
				return False
			if last_touched <= frames - 1 and last_touched + ART_TOUCH_JITTER > frames: 
				logging.debug("art was touched too recentely - at {0}".format(last_touched))
				return False
		else:
			self.last_touched_art[art.id] = frames
		# trigger the art-touch event!
		logging.debug("shape #{0} is touching art #{1} - triggering event!".format(self.id, art.id))
		art.startEffect(effect.TRANSFER_EFFECT, self)
		#TODO: wait to receive the swirl until the transfer effect is done (pass via a callback function maybe?)
		self.receiveSwirl(Swirl(effect.BURST_EFFECT))	#FIXME: the effect.BURST_EFFECT should come from the art somewhere


	def move(self, dx, dy):
		# Move each axis separately. Note that this checks for collisions both times.
		movedx = movedy = False
		if dx != 0:
			movedx = self.move_single_axis(dx, 0)
		if dy != 0:
			movedy = self.move_single_axis(0, dy)
		if movedx or movedy:
			# check for other map effects that happen based on movement
			self.map.checkTriggers(self)
		self.last_moved_frame = pacglobal.get_frames()

	def move_single_axis(self, dx, dy):
		# save initial positions
		startpos = list(self.mapCenter)
		# Move the rect
		#logging.debug("Shape.move_single_axis({0}, {1})".format(dx, dy))
		self.mapCenter[0] += int(dx)
		self.mapCenter[1] += int(dy)
		# if there's a collision, un-do the move
		if self.map.wallCollision(self):
			#logging.debug("move aborted due to collision")
			self.mapCenter = startpos
			return False
		else:
			#logging.debug("shape moved to %s from %s", self.mapCenter, startpos)
			self.updatePosition()
			return True
	
	def moveUp(self):
		self.move(0, -self.linearSpeed)

	def moveDown(self):
		self.move(0, self.linearSpeed)
	
	def moveLeft(self):
		self.move(-self.linearSpeed, 0)

	def moveRight(self):
		self.move(self.linearSpeed, 0)
	
	def startMove(self, direction):
		self.going_in_dir[direction] = True
	
	def stopMove(self, direction):
		self.going_in_dir[direction] = False
	
	def moveFwd(self):
		# Move in the direction we're pointing
		theta = 2 * math.pi * ((float(self.angle)+90)%360 / 360)
		dy = math.cos(theta)
		dx = math.sin(theta)
		#print "DEBUG: angle={0}, dx={1}, dy={2}".format(theta, dx, dy)
		#print "DEBUG: Shape.moveFwd(): old mapCenter={0}".format(self.mapCenter)
		self.move(dx * self.linearSpeed, dy * self.linearSpeed)
		#print "DEBUG: Shape.moveFwd(): new mapCenter={0}".format(self.mapCenter)

	def moveBack(self):
		# Move away from the direction we're pointing
		theta = 2 * math.pi * ((float(self.angle)+90)%360 / 360)
		dy = math.cos(theta)
		dx = math.sin(theta)
		self.move(dx * -self.linearSpeed, dy * -self.linearSpeed)

	def sizeUp(self):
		logging.debug("old size="+str(self.side_length))
		self.side_length *= 1.1
		if self.side_length > SIZE_MAXIMUM:
			self.side_length = SIZE_MAXIMUM
		self.setSpeed()
		logging.debug("new size="+str(self.side_length))
		self.makeSprite()

	def sizeDown(self):
		logging.debug ("old size="+str(self.side_length))
		self.side_length *= 0.9
		if(self.side_length < SIZE_MINIMUM):
			self.side_length = SIZE_MINIMUM
		self.setSpeed()
		logging.debug ("new size="+str(self.side_length))
		self.makeSprite()
	
	def setAngle(self, angle):
		startAngle = self.angle
		# update the angle
		self.angle = angle
		# check for wrap-around
		if(self.angle < 0): self.angle = 360 + self.angle
		if(self.angle >= 360): self.angle = 360 - self.angle
		#print "DEBUG: angle is now {0}".format(self.angle)
		
		# if there's a collision, un-do the rotation
		#if hasattr(self, 'map') and self.map.wallCollision(self):
		# remake the sprite for the collision test
		self.makeSprite()
		if self.map.wallCollision(self):
			#logging.debug ("rotation cancelled due to collision. angle left at {0}".format(self.angle))
			self.angle = startAngle
			self.makeSprite()
			return False
		else:
			# re-create the sprite in the new position
			#logging.debug ("new angle: {0}".format(self.angle))
			self.makeSprite()
			return True
		
		
	def changeAngle(self, delta):
		""" angle in degrees. 0 is (12 noon?) """
		return self.setAngle(self.angle + delta)
		

	def rotateLeft(self):
		self.changeAngle(self.rotationSpeed)
		
	def rotateRight(self):
		self.changeAngle(-self.rotationSpeed)
		
	def lessSides(self):
		self.num_sides -= 1
		if(self.num_sides == 0): self.num_sides = 1
		logging.debug ("num_sides is now {0}".format(self.num_sides))
		self.makeSprite()
	
	def moreSides(self):
		self.num_sides += 1
		if(self.num_sides > MAX_SIDES+1): self.num_sides = MAX_SIDES+1
		logging.debug ("num_sides is now {0}".format(self.num_sides))
		self.makeSprite()



class ShapeTest:

	def __init__(self):

		# Make the display size a member of the class
		self.displaySize = (640, 480)
		
		# Initialize pygame
		pygame.init()

		# Create a clock to manage time
		self.clock = pygame.time.Clock()

		# Set the window title
		display.set_caption("Shape Test")

		# Create the window
		self.display = display.set_mode(self.displaySize)
		
		self.shape = Shape(self.displaySize, None, self.displaySize[0] / 10, 3)
		self.sprites = sprite.Group(self.shape)
		
	def run(self):
		# Runs the game loop

		while True:
			# The code here runs when every frame is drawn
			#print "looping"

			# Handle Events
			self.handleEvents()

			# Update and draw the sprites
			self.sprites.update(pygame.time.get_ticks())
			self.sprites.draw(self.display)

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

			if event.type == KEYDOWN:
				# Find which key was pressed and start moving appropriate bat
				if event.key == K_ESCAPE:
					pygame.quit()
					sys.exit()
				#elif event.key == K_w:
				elif event.key == K_DOWN:
					self.shape.lessSides()
				elif event.key == K_UP:
					self.shape.moreSides()
				elif event.key == K_LEFT:
					self.shape.rotateLeft()
				elif event.key == K_RIGHT:
					self.shape.rotateRight()
				elif event.key == K_SPACE:
					self.display.fill(colors.BLACK)
				elif event.key == K_a:
					self.shape.colorUp()
				elif event.key == K_z:
					self.shape.colorDn()

			#if event.type == KEYUP:
				#if event.key == K_s or event.key == K_w:
				#	self.player1Bat.stopMove()
				#elif event.key == K_DOWN or event.key == K_UP:
				#	self.player2Bat.stopMove()



if __name__ == '__main__':
	game = ShapeTest()
	game.run()
