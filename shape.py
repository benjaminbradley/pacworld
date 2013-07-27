import pygame # Provides what we need to make a game
import sys # Gives us the sys.exit function to close our program
import math	# sin,cos,pi

from pygame.locals import *
from pygame import *

import pacsounds
import colors

MAX_SIDES = 10
SIZE_MINIMUM = 5
SIZE_MAXIMUM = 140
DIR_UP = 'u'
DIR_DOWN = 'd'
DIR_LEFT = 'l'
DIR_RIGHT = 'r'
DIRECTIONS = [DIR_UP, DIR_DOWN, DIR_LEFT, DIR_RIGHT]

BURST_EFFECT_NUMFRAMES = 6

# The class for Shapes
class Shape(sprite.Sprite):
	
	def __init__(self, displaySize, themap, shape_size, num_sides = 3):
		# Initialize the sprite base class
		super(Shape, self).__init__()
		
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
		self.in_burstEffect = False

		# Reset the shape & create the first image
		self.reset()
		
		# placeholder variables for subsystems
		self.sound = None
	
	def setColor(self):
		self.color = colors.COLORWHEEL[self.colorIdx]
		self.eye_color = colors.YELLOW
	
	def colorUp(self):
		print "DEBUG: Shape.colorUp()"
		self.colorIdx += 1
		if(self.colorIdx >= len(colors.COLORWHEEL)):
			self.colorIdx = 0
		self.setColor()
		self.makeSprite()

	def colorDn(self):
		print "DEBUG: Shape.colorDn()"
		self.colorIdx -= 1
		if(self.colorIdx < 0):
			self.colorIdx = len(colors.COLORWHEEL)-1
		self.setColor()
		self.makeSprite()

	def setSpeed(self):
		''' sets the shape's speed based on its size '''
		self.linearSpeed = int(self.side_length / 8)
		self.rotationSpeed = self.linearSpeed
		print "DEBUG: linearSpeed is now {0}".format(self.linearSpeed)
	
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
		if self.in_burstEffect:
			width = 2
			radius = int(self.side_length/2)
			print "DEBUG: Shape.update(): frame={0}, numframe={1}, radius={2}".format(self.burstEffect_frame, self.burstEffect_numframes, radius)
			burst_radius = int(float(self.burstEffect_frame) / float(self.burstEffect_numframes) * radius)
			if width > burst_radius: width = burst_radius
			gradpercent = float(self.burstEffect_frame) / float(self.burstEffect_numframes)
			grad_color = [int(gradpercent*c) for c in colors.NEONBLUE]
			print "DEBUG: Shape.update(): in burstEffect: burst_radius = {0}, gradpercent = {1}, grad_color={2}".format(burst_radius, gradpercent, grad_color)
			pygame.draw.circle(self.image, grad_color, (radius,radius), burst_radius, width)
		
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
		# Start the shape directly in the centre of the screen
		self.mapCenter = [self.displaySize[0] / 2, self.displaySize[1] / 2]
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
		if self.startMapCenter != self.mapCenter:
			dx = self.startMapCenter[0] - self.mapCenter[0]
			dy = self.startMapCenter[1] - self.mapCenter[1]
			#print "DEBUG: Shape.update(): self.startMapCenter={0}, mapCenter={1}, dx={2}, dy={3}".format(self.startMapCenter, self.mapCenter, dx, dy)
			GRAPHIC_BASE_ANGLE = 90
			if(dx == 0):
				if(dy > 0): self.setAngle(GRAPHIC_BASE_ANGLE)
				else: self.setAngle(180+GRAPHIC_BASE_ANGLE)
			elif(dy == 0):
				if(dx > 0): self.setAngle(90+GRAPHIC_BASE_ANGLE)
				else: self.setAngle(270+GRAPHIC_BASE_ANGLE)
			else:
				# Tangent: tan(theta) = Opposite / Adjacent
				theta = math.atan(float(dy)/float(dx))
				# 2*pi rad = 360 deg
				deg = theta * 180 / math.pi
				newDeg = int(deg+GRAPHIC_BASE_ANGLE)
				#print "DEBUG: Shape.update(): self.theta={0}, deg={1}".format(theta, newDeg)
				if(dy < 0):
					newDeg += 180
				self.setAngle(newDeg)

		# set starting mapCenter for the top of the next update cycle
		self.startMapCenter = list(self.mapCenter)

		# check for and update sprite animations
		if self.in_burstEffect:
			#print "DEBUG: Shape.update(): t={0}, lastUpdate={1}, frame={2}".format(t, self.burstEffect_last_update, self.burstEffect_frame)
			if t - self.burstEffect_last_update > self.burstEffect_delay:
				self.burstEffect_frame += 1
				if self.burstEffect_frame >= self.burstEffect_numframes:
					self.in_burstEffect = False	# end the effect, only go through it once
				self.burstEffect_last_update = t
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



	def startBurst(self):
		fps = 10
		# initialize animation timer
		self.in_burstEffect = True
		#self.burstEffect_start = pygame.time.get_ticks()
		self.burstEffect_delay = 1000 / fps
		self.burstEffect_last_update = 0
		self.burstEffect_frame = 0
		self.burstEffect_numframes = BURST_EFFECT_NUMFRAMES
		# play burst sound
		if self.sound != None: self.sound.play('3roboditzfade')


	def move(self, dx, dy):
		# Move each axis separately. Note that this checks for collisions both times.
		if dx != 0:
			self.move_single_axis(dx, 0)
		if dy != 0:
			self.move_single_axis(0, dy)

	def move_single_axis(self, dx, dy):
		# save initial positions
		startpos = list(self.mapCenter)
		# Move the rect
		#print "DEBUG: Shape.move_single_axis({0}, {1})".format(dx, dy)
		self.mapCenter[0] += int(dx)
		self.mapCenter[1] += int(dy)
		# if there's a collision, un-do the move
		if self.map.wallCollision(self):
			self.mapCenter = startpos
		else:
			self.updatePosition()
	
	def moveUp(self):
		"""docstring for moveUp"""
		self.move(0, -self.linearSpeed)

	def moveDown(self):
		"""docstring for moveDown"""
		self.move(0, self.linearSpeed)
	
	def moveLeft(self):
		"""docstring for moveLeft"""
		self.move(-self.linearSpeed, 0)

	def moveRight(self):
		"""docstring for moveRight"""
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
		print "DEBUG: Shape.sizeUp(): old size="+str(self.side_length)
		self.side_length *= 1.1
		if self.side_length > SIZE_MAXIMUM:
			self.side_length = SIZE_MAXIMUM
		self.setSpeed()
		print "DEBUG: Shape.sizeUp(): new size="+str(self.side_length)
		self.makeSprite()

	def sizeDown(self):
		print "DEBUG: Shape.sizeDown(): old size="+str(self.side_length)
		self.side_length *= 0.9
		if(self.side_length < SIZE_MINIMUM):
			self.side_length = SIZE_MINIMUM
		self.setSpeed()
		print "DEBUG: Shape.sizeDown(): new size="+str(self.side_length)
		self.makeSprite()
	
	def setAngle(self, angle):
		"""docstring for setAngle"""
		startAngle = self.angle
		# update the angle
		self.angle = angle
		# check for wrap-around
		if(self.angle < 0): self.angle = 360 + self.angle
		if(self.angle >= 360): self.angle = 360 - self.angle
		#print "DEBUG: angle is now {0}".format(self.angle)
		# re-create the sprite in the new position
		self.makeSprite()
		
		# if there's a collision, un-do the rotation
		if hasattr(self, 'bg') and self.map.wallCollision(self):
			self.angle = startAngle
			self.makeSprite()
			return False
		else:
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
		print "DEBUG: Shape.lessSides(): num_sides is now {0}".format(self.num_sides)
		self.makeSprite()
	
	def moreSides(self):
		self.num_sides += 1
		if(self.num_sides > MAX_SIDES+1): self.num_sides = MAX_SIDES+1
		print "DEBUG: Shape.moreSides(): num_sides is now {0}".format(self.num_sides)
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
				elif event.key == K_m:
					self.shape.startBurst()

			#if event.type == KEYUP:
				#if event.key == K_s or event.key == K_w:
				#	self.player1Bat.stopMove()
				#elif event.key == K_DOWN or event.key == K_UP:
				#	self.player2Bat.stopMove()



if __name__ == '__main__':
	game = ShapeTest()
	game.run()
