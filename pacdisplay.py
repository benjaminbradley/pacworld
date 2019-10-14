import logging
import pygame

pacdisplay_instance = None
'''
def getPacdisplay():
  global pacdisplay_instance
  if not pacdisplay_instance:
    pacdisplay_instance = Pacdisplay()
  return pacdisplay_instance
'''

# The class for the sound system
class Pacdisplay(object):
  def __init__(self, displaySize):
    self.displaySize = displaySize

  def getDisplaySize(self):
    return self.displaySize

  def setDisplaySize(self, displaySize):
    self.displaySize = displaySize

  def draw_text_centered(self, surface, text, centery):
    logging.debug("***** {}".format(text))
    font = pygame.font.Font(None, 24)
    textBitmap = font.render(text, True, (255,0,0))
    textWidth = textBitmap.get_rect().width
    centerx = int(self.displaySize[0]/2)
    topLeft = [centerx - int(textWidth/2), centery]
    pygame.draw.rect(surface, (0,0,0), pygame.Rect(centerx-200, centery, 400, 30))
    surface.blit(textBitmap, topLeft)
    pygame.display.update()