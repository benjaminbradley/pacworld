import sys
import random
import pygame
from pygame import *
import logging

sys.path.append('art')
import ArtRenderer

import pacdefs
from pacsprite import Pacsprite
import colors
import effect
from effect import *  # Effect, EFFECT_*
from swirl import *


BURST_FREQUENCY = 3000

class Art(Pacsprite):
  def __init__(self, themap, left, top, style = None):
    # Initialize the sprite base class
    super(Art, self).__init__()
    # initialize art variables
    self.map = themap
    self.side_length = themap.character_size
    self.width = self.side_length
    self.height = self.side_length
    self.type = pacdefs.TYPE_ART
    self.symbol = pacdefs.ART_SYMBOL
    self.doors = {}  # dictionary of side(int) to (X,Y) tuple of ints
    self.effects = {}  # dictionary of Effect.EFFECT_TYPE to Effect class
    self.angle = 0
    self.color = colors.PINK2
    self.style = style
    if self.style is None:
      self.style = random.choice(pacdefs.STYLES)
    self.jitter = pygame.time.get_ticks() + random.randint(0, BURST_FREQUENCY)
    #print "DEBUG: Art.__init__(): jitter={0}".format(self.jitter)
    
    # get animation for the art
    self.art_animation = ArtRenderer.getRenderedArt(style).getAnimation()
    # start this art instance on a random frame to add variety
    self.art_animation_current_frame = random.randint(0, self.art_animation.getNumFrames()-1)

    if self.style == pacdefs.STYLE_SPIRAL:
      self.effect_type = effect.SPIRAL_EFFECT
      self.animation_framerate = 1
    elif self.style == pacdefs.STYLE_TREE:
      self.effect_type = effect.TREE_EFFECT
      self.animation_framerate = 1
    elif self.style == pacdefs.STYLE_MANDALA:
      self.effect_type = effect.BURST_EFFECT
      self.animation_framerate = 2
    self.animation_framerate_counter = 0
    
    # make & capture the initial image for the art
    self.makeSprite()
    
    self.setPos(left,top)
    
    # aspects particular to this type of art
    self.burstFrequency = BURST_FREQUENCY  # pull this from somewhere ?
    self.lastBurst = 0


  def setPos(self, left, top):
    self.top = top
    self.left = left
    # calculated variables
    # x,y is the art piece's location on the map (left,top corner)
    xmargin = int((self.map.grid_cellwidth - self.rect.width ) / 2)
    ymargin = int((self.map.grid_cellheight - self.rect.height ) / 2)
    self.x = self.left * self.map.grid_cellwidth + xmargin
    self.y = self.top * self.map.grid_cellheight + ymargin
    #self.rect.top = (self.top - 0.5 )* self.map.grid_cellheight
    #self.rect.left = (self.left - 0.5) * self.map.grid_cellwidth
    self.rect.left = self.x
    self.rect.top = self.y


  def __str__(self):
    if self.style == pacdefs.STYLE_TREE: stylestr = 'tr'
    elif self.style == pacdefs.STYLE_SPIRAL: stylestr = 'sp'
    elif self.style == pacdefs.STYLE_MANDALA: stylestr = 'ma'
    return '<Art #'+str(self.id)+'['+stylestr+']>'


  def debug(self, msg):
    if hasattr(self, 'id'): the_id = self.id
    else: the_id = '-'
    logging.debug("Art[{0}]:{1}".format(the_id, msg))


  def makeSprite(self):
    # get next frame of the animation
    self.image = self.art_animation.getFrame(self.art_animation_current_frame).copy()
    
    for effect in self.effects.values():
      effect.draw(self.image)
    
    # rotate image, if applicable
    if(self.angle != 0):
      self.image = pygame.transform.rotate(self.image, self.angle)

    # add DEBUG info if enabled
    if pacdefs.DEBUG_ART_SHOWID and hasattr(self, 'id'):
      font = pygame.font.Font(None, 26)
      textBitmap = font.render(str(self.id), True, colors.PINK)
      self.image.blit(textBitmap, (int(self.image.get_width()/2), int(self.image.get_height()/2)))

    # Create the sprites rectangle from the image, maintaining rect position if set
    oldrectpos = None
    if hasattr(self, 'rect'):
      oldrectpos = self.rect.center
    self.rect = self.image.get_rect()
    if oldrectpos:
      self.rect.center = oldrectpos

    # create a mask for the sprite (for collision detection)
    self.mask = pygame.mask.from_surface(self.image)
  
  
  def startEffect(self, effect_type, effect_options):
    # initialize effect variables
    #logging.debug("starting new effect, type: {0}".format(effect_type))
    self.effects[effect_type] = Effect(effect_type, effect_options)
    self.makeSprite()
  
  
  def getSwirl(self):
    # return the type of swirl that this art gives
    if self.style == pacdefs.STYLE_TREE: swirl_type = LOOK_LT
    elif self.style == pacdefs.STYLE_SPIRAL: swirl_type = LOOK_LINE
    elif self.style == pacdefs.STYLE_MANDALA: swirl_type = LOOK_CIRCLE
    else:
      logging.error("Unhandled Art Style in Art.getSwirl(): {}".format(self.style))
      swirl_type = None # pick one randomly
    return Swirl(swirl_type, self.effect_type)


  def update(self, t):
    remakeSprite = False
    # check for periodic effects to start
    if self.lastBurst + self.burstFrequency < t and self.jitter < t:
      self.lastBurst = t
      #logging.debug ("Art.update(): triggering burst for art #{0} starting at {1}".format(self.id, t))
      windowRect = self.map.player.shape.getWindowRect()
      if self.onScreen(windowRect): soundvolume = pacdefs.ONSCREEN_SOUND_PERCENT
      elif self.nearScreen(windowRect): soundvolume = pacdefs.NEARBY_SOUND_PERCENT
      else: soundvolume = 0
      self.startEffect(self.effect_type, {EFFECT_VOLUME: soundvolume})
    
    self.animation_framerate_counter += 1
    if(self.animation_framerate_counter >= self.animation_framerate):
      self.art_animation_current_frame = self.art_animation.getNextFrame(self.art_animation_current_frame)
      self.animation_framerate_counter = 0
    remakeSprite = True #TODO: set this based on nextFrame() / artRenderer.update()
    
    # check for current effects to continue
    completed_effects = []
    for effect_type in self.effects.keys():
      if self.effects[effect_type].update(t):
        remakeSprite = True
      else:
        completed_effects.append(effect_type)
        remakeSprite = True
    # clean up completed effects
    for effect_type in completed_effects:
      del self.effects[effect_type]  # FIXME: is more explicit garbage collection needed here?
    
    if remakeSprite: self.makeSprite()
  
  
  def draw(self, display, windowRect):
    #TODO: adjust blit dest by mapTopLeft
    screenpos = (self.x - windowRect[0], self.y - windowRect[1])
    #print "DEBUG: Art.draw(): drawing image at {0}".format(screenpos)
    display.blit(self.image, screenpos)
  # end of Art.draw()

  
  def getCenter(self):
    return self.rect.center


  def getMapTopLeft(self):
    """returns an (x,y) tuple for the top-left of this art on the map"""
    return (self.left * self.map.grid_cellwidth, self.top * self.map.grid_cellheight)
