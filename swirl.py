import pygame
from pygame import *
import logging
import random

from pacsounds import getPacsound
import effect
from effect import Effect
import colors

LOOK_CIRCLE = 1
LOOK_LINE = 2
LOOK_LT = 3
LOOKS = [LOOK_CIRCLE, LOOK_LINE, LOOK_LT]

class Swirl(sprite.Sprite):
  
  def __init__(self, look_type = None, effect_type = None):
    # Initialize the sprite base class
    super(Swirl, self).__init__()
    self.sound = getPacsound()
    
    if(look_type is None):
      look_type = LOOKS[random.randint(0,len(LOOKS)-1)]
    self.look = look_type
    
    if(effect_type is None):
      if(look_type == LOOK_CIRCLE):
        effect_type = effect.BURST_EFFECT
      elif(look_type == LOOK_LINE):
        effect_type = effect.SPIRAL_EFFECT
      elif(look_type == LOOK_LT):
        effect_type = effect.TREE_EFFECT
    self.effect_type = effect_type
  
  def activate(self, shape, dir_up):
    shape.effects[self.effect_type] = Effect(self.effect_type, {effect.EFFECT_VOLUME: shape.soundProximity()})
    if(self.look == LOOK_LINE):
      if(dir_up): result = shape.moreSides()
      else: result = shape.lessSides()
      if(result): self.sound.play('sideChange', shape.soundProximity())
    elif(self.look == LOOK_CIRCLE):
      if(dir_up): result = shape.sizeUp()
      else: result = shape.sizeDown()
      if(result): self.sound.play('sizeChange', shape.soundProximity())
    elif(self.look == LOOK_LT):
      if(dir_up): result = shape.colorUp()
      else: result = shape.colorDn()
      if(result): self.sound.play('colorChange', shape.soundProximity())
    shape.makeSprite()

  def draw(self, image, position, active = False):
    lineWidth = 1  # default, may be adjusted later
    if active:
      color = colors.PINK2
    else:
      color = colors.WHITE
    if self.look == LOOK_CIRCLE:
      # draw a tiny circle
      radius = 3
      pygame.draw.circle(image, color, position, radius, lineWidth)
    elif self.look == LOOK_LINE:
      # draw a straight line
      length = 4
      start_pos = (position[0] - length/2, position[1])
      end_pos = (position[0] + length/2, position[1])
      lineWidth = 2
      pygame.draw.line(image, color, start_pos, end_pos, lineWidth)
    elif self.look == LOOK_LT:
      # draw an angle
      length = 4
      start1_pos = (position[0] - length/2, position[1]-length)
      start2_pos = (position[0] - length/2, position[1]+length)
      end_pos = (position[0] + length/2, position[1])
      lineWidth = 2
      pygame.draw.line(image, color, start1_pos, end_pos, lineWidth)
      pygame.draw.line(image, color, start2_pos, end_pos, lineWidth)
    else:
      logging.critical("unknown effect look: {0}".format(self.look))

