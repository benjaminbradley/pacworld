#from pygame import *  # for pygame.time.get_ticks()
import logging

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
