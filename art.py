import sys
import random
import pygame
from pygame import *
import logging
from math import pi

sys.path.append('art')
from DrawSpiral import DrawSpiral
from FractalTree import DrawFractalTree
from Mandala import DrawMandala

import pacdefs
from pacsprite import Pacsprite
import colors
import effect
from effect import *  # Effect, EFFECT_*
from swirl import *


STYLE_TREE = 0
STYLE_SPIRAL = 1
STYLE_MANDALA = 2
STYLES = [STYLE_TREE, STYLE_SPIRAL, STYLE_MANDALA]

BURST_FREQUENCY = 3000

FRACTALTREE_branch_ratio = 1.5
FRACTALTREE_base_angle = -90
FRACTALTREE_steps = 8
FRACTALTREE_maxd_beg = 2
FRACTALTREE_maxd_end = 8
FRACTALTREE_spread_beg = 12
FRACTALTREE_spread_end = 30
FRANTALTREE_color = (128, 255, 128)

#example art: a fractal tree which grows and withers
#example art: a spiral which rotates
#example art: an animated mandala

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
      self.style = random.choice(STYLES)
    self.jitter = pygame.time.get_ticks() + random.randint(0, BURST_FREQUENCY)
    #print "DEBUG: Art.__init__(): jitter={0}".format(self.jitter)
    
    if self.style == STYLE_SPIRAL:
      self.spiral_minRad = 3
      self.spiral_maxRad = self.spiral_curRad = int(float(self.side_length) / 2)
      self.spiral_curRot = pi
      self.spiral_startAngle = 0.0
      self.spiral_radStep = 2.0
    elif self.style == STYLE_TREE:
      # initialize state vars for tree animation
      self.fractaltree_maxd = FRACTALTREE_maxd_beg
      self.fractaltree_spread = FRACTALTREE_spread_beg
      self.fractaltree_maxd_chgdir = 1
      self.fractaltree_spread_chgdir = 1
      self.fractaltree_pause = 0
    elif self.style == STYLE_MANDALA:
      self.mandala_angle = 0
      self.mandala_inner_radius_ratio_chg = 0.03
      self.mandala_inner_radius_ratio_max = 0.6
      self.mandala_inner_radius_ratio_min = 0.2
      self.mandala_inner_radius_ratio = self.mandala_inner_radius_ratio_min
      self.mandala_inner_radius_ratio2 = self.mandala_inner_radius_ratio + 0.2
      self.mandala_wait = 0

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
    if self.style == STYLE_TREE: stylestr = 'tr'
    elif self.style == STYLE_SPIRAL: stylestr = 'sp'
    elif self.style == STYLE_MANDALA: stylestr = 'ma'
    return '<Art #'+str(self.id)+'['+stylestr+']>'

  def debug(self, msg):
    if hasattr(self, 'id'): the_id = self.id
    else: the_id = '-'
    logging.debug("Art[{0}]:{1}".format(the_id, msg))

  def makeSprite(self):
    # Create an image for the sprite
    self.image = Surface((self.side_length, self.side_length))
    self.image.fill(colors.BLACK)
    self.image.set_colorkey(colors.BLACK, RLEACCEL)  # set the background to transparent
    
    # draw the base sprite, in it's current state
    half = int(self.side_length/2)
    if self.style == STYLE_TREE:
      DrawFractalTree(self.image, (half, self.side_length), FRACTALTREE_base_angle, self.fractaltree_maxd, self.fractaltree_spread, FRACTALTREE_branch_ratio, FRANTALTREE_color)
    elif self.style == STYLE_SPIRAL:
      DrawSpiral(self.image, [self.spiral_maxRad,self.spiral_maxRad], self.spiral_curRad, self.spiral_curRot, 3, True, self.spiral_startAngle)
    elif self.style == STYLE_MANDALA:
      DrawMandala(self.image, (half, half), (255,128,128), half, self.mandala_angle, 12, self.mandala_inner_radius_ratio, self.mandala_inner_radius_ratio2)
      
    
    for effect in self.effects.values():
      effect.draw(self.image)  # TODO: if it's the transfer effect, it should be drawn on the world map, right? where...
    
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
    if self.style == STYLE_TREE: swirl_type = LOOK_LT
    elif self.style == STYLE_SPIRAL: swirl_type = LOOK_LINE
    elif self.style == STYLE_MANDALA: swirl_type = LOOK_CIRCLE
    else:
      logging.error("Unhandled Art Style in Art.getSwirl(): {}".format(self.style))
      swirl_type = None # pick one randomly
    return Swirl(swirl_type)


  def update(self, t):
    remakeSprite = False
    # animate base sprite
    if self.style == STYLE_SPIRAL:
      self.spiral_curRad += self.spiral_radStep
      if self.spiral_curRad <= self.spiral_minRad or self.spiral_curRad >= self.spiral_maxRad: self.spiral_radStep = -self.spiral_radStep
      self.spiral_curRot += 0.1
      self.spiral_startAngle -= 0.05
      remakeSprite = True
    elif self.style == STYLE_TREE:
      if self.fractaltree_pause > 0:
        self.fractaltree_pause -= 1
      else:
        maxdchg = max(1,int((FRACTALTREE_maxd_end - FRACTALTREE_maxd_beg) / FRACTALTREE_steps))
        self.fractaltree_maxd += self.fractaltree_maxd_chgdir * maxdchg
        if(self.fractaltree_maxd > FRACTALTREE_maxd_end):
          self.fractaltree_pause = 1
          self.fractaltree_maxd_chgdir = 0
          spreadchg = max(1,int((FRACTALTREE_spread_end - FRACTALTREE_spread_beg) / FRACTALTREE_steps))
          self.fractaltree_spread += self.fractaltree_spread_chgdir * spreadchg
          if(self.fractaltree_spread > FRACTALTREE_spread_end):
            self.fractaltree_spread_chgdir = -1
            self.fractaltree_pause = 20
          elif(self.fractaltree_spread < FRACTALTREE_spread_beg):
            self.fractaltree_maxd_chgdir = -1
            self.fractaltree_spread_chgdir = 0
        elif(self.fractaltree_maxd < FRACTALTREE_maxd_beg):
          self.fractaltree_maxd_chgdir = 1
          self.fractaltree_spread_chgdir = 1
          self.fractaltree_pause = 20
        remakeSprite = True
    elif self.style == STYLE_MANDALA:
      # spin it around
      self.mandala_angle -= 1
      if self.mandala_angle == 360: self.mandala_angle = 0
      remakeSprite = True
      # timing
      if self.mandala_wait > 0:
        self.mandala_wait -= 1
      else:
        # grow/shrink
        self.mandala_inner_radius_ratio += self.mandala_inner_radius_ratio_chg
        inner_radius_percent = (self.mandala_inner_radius_ratio - self.mandala_inner_radius_ratio_min) / (self.mandala_inner_radius_ratio_max - self.mandala_inner_radius_ratio_min)
        self.mandala_inner_radius_ratio2 = self.mandala_inner_radius_ratio + (0.3 - 0.2 * inner_radius_percent)
        self.mandala_wait = 4*(abs(0.5 - inner_radius_percent) * 2)
        if(self.mandala_inner_radius_ratio_chg > 0 and self.mandala_inner_radius_ratio >= self.mandala_inner_radius_ratio_max):
          self.mandala_inner_radius_ratio_chg *= -1
        elif(self.mandala_inner_radius_ratio_chg < 0 and self.mandala_inner_radius_ratio <= self.mandala_inner_radius_ratio_min):
          self.mandala_inner_radius_ratio_chg *= -1
    
    # check for periodic effects to start
    if self.lastBurst + self.burstFrequency < t and self.jitter < t:
      self.lastBurst = t
      #logging.debug ("Art.update(): triggering burst for art #{0} starting at {1}".format(self.id, t))
      windowRect = self.map.player.shape.getWindowRect()
      if self.onScreen(windowRect): soundvolume = pacdefs.ONSCREEN_SOUND_PERCENT
      elif self.nearScreen(windowRect): soundvolume = pacdefs.NEARBY_SOUND_PERCENT
      else: soundvolume = 0
      self.startEffect(effect.BURST_EFFECT, {EFFECT_VOLUME: soundvolume})
    
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
