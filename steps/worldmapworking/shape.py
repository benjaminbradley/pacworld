import pygame # Provides what we need to make a game
import sys # Gives us the sys.exit function to close our program
import math	# sin,cos,pi

from pygame.locals import *
from pygame import *

BLACK = (0,0,0)
MAX_SIDES = 10
SIZE_MINIMUM = 5
SIZE_MAXIMUM = 140

# The class for Shapes
class Shape(sprite.Sprite):
	
	def __init__(self, displaySize, num_sides = 3):
		# Initialize the sprite base class
		super(Shape, self).__init__()
		
		# Get the display size for working out collisions later
		self.displaySize = displaySize
		
		self.color = (0,0,255)
		self.eye_color = (0,255,0)
		
		# Get a radius value proportionate to the display size
		self.side_length = self.displaySize[0] / 10
		self.num_sides = num_sides
		self.outlineWidth = 2
		self.angle = 0

		# Work out a speed
		self.setSpeed()

		# create the image for the shape
		self.makeSprite()
			
		# Reset the shape
		self.reset()
	
	def setSpeed(self):
		self.linearSpeed = int(self.side_length / 8)
		self.rotationSpeed = self.linearSpeed
		print "DEBUG: linearSpeed is now {0}".format(self.linearSpeed)
	
	def makeSprite(self):
		# Create an image for the sprite
		self.image = Surface((self.side_length, self.side_length))
		self.image.fill(BLACK)
		self.image.set_colorkey(BLACK, RLEACCEL)	# set the background to transparent
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
		
		# draw the "eye" direction indicator
		radius = self.outlineWidth + self.outlineWidth
		center = int(float(self.side_length) / 2)
		pygame.draw.circle(self.image, self.eye_color, (self.side_length-radius, center), radius, self.outlineWidth)
		
		
		# rotate image, if applicable
		if(self.angle != 0):
			self.image = pygame.transform.rotate(self.image, self.angle)

		
		# Create the sprites rectangle from the image
		self.rect = self.image.get_rect()
		
		# create a mask for the sprite (for collision detection)
		self.mask = pygame.mask.from_surface(self.image)
	
	def reset(self):
		# Start the shape directly in the centre of the screen
		self.mapCenter = [self.displaySize[0] / 2, self.displaySize[1] / 2]
		# reset other attributes as well
		self.angle = 0
		self.makeSprite()

	def update(self, t):
		pass

	def draw(self, display):
		imageCenter = list(self.mapCenter)
		if self.mapCenter[0] < self.bg.displaySize[0]/2:
			imageCenter[0] = self.mapCenter[0]
		elif self.mapCenter[0] > self.bg.mapSize[0]-self.bg.displaySize[0]/2:
			imageCenter[0] = self.bg.displaySize[0] - (self.bg.mapSize[0]-self.mapCenter[0])
		else: 
			imageCenter[0] = self.bg.displaySize[0]/2

		if self.mapCenter[1] < self.bg.displaySize[1]/2:
			imageCenter[1] = self.mapCenter[1]
		elif self.mapCenter[1] > self.bg.mapSize[1]-self.bg.displaySize[1]/2:
			imageCenter[1] = self.bg.displaySize[1] - (self.bg.mapSize[1]-self.mapCenter[1])
		else: 
			imageCenter[1] = self.bg.displaySize[1]/2

		#print "DEBUG: drawing image at {0}".format(imageCenter)
		display.blit(self.image, imageCenter)

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
		if self.bg.wallCollision(self):
			self.mapCenter = startpos
	
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

	def changeAngle(self, delta):
		startAngle = self.angle
		# update the angle
		self.angle += delta
		# check for wrap-around
		if(self.angle < 0): self.angle = 360 + self.angle
		if(self.angle >= 360): self.angle = 360 - self.angle
		#print "DEBUG: angle is now {0}".format(self.angle)
		# re-create the sprite in the new position
		self.makeSprite()
		
		# if there's a collision, un-do the rotation
		if self.bg.wallCollision(self):
			self.angle = startAngle
			self.makeSprite()
		

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
		
		self.shape = Shape(self.displaySize, 3)
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

			#if event.type == KEYUP:
				#if event.key == K_s or event.key == K_w:
				#	self.player1Bat.stopMove()
				#elif event.key == K_DOWN or event.key == K_UP:
				#	self.player2Bat.stopMove()



if __name__ == '__main__':
	game = ShapeTest()
	game.run()
