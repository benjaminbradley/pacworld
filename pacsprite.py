# common attributes/methods shared by all pacworld sprites
import pygame
import logging

class Pacsprite(pygame.sprite.Sprite):
  # required attributes
  # self.getMapTopLeft()  (x,y)
  # self.rect   Rect

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
