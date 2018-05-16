
import logging
from math import pi
import sys
from pygame import Surface, RLEACCEL


import pacdefs
import colors
import effect
from FrameAnimation import FrameAnimation
sys.path.append('art')
from DrawSpiral import DrawSpiral
from FractalTree import DrawFractalTree
from Mandala import DrawMandala


# initialize a rendered animation for all art styles
rendered_art = {} # hash of style => ArtRenderer
def renderArt(side_length):
  for style in pacdefs.STYLES:
    rendered_art[style] = ArtRenderer(style, side_length)
    logging.debug("Rendered art style {} with {} frames.".format(style, rendered_art[style].getAnimation().getNumFrames()))

def getRenderedArt(style):
  if style not in rendered_art.keys():
    logging.error("Art style {} has not been pre-rendered.".format(style))
    return None
  return rendered_art[style]


#example art: a fractal tree which grows and withers
#example art: a spiral which rotates
#example art: an animated mandala

FRACTALTREE_branch_ratio = 1.5
FRACTALTREE_base_angle = -90
FRACTALTREE_steps = 8
FRACTALTREE_maxd_beg = 2
FRACTALTREE_maxd_end = 8
FRACTALTREE_spread_beg = 12
FRACTALTREE_spread_end = 30
FRACTALTREE_color = (128, 255, 128)

class ArtRenderer(object):

  def __init__(self, style, side_length):
    self.style = style
    self.side_length = side_length
    self.cycle_complete = False
    #initialize state variables
    if self.style == pacdefs.STYLE_SPIRAL:
      self.spiral_minRad = 3
      self.spiral_maxRad = self.spiral_curRad = int(float(self.side_length) / 2)
      self.spiral_curRot = pi
      self.spiral_startAngle = 0.0
      self.spiral_radStep = 2.0
      self.sprial_rotChg = 0.1
    elif self.style == pacdefs.STYLE_TREE:
      # initialize state vars for tree animation
      self.fractaltree_maxd = FRACTALTREE_maxd_beg
      self.fractaltree_spread = FRACTALTREE_spread_beg
      self.fractaltree_maxd_chgdir = 1
      self.fractaltree_spread_chgdir = 1
      self.fractaltree_pause = 0
    elif self.style == pacdefs.STYLE_MANDALA:
      self.mandala_angle = 0
      self.mandala_inner_radius_ratio_chg = 0.03
      self.mandala_inner_radius_ratio_max = 0.6
      self.mandala_inner_radius_ratio_min = 0.2
      self.mandala_inner_radius_ratio = self.mandala_inner_radius_ratio_min
      inner_radius_percent = (self.mandala_inner_radius_ratio - self.mandala_inner_radius_ratio_min) / (self.mandala_inner_radius_ratio_max - self.mandala_inner_radius_ratio_min)
      self.mandala_inner_radius_ratio2 = self.mandala_inner_radius_ratio + (0.3 - 0.2 * inner_radius_percent)
      self.mandala_wait = 0
    
    #generate all frames
    self.animation = FrameAnimation()
    while not self.cycle_complete:
      image = self.renderFrame()
      # store frame in animation
      self.animation.addFrame(image)
      # move onto next...
      remakeSprite = self.update()
      #TODO: figure out how to handle remakeSprite == false - maybe something like RLE ?


  def renderFrame(self):
    # Create an image for the sprite
    image = Surface((self.side_length, self.side_length))
    image.fill(colors.BLACK)
    image.set_colorkey(colors.BLACK, RLEACCEL)  # set the background to transparent
    
    # draw the base sprite, in it's current state
    half = int(self.side_length/2)
    if self.style == pacdefs.STYLE_TREE:
      DrawFractalTree(image, (half, self.side_length), FRACTALTREE_base_angle, self.fractaltree_maxd, self.fractaltree_spread, FRACTALTREE_branch_ratio, FRACTALTREE_color)
    elif self.style == pacdefs.STYLE_SPIRAL:
      DrawSpiral(image, [self.spiral_maxRad,self.spiral_maxRad], self.spiral_curRad, self.spiral_curRot, 3, True, self.spiral_startAngle)
    elif self.style == pacdefs.STYLE_MANDALA:
      DrawMandala(image, (half, half), (255,128,128), half, self.mandala_angle, 12, self.mandala_inner_radius_ratio, self.mandala_inner_radius_ratio2)
      #DrawMandala(image, (half, half), (255,128,128), half, 0, 12, self.mandala_inner_radius_ratio, self.mandala_inner_radius_ratio2)
    
    return image


  def update(self):
    remakeSprite = False
    # animate base sprite
    if self.style == pacdefs.STYLE_SPIRAL:
      self.spiral_curRad += self.spiral_radStep
      if self.spiral_curRad <= self.spiral_minRad or self.spiral_curRad >= self.spiral_maxRad: self.spiral_radStep = -self.spiral_radStep
      self.spiral_curRot += self.sprial_rotChg
      self.spiral_startAngle -= 0.05
      remakeSprite = True
      if(self.spiral_curRot >= 85): self.sprial_rotChg *= -1
      if(self.sprial_rotChg < 0 and self.spiral_curRot <= pi): self.cycle_complete = True
    elif self.style == pacdefs.STYLE_TREE:
      if self.fractaltree_pause > 0:
        self.fractaltree_pause -= 1
      elif(self.fractaltree_maxd < FRACTALTREE_maxd_beg and self.fractaltree_pause == 0):
          self.cycle_complete = True
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
    elif self.style == pacdefs.STYLE_MANDALA:
      # spin it around
      self.mandala_angle -= 1.782   # takes 101 loops to complete the grow/shrink cycle, so 180/101 = 1.782
      if self.mandala_angle <= -180: self.cycle_complete = True
      elif self.mandala_angle == -360: self.mandala_angle = 0
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
    
    return remakeSprite


  def getAnimation(self):
    return self.animation




if __name__ == '__main__':  # Begin test code
  logging.basicConfig(format='%(asctime)-15s:%(levelname)s:%(filename)s#%(funcName)s(): %(message)s', level=logging.DEBUG)
  import pygame
  screen_width = 800
  screen_height = 600
  screen = pygame.display.set_mode((screen_width, screen_height))
  pygame.display.set_caption("Art Renderer")

  renderArt(screen_height / 6)
  
  while True:
    for event in pygame.event.get():
      if event.type == pygame.QUIT or event.type == pygame.KEYDOWN:
        sys.exit()

    screen.fill((0, 0, 0))
    art_width = screen_width / len(pacdefs.STYLES)
    art_y = screen_height / 2
    for i,style in enumerate(pacdefs.STYLES):
      animation = rendered_art[style].getAnimation()
      image = animation.getCurrentFrame()
      art_x = int(art_width * (i + 0.5))
      screen.blit(image, (art_x, art_y))
      animation.nextFrame()
    
    pygame.time.Clock().tick(30)
    pygame.display.update()
