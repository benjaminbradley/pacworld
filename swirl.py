import pygame
from pygame import *
import logging

from effect import Effect
import colors

class Swirl(sprite.Sprite):
	
	def __init__(self, effect_type):
		# Initialize the sprite base class
		super(Swirl, self).__init__()
		
		self.effect_type = effect_type
	
	def activate(self, shape):
		shape.effects[self.effect_type] = Effect(self.effect_type, None)
		shape.makeSprite()

