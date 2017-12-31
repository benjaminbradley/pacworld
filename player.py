import logging
import random

AUTO_MODE_ACTIVATION_IDLETICKS = 50000
AUTO_MODE_SWITCHSHAPES_IDLETICKS = 150000


# The class for the player
class Player():
  
  def __init__(self): #, mapSize, displaySize, theworld): , map ?
    self.shape = None
    self.last_shapeswitch = None

  def selectShape(self, shape):
    if self.shape != None:
      self.shape.autonomous = True  # make the old shape autonomous again
    # 
    self.shape = shape
    self.shape.autonomous = False  # the player shape

  def checkIdle(self, ticks):
    """if player's shape has been idle too long, activate autonomous behavion"""
    if('last_activity' not in self.shape.auto_status.keys()):
      # initialize
      self.shape.auto_status['last_activity'] = ticks
    elif(self.shape.auto_status['last_activity'] + AUTO_MODE_ACTIVATION_IDLETICKS < ticks and not self.shape.autonomous):
      self.shape.debug("Player idle, triggering autonomous behavior.")
      self.shape.autonomous = True
      self.last_shapeswitch = ticks
    elif(self.shape.autonomous and \
      (self.last_shapeswitch is None or self.last_shapeswitch + AUTO_MODE_SWITCHSHAPES_IDLETICKS < ticks)):
      self.shape.debug("Player idle, switching to new random shape.")
      # change shapes
      self.last_shapeswitch = ticks
      self.shape = random.choice(self.shape.map.shapes)

  def notIdle(self, ticks):
    """register player input, cancel autonomous behavior if enabled"""
    self.shape.auto_status['last_activity'] = ticks
    if(self.shape.autonomous):
      self.shape.debug("Player not idle, cancelling autonomous behavior.")
      self.shape.autonomous = False
