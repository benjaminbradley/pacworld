#import sys
#import pygame
#from pygame import *
import logging

#import wall
#from wall import Wall
#import colors
#import world
#from effect import *	# Effect, EFFECT_*

# The class for the player
class Player():
	
	def __init__(self): #, mapSize, displaySize, theworld): , map ?
		self.shape = None

	def selectShape(self, shape):
			if self.shape != None:
				self.shape.autonomous = True	# make the old shape autonomous again
			# 
			self.shape = shape
			self.shape.autonomous = False	# the player shape
