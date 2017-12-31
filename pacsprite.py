# common attributes/methods shared by all pacworld sprites
import pygame
import logging
import pacglobal

class Pacsprite(pygame.sprite.Sprite):
  # required attributes
  # self.getMapTopLeft()  (x,y)
  # self.rect   Rect
  # self.map    Map

  def __init__(self):
    # Initialize the sprite base class
    super(Pacsprite, self).__init__()
    
    # cache for list of arts currently on screen, should be calculated only once per cycle
    self.onscreen_art_lastupdated = None
    self.onscreen_art = []

  def onScreen(self, windowRect):
    windowRight = windowRect.left + windowRect.width
    windowBottom = windowRect.top + windowRect.height
    # if object is on the screen, we will draw it
    mapTopLeft = self.getMapTopLeft()
    objLeft = mapTopLeft[0]
    objRight = mapTopLeft[0]+self.rect.width
    objTop = mapTopLeft[1]
    objBottom = mapTopLeft[1]+self.rect.height
    if objLeft > windowRight: return False
    if objRight < windowRect.left: return False
    if objBottom < windowRect.top: return False
    if objTop > windowBottom: return False
    return True     # obj IS on the screen

  def nearScreen(self, windowRect):
    """This function checks to see if the object is on or near the currently displayed screen"""
    adjWindowLeft = windowRect.left - windowRect.width
    adjWindowRight = windowRect.left + int(windowRect.width * 1.5)
    adjWindowTop = windowRect.top - windowRect.height
    adjWindowBottom = windowRect.top + int(windowRect.height * 1.5)
    # if object is within this extended window, return true
    mapTopLeft = self.getMapTopLeft()
    objLeft = mapTopLeft[0]
    objRight = mapTopLeft[0]+self.rect.width
    objTop = mapTopLeft[1]
    objBottom = mapTopLeft[1]+self.rect.height
    if objLeft < adjWindowLeft: return False
    if objTop < adjWindowTop: return False
    if objRight > adjWindowRight: return False
    if objBottom > adjWindowBottom: return False
    return True     # sprite IS near the screen

  def getWindowRect(self):
    """get the rect for the display window containing the center point"""
    center = self.getMapTopLeft()
    windowLeft = center[0] - self.map.display.getDisplaySize()[0]/2
    if windowLeft+self.map.display.getDisplaySize()[0] >= self.map.mapSize[0]: windowLeft = self.map.mapSize[0]-self.map.display.getDisplaySize()[0]-1
    if windowLeft < 0: windowLeft = 0
    windowTop = center[1] - self.map.display.getDisplaySize()[1]/2
    if windowTop+self.map.display.getDisplaySize()[1] >= self.map.mapSize[1]: windowTop = self.map.mapSize[1]-self.map.display.getDisplaySize()[1]-1
    if windowTop < 0: windowTop = 0
    return pygame.Rect(windowLeft, windowTop, self.map.display.getDisplaySize()[0], self.map.display.getDisplaySize()[1])

  def art_onscreen(self):
    """returns an array of all arts currently on the screen
    caches data for multiple calls in each game frame
    """
    windowRect = self.getWindowRect()
    cur_frame = pacglobal.get_frames()
    if self.onscreen_art_lastupdated != None and self.onscreen_art_lastupdated == cur_frame:
      #logging.debug("returning cached art_onscreen")
      return self.onscreen_art
    #logging.debug("Re-calculating on-screen art for shape {1} at F#{0}...".format(cur_frame, self.id))
    self.onscreen_art_lastupdated = cur_frame
    self.onscreen_art = []
    for artpiece in self.map.arts:
      if artpiece.onScreen(windowRect): self.onscreen_art.append(artpiece)
    #logging.debug("returning new onscreen_art: {0}".format(self.onscreen_art))
    return self.onscreen_art
  # end of art_onscreen()
