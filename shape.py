import random
import pygame # Provides what we need to make a game
import sys # Gives us the sys.exit function to close our program
import math  # sin,cos,pi
import logging

from pathfinder import PathFinder

import pacdefs
import pacglobal
from pacsounds import Pacsounds,getPacsound
from pacdisplay import Pacdisplay
from pacsprite import Pacsprite
import colors
import effect
from effect import *  # Effect, EFFECT_*
from swirl import Swirl

MAX_SIDES = 10
SIZE_MINIMUM = 10
SIZE_MAXIMUM = 140
DIR_UP = 'u'
DIR_DOWN = 'd'
DIR_LEFT = 'l'
DIR_RIGHT = 'r'
DIRECTIONS = [DIR_UP, DIR_DOWN, DIR_LEFT, DIR_RIGHT]

BURST_EFFECT_NUMFRAMES = 6
ART_TOUCH_JITTER = 15  # time in game frames that re-touching the same art piece will not trigger a re-touch effect
MOVE_HISTORY_SIZE = 5  # number of movements to use to calculating average movement over time to set character angle

AUTO_SWIRL_ACTIVATION_MINTICKS = 5000
AUTO_SWIRL_ACTIVATION_CHANCE = 0.05
AUTO_SWIRL_CHANGE_MINTICKS = 20000
AUTO_SWIRL_CHANGE_CHANCE = 0.02
AUTO_THOUGHT_CREATION_CHANCE = 0.01

MAX_THOUGHTFORM_ID = 2147483647
MAX_THOUGHTFORM_COMPLEXITY = 1000
MIN_THOUGHTFORM_COMPLEXITY = 200

# The class for Shapes
class Shape(Pacsprite):
  
  def __init__(self, display, themap, shape_size, num_sides = 3):
    # Initialize the sprite base class
    super(Shape, self).__init__()
    
    self.type = pacdefs.TYPE_CHARACTER
    self.map = themap
    
    # Get the display size for working out collisions later
    self.display = display
    
    self.colorIdx = 0
    self.setColor()
    
    # Get a radius value proportionate to the display size
    self.side_length = shape_size
    self.num_sides = num_sides
    self.outlineWidth = 4
    self.angle = 0
    
    # data for helper functs startmove/stopmove for keyboard movement
    self.going_in_dir = {}  # hash of direction (DIR_* constants) to boolean
    for d in DIRECTIONS: self.going_in_dir[d] = False
    # data for rotation movement over time
    self.turning = None  # if set, will be a hash containing the key 'angle'

    # Work out a speed
    self.setSpeed()
    self.autoSpeed = int(random.randint(60,120) * self.linearSpeed/2 / 100)
    # cap autonomous movement at half normal speed
    # multiplied by a randomizer

    # initialize effects
    self.effects = {}  # dictionary of Effect.EFFECT_TYPE to Effect class
    
    self.swirls = []  # array of swirls the shape has
    self.curSwirl = None  # array index pointer to "current" swirl
    self.swirlRotationAngle_rad = 0  # swirls rotate inside the character
    self.swirlRotationAngle_delta_rad = float(random.randint(1,20)) / 360 * 2*math.pi
    if(random.randint(0,1) == 0): self.swirlRotationAngle_delta_rad *= -1
    #logging.debug("swirlRotationAngle_delta_rad = {0}".format(self.swirlRotationAngle_delta_rad))

    # Reset the shape & create the first image
    self.reset()  # also initializes some location-based variables
    
    # experience variables
    self.last_touched_art = {}  # hash of art.id to ticks
    self.last_moved_frame = 0  # frame of last character movement
    self.last_artsearch_position = None # position where we were last time we searched for nearby art
    self.map_knowledge = [[None for x in range(self.map.world.cols+1)] for y in range(self.map.world.rows+1)]  # hash of y,x indices to: -1=inaccessible, 0=accessible, never been there, 1+=times visited; None=unknown
    
    # AI
    self.autonomous = False
    self.auto_status = {}  # dictionary of key/value pairs for autonomous activity

    # initialize subsystems
    self.sound = getPacsound()

  def debug(self, msg):
    if hasattr(self, 'id'): the_id = self.id
    else: the_id = '-'
    logging.debug("Shape[{0}]:{1}".format(the_id, msg))

  def setColor(self):
    self.color = colors.COLORWHEEL[self.colorIdx]
    self.eye_color = colors.YELLOW
  
  def colorUp(self):
    self.colorIdx += 1
    if(self.colorIdx >= len(colors.COLORWHEEL)):
      self.colorIdx = 0
    self.setColor()
    self.makeSprite()
    return True  # always successful

  def colorDn(self):
    self.colorIdx -= 1
    if(self.colorIdx < 0):
      self.colorIdx = len(colors.COLORWHEEL)-1
    self.setColor()
    self.makeSprite()
    return True  # always successful

  def setSpeed(self):
    ''' sets the shape's speed based on its size '''
    self.linearSpeed = int(self.side_length / 8)
    self.rotationSpeed = self.linearSpeed
    self.debug("linearSpeed is now {0}".format(self.linearSpeed))
  
  def get_swirlpos(self, i):
    num_swirls = len(self.swirls)
    base_x = int(self.image.get_width()/2)
    base_y = int(self.image.get_height()/2)
    if num_swirls == 1:
      return (base_x,base_y)
    else:
      SWIRL_ROTATE_RADIUS = max(4, int(self.side_length / 15))  #2 + num_swirls
      theta = 2 * math.pi * float(i) / float(num_swirls)
      theta = theta + self.swirlRotationAngle_rad;
      if(theta > 2*math.pi): theta -= 2*math.pi
      if(theta < 0): theta += 2*math.pi
      x = int(SWIRL_ROTATE_RADIUS * math.cos(theta))
      y = int(SWIRL_ROTATE_RADIUS * math.sin(theta))
      #logging.debug("swirl x,y is {0},{1}".format(x,y))
      return (base_x + x, base_y + y)
  
  def getCenter(self):
    return self.center

  def getMapTopLeft(self):
    """returns an (x,y) tuple for the top-left of this shape on the map"""
    x = self.center[0] - int(self.rect.width/2)
    y = self.center[1] - int(self.rect.height/2)
    return (x,y)

  def makeSprite(self):
    # Create an image for the sprite
    self.image = pygame.Surface((self.side_length, self.side_length))
    self.image.fill(colors.BLACK)
    self.image.set_colorkey(colors.BLACK, pygame.RLEACCEL)  # set the background to transparent
    if(self.num_sides == 1):
      # dot
      radius = self.outlineWidth + self.outlineWidth
      center = int(float(self.side_length) / 2)
      pygame.draw.circle(self.image, self.color, (center,center), radius, 0)
      pygame.draw.line(self.image, (63,63,63), (center,center), (self.side_length, center), 1)
    elif(self.num_sides == 2):
      # a single line
      y = int(float(self.side_length) / 2)
      pygame.draw.line(self.image, self.color, (0, y), (self.side_length, y), self.outlineWidth)
    elif(self.num_sides > MAX_SIDES):
      radius = int(float(self.side_length) / 2)
      pygame.draw.circle(self.image, self.color, (radius,radius), radius, self.outlineWidth)
    else:
      pointlist = []
      for i in range(self.num_sides):
        r = int(float(self.side_length-self.outlineWidth)/2)
        theta = 2 * math.pi * float(i) / float(self.num_sides)
        x = r + int(r * math.cos(theta))
        y = r + int(r * math.sin(theta))
        pointlist.append((x,y))
      pygame.draw.polygon(self.image, self.color, pointlist, self.outlineWidth)
    
    # add the swirls
    for i,swirl in enumerate(self.swirls):
      swirlpos = self.get_swirlpos(i)
      swirl.draw(self.image, swirlpos, i == self.curSwirl)

    # draw the "eye" direction indicator
    radius = self.outlineWidth + self.outlineWidth
    center = int(float(self.side_length) / 2)
    pygame.draw.circle(self.image, self.eye_color, (self.side_length-radius, center), radius, self.outlineWidth)
    
    # add DEBUG info if enabled
    if pacdefs.DEBUG_SHAPE_SHOWID and hasattr(self, 'id'):
      font = pygame.font.Font(None, 26)
      textBitmap = font.render(str(self.id), True, colors.PINK)
      self.image.blit(textBitmap, (int(self.image.get_width()/2), int(self.image.get_height()/2)))
    
    # save the old sprite location before generating new rect
    oldrectpos = None
    if hasattr(self, 'rect'):
      oldrectpos = self.rect.center
    
    # rotate image, if applicable
    if(self.angle != 0):
      self.image = pygame.transform.rotate(self.image, self.angle)

    # create a mask for the sprite (for collision detection)
    self.mask = pygame.mask.from_surface(self.image)

    # draw any effects
    for effect in self.effects.values():
      effect.draw(self.image)

    # Create the sprites rectangle from the image, maintaining rect position if set
    #pygame.draw.rect(self.image, (255,0,0), self.image.get_rect(), 3)  # DEBUG RED BORDER
    self.rect = self.image.get_rect()
    if oldrectpos != None:
      self.rect.center = oldrectpos
    
    self.dirty_sprite = False

  def topLeftToCenter(self, xy):
    return [xy[0] + int(self.rect.width/2), xy[1] + int(self.rect.height/2)]
  
  def reset(self):
    # put us in a random square
    startRow = random.randint(0, self.map.world.rows-1)
    startCol = random.randint(0, self.map.world.cols-1)
    startPos = (startCol, startRow)
    # reset sprite
    self.angle = 0
    self.makeSprite()
    # Start the shape directly in the centre of the screen
    self.center = self.map.gridToScreenCoordCenter(startPos)
    self.screenTopLeft = list(self.getMapTopLeft())
    # reset other attributes as well
    self.updatePosition()
    self.moveHistory = [list(self.getCenter())]  # must happen after self.rect is set in makeSprite()

  def update(self, t):
    # check for on-going movement (for kb input)
    if self.going_in_dir[DIR_DOWN]:
      self.moveDown()
    elif self.going_in_dir[DIR_UP]:
      self.moveUp()
    # once for each axis
    if self.going_in_dir[DIR_LEFT]:
      self.moveLeft()
    elif self.going_in_dir[DIR_RIGHT]:
      self.moveRight()


    # angle changes...

    # check for on-going rotation
    if self.turning != None:
      #print("self.turning from {0} to {1}".format(self.angle, self.turning['angle']))
      if self.angle == self.turning['angle']:  # we're there!
        # stop rotating
        self.turning = None
      else:  # move closer to the target angle
        #logging.debug("shape #{0} is rotating towards {1}, currently at {2}".format(self.id, self.turning['angle'], self.angle))
        minAngle = min(self.angle, self.turning['angle'])
        maxAngle = max(self.angle, self.turning['angle'])
        a = maxAngle - minAngle
        b = 360 + minAngle - maxAngle
        angleDiff = min(a, b)
        if angleDiff < self.rotationSpeed:  # if we're close enough (within one rotation), just set it
          self.angle = self.turning['angle']
        else:
          # need to change center and angle at the same time, if possible
          oldrect = self.rect
          if (self.turning['angle']-self.angle+360) % 360 > 180:
            dir = -1
          else:
            dir = 1
          #logging.debug("turning: cur={4}, goal={5}; dir={2}".format(a,b,dir,None, self.angle,self.turning['angle']))
          #logging.debug("angle diff options {0} or {1}; cur={4}, goal={5}; dir={2}".format(a,b,dir,None, self.angle,self.turning['angle']))
          #logging.debug("new angle set by turning")
          if not self.changeAngle(dir * self.rotationSpeed):
            # if the angle change was unsuccessful/blocked, cancel the operation
            self.turning = None

          # if the rect got resized we'll need to move the center to match
          if self.rect != oldrect:
            # attempt to move the mapcenter by the change in rect size
            dx = self.rect.left - oldrect.left
            dy = self.rect.top - oldrect.top

            if (dx != 0 or dy != 0):
              # move the center to match the new angle, if possible
              moved = self.move(dx, dy)
              #logging.debug("moving by ({0},{1}): success={2}".format(dx,dy,moved))
              self.recordMove()

    # no on-going rotation, what about movement?
    elif self.moveHistory[-1] != list(self.getCenter()):
      # check movement during this update cycle and update angle appropriately
      newAngle = None
      oldestPosition = self.moveHistory[0]
      dx = -1* (oldestPosition[0] - self.getCenter()[0])
      dy = oldestPosition[1] - self.getCenter()[1]
      GRAPHIC_BASE_ANGLE = 90
      if(dx == 0):
        if(dy > 0): newAngle = GRAPHIC_BASE_ANGLE
        else: newAngle = 180+GRAPHIC_BASE_ANGLE
      elif(dy == 0):
        if(dx > 0): newAngle = 270+GRAPHIC_BASE_ANGLE
        else: newAngle = 90+GRAPHIC_BASE_ANGLE
      else:
        # atan2 returns an angle in radians
        theta = math.atan2(float(dy), float(dx))
        #logging.debug("newAngle theta={0}".format(theta))
        # 2*pi rad = 360 deg
        # (pi * theta) * 2 / 360 = deg
        #deg = theta * 180 / math.pi
        newAngle = theta / (2 * math.pi) * 360
      #print "DEBUG: Shape.update(): self.theta={0}, deg={1}".format(theta, newDeg)
      #logging.debug("mapCenter={1}, dx={2}, dy={3}; newAngle={4}".format(None, self.getMapTopLeft(), dx, dy, newAngle))
    
      # record move history for future angle calculation
      self.recordMove()
      
      if newAngle != None:
        #print("setting angle in update to {0}".format(newAngle))
        self.setAngle(newAngle)  # should happen after the object position is updated for movement so that collision detection test is accurate
        #logging.debug("new angle set by movement")
    # end checks for ongoing rotation or movement
    
    
    # advance self play, if enabled
    if self.autonomous:
      self.autoUpdate(t)
    
    if len(self.swirls) > 1:  # rotate swirls inside the character
      self.swirlRotationAngle_rad = (self.swirlRotationAngle_rad + self.swirlRotationAngle_delta_rad)
      #logging.debug("new angle: {0}".format(self.swirlRotationAngle_rad))
      if(self.swirlRotationAngle_rad > 2*math.pi): self.swirlRotationAngle_rad -= 2*math.pi
      if(self.swirlRotationAngle_rad < 0): self.swirlRotationAngle_rad += 2*math.pi
      #logging.debug("rotating swirls to new angle: {0}".format(self.swirlRotationAngle_rad))
      self.dirty_sprite = True
    
    # check for and update sprite animations
    if effect.BURST_EFFECT in self.effects.keys():
      if not self.effects[effect.BURST_EFFECT].update(t):
        del self.effects[effect.BURST_EFFECT]  # FIXME: is more explicit garbage collection needed here?
      self.dirty_sprite = True
    
    if(self.dirty_sprite): self.makeSprite()
  # end of update()
  
  
  def in_move(self):
    return 'movement_destination' in self.auto_status.keys() and self.auto_status['movement_destination'] != None

  def in_head(self):
    return 'thoughtform_id' in self.auto_status.keys() and self.auto_status['thoughtform_id'] != None
  
  def spawnThoughtform(self, ticks):
    self.auto_status['thoughtform_id'] = random.randint(0, MAX_THOUGHTFORM_ID)
    self.auto_status['thoughtform_complexity'] = random.randint(0, (MAX_THOUGHTFORM_COMPLEXITY-MIN_THOUGHTFORM_COMPLEXITY)) + MIN_THOUGHTFORM_COMPLEXITY
    self.auto_status['thoughtform_starttick'] = ticks
    self.debug("spawning thoughtform[#{1}, c={2}] at {0}".format(ticks, self.auto_status['thoughtform_id'], self.auto_status['thoughtform_complexity']))


  def autoUpdate(self, ticks):
    """this is the master update routine for the NPC AI"""
    # possible random activities:
    swirl_activation_chance = AUTO_SWIRL_ACTIVATION_CHANCE
    
    # ACTIVITY: change swirls
    if len(self.swirls) > 0 and \
        ('last-swirl-change' not in self.auto_status.keys() or self.auto_status['last-swirl-change'] + AUTO_SWIRL_CHANGE_MINTICKS < ticks) \
        and random.random() < AUTO_SWIRL_CHANGE_CHANCE:
      if(random.randint(0,1) == 0):
        self.trySwirlLeft()
      else:
        self.trySwirlRight()
      self.auto_status['last-swirl-change'] = ticks
      swirl_activation_chance = 0.5   # if we've just changed swirls, there's a high chance that we'll immediately activate it
    
    # ACTIVITY: activate a swirl
    if len(self.swirls) > 0 and \
        ('last-swirl-activation' not in self.auto_status.keys() or self.auto_status['last-swirl-activation'] + AUTO_SWIRL_ACTIVATION_MINTICKS < ticks) \
        and random.random() < swirl_activation_chance:
      #logging.debug("[Shape {1}] self-activating current swirl at {0}".format(ticks, self.id))
      self.activateSwirl(random.randint(0,1) == 0)
      self.auto_status['last-swirl-activation'] = ticks
    
    # ACTIVITY: stop to think
    # TODO: modify probability based on interesting things in environment
    if self.in_head():
      if self.auto_status['thoughtform_starttick'] + self.auto_status['thoughtform_complexity'] * 3 < ticks:
        self.debug("Thoughtform {0} has expired at {1}.".format(self.auto_status['thoughtform_id'], ticks))
        del self.auto_status['thoughtform_id']
        del self.auto_status['thoughtform_complexity']
        del self.auto_status['thoughtform_starttick']
        if 'thoughtform_target' in self.auto_status: del self.auto_status['thoughtform_target']
      else:
        # still in an ongoing thought
        if self.turning is None and 'thoughtform_target' in self.auto_status:  # and we're not currently turning
          self.faceTo(self.auto_status['thoughtform_target'])  # make sure we turn to face the object we're considering
    elif not self.in_head() and random.random() < AUTO_THOUGHT_CREATION_CHANCE:
      self.spawnThoughtform(ticks)
      # turn to look at something nearby
      object_of_interest = None
      # close people first
      radius = 2
      while(object_of_interest is None and radius <= 6):
        nearby_shapes = self.map.nearShapes(self.getCenter(), self.map.character_size * radius, self)
        if len(nearby_shapes) > 0:
          object_of_interest = nearby_shapes[0]
        radius += 2
      # then art, if no nearby people found
      if object_of_interest is None:
        nearby_art = self.art_onscreen()
        if len(nearby_art) > 0:
          object_of_interest = random.choice(nearby_art)
      if object_of_interest is not None:
        self.debug("Found a nearby object of interest, turning to face...")
        self.faceTo(object_of_interest)
        self.auto_status['thoughtform_target'] = object_of_interest

    # ACTIVITY: move in a direction
    # if we're already moving to a known destination, carry on
    elif self.in_move():
      # move along the path
      # destination in X,Y coords is the next point in the path
      nextnodeGridYX = self.auto_status['movement_path'][self.auto_status['movement_path_curidx']]
      destGridLeftTopXY = self.map.gridToScreenCoord((nextnodeGridYX[1], nextnodeGridYX[0]))
      # adjust dest to center shape on dest grid square
      xoffset = (self.map.grid_cellwidth) / 2
      yoffset = (self.map.grid_cellheight) / 2
      destXY = (destGridLeftTopXY[0] + xoffset, destGridLeftTopXY[1] + yoffset)
      dest_distance = int(self.map.world.move_cost(self.getCenter(), list(destXY)))
      #logging.debug("moving from {0} towards destination at {1} (based on destTopLeft of {2} adjusted by offset {5}) via node {3}, distance to target is {4}".format(self.getCenter(), destXY, destGridLeftTopXY, nextnodeGridYX, dest_distance, (xoffset, yoffset)))
      self.moveTowards(destXY)

      # if we're at the node (or close enough), move to the next node
      if dest_distance < pacdefs.WALL_LINE_WIDTH + self.linearSpeed:
        self.debug("reached node {0}, moving to next node in path (out of {1} total nodes)".format(self.auto_status['movement_path_curidx'], len(self.auto_status['movement_path'])))
        # if we're at our destination, clear the destination & path
        self.auto_status['movement_path_curidx'] += 1
        if self.auto_status['movement_path_curidx'] == len(self.auto_status['movement_path']):
          self.debug("reached destination, clearing path")
          # if we just finished "wandering", then stop and have a think
          if type(self.auto_status['movement_destination']) is str:
            self.spawnThoughtform(ticks)
          del self.auto_status['movement_destination']
          del self.auto_status['movement_path']
          del self.auto_status['movement_path_curidx']
    elif(self.last_artsearch_position != list(self.getCenter())): # if we have moved since the last look, or have never looked
      # else, look for a new destination
      #  if something interesting is onscreen
      self.last_artsearch_position = list(self.getCenter())
      self.debug("Searching for nearby art...")
      art_on_screen = self.art_onscreen()
      random.shuffle(art_on_screen)
      for art in art_on_screen:
        # if artpiece is on the screen,
        #   and we haven't seen it yet
        if art.id in self.last_touched_art.keys(): continue # skip arts that we've already seen
        #  then look for a path from current pos to artpiece
        start = self.get_gridCoordsYX()
        goal = (art.top, art.left) # grid square of art piece; NOTE: pathfinder takes (y,x) coordinates
        self.debug("[FORMAT (y,x)] looking for path from {0} to {1}".format(start, goal))
        pf = PathFinder(self.map.world.successors, self.map.world.move_cost, self.map.world.move_cost)
        path = list(pf.compute_path(start, goal))
        if(path):  # if we can get to it, set our destination
          if(len(path) > 1):  # but only if it's more than 1 step away
            self.debug("setting destination as art {0}, via path: {1}".format(art,path))
            self.auto_status['movement_destination'] = art
            self.auto_status['movement_path'] = path
            self.auto_status['movement_path_curidx'] = 1  # destination starts at node 1 since node 0 is starting point
            break
        else:
          # no path is possible, mark this destination as inaccessible
          self.last_touched_art[art.id] = None  # adding the key to the dictionary marks this as "seen"
      # if we finish the for loop, there is no art on screen
    else:
      # ACTIVITY: go to a random accessible square on screen, with preference for unvisited squares
      # wander around the map - use an exploratory algorithm ?
      destination = None
      while(destination is None):
        path = None
        #get random destination on screen
        winRect = self.getWindowRect() # left, top, right, bottom
        grid_minx = int(winRect[0] / self.map.grid_cellwidth)
        grid_miny = int(winRect[1] / self.map.grid_cellheight)
        grid_maxx = int((winRect[0]+winRect[2]) / self.map.grid_cellwidth)
        grid_maxy = int((winRect[1]+winRect[3]) / self.map.grid_cellheight)
        #self.debug("on-screen grid coords are: {0} (topLeft) to {1} (botRight)".format((grid_minx,grid_miny), (grid_maxx, grid_maxy)))
        destx = random.randint(grid_minx,grid_maxx)
        desty = random.randint(grid_miny,grid_maxy)
        #self.debug("testing grid spot: {0},{1} (x,y)".format(destx, desty))
        destination = str(destx)+','+str(desty)
        if(self.map_knowledge[desty][destx] is None):
          # try and compute path to destination if not already known...
          start = self.get_gridCoordsYX()
          goal = (desty, destx) # NOTE: pathfinder takes (y,x) coordinates
          pf = PathFinder(self.map.world.successors, self.map.world.move_cost, self.map.world.move_cost)
          path = list(pf.compute_path(start, goal))
          # keep track of visited (and inaccessible) squares in the grid...
          if(path):  # if we can get to it, set our destination
            self.map_knowledge[desty][destx] = 0
          else:
            self.map_knowledge[desty][destx] = -1
            #self.debug("grid spot: {0},{1} (x,y) is INACCESSIBLE".format(destx, desty))
            # destination is INaccessible
            destination = None
        elif(self.map_knowledge[desty][destx] == -1):
          # known destination, but inaccessible, try again...
          destination = None
      # good destination, not inaccessible...
      #TODO: create preference for unvisited squares
      # go to destination....
      self.debug("wandering to grid spot: {0},{1} (x,y)".format(destx, desty))
      if(path is None):
        # going to previously computed destination
        start = self.get_gridCoordsYX()
        goal = (desty, destx) # NOTE: pathfinder takes (y,x) coordinates
        pf = PathFinder(self.map.world.successors, self.map.world.move_cost, self.map.world.move_cost)
        path = list(pf.compute_path(start, goal))
      if(len(path) > 1):  # if len(path) <= 1 then we're already there
        self.auto_status['movement_path'] = path
        self.auto_status['movement_path_curidx'] = 1  # destination starts at node 1 since node 0 is starting point
        self.auto_status['movement_destination'] = destination
      #TODO: update self.map_knowledge when we get to a grid square there
      
  # end of autoUpdate()


  def recordMove(self):
    self.moveHistory.append(list(self.getCenter()))
    if(len(self.moveHistory) > MOVE_HISTORY_SIZE):
      self.moveHistory.pop(0)  # remove front element
  
  
  def animateToAngle(self, newAngle):
    self.turning = {
      'angle' : newAngle
    }

  def get_gridCoordsYX(self):
    gridY = int(self.center[1] / self.map.grid_cellheight)
    gridX = int(self.center[0] / self.map.grid_cellwidth)
    self.debug("in grid square {0},{1} (X,Y)".format(gridX, gridY))
    return (gridY,gridX)


  def updatePosition(self):
    """place the shape's sprite on the screen based on it's current position on the map"""
    """updates screenTopLeft and sprite.rect's position"""
    mapTopLeft = self.getMapTopLeft()
    self.screenTopLeft = list(mapTopLeft)
    if mapTopLeft[0] < self.display.getDisplaySize()[0]/2:
      self.screenTopLeft[0] = mapTopLeft[0]
    elif mapTopLeft[0] > self.map.mapSize[0]-self.display.getDisplaySize()[0]/2:
      self.screenTopLeft[0] = self.display.getDisplaySize()[0] - (self.map.mapSize[0]-mapTopLeft[0])
    else: 
      self.screenTopLeft[0] = self.display.getDisplaySize()[0]/2

    if mapTopLeft[1] < self.display.getDisplaySize()[1]/2:
      self.screenTopLeft[1] = mapTopLeft[1]
    elif mapTopLeft[1] > self.map.mapSize[1]-self.display.getDisplaySize()[1]/2:
      self.screenTopLeft[1] = self.display.getDisplaySize()[1] - (self.map.mapSize[1]-mapTopLeft[1])
    else: 
      self.screenTopLeft[1] = self.display.getDisplaySize()[1]/2
    
    self.rect.top = self.screenTopLeft[1]
    self.rect.left = self.screenTopLeft[0]
    #logging.debug("rect is: {0}".format(self.rect))

  def draw(self, surface):
    if self.map.player.shape == self:
      #print "DEBUG: drawing image at {0}".format(self.screenTopLeft)
      surface.blit(self.image, self.screenTopLeft)
    else:
      windowRect = self.map.player.shape.getWindowRect()
      mapTopLeft = self.getMapTopLeft()
      screenx = mapTopLeft[0] - windowRect.left
      screeny = mapTopLeft[1] - windowRect.top
      surface.blit(self.image, (screenx,screeny))
  # end of Shape.draw()


  """return a float between 0 and 1 based on how close this shape is to the player"""
  def soundProximity(self):
    windowRect = self.map.player.shape.getWindowRect()
    if self==self.map.player.shape: soundvolume = 1.0
    elif self.onScreen(windowRect): soundvolume = pacdefs.ONSCREEN_SOUND_PERCENT
    elif self.nearScreen(windowRect): soundvolume = pacdefs.NEARBY_SOUND_PERCENT
    else: soundvolume = 0
    return soundvolume


  def receiveSwirl(self, swirl):
    for myswirl in self.swirls:
      if(swirl.look == myswirl.look):
        self.debug("this shape already has this swirl type")
        return
    self.swirls.append(swirl)
    self.curSwirl = len(self.swirls) - 1  # change current to the new one
    self.debug("got a new swirl effect type {0}, total {1} swirls now".format(swirl.effect_type, len(self.swirls)))
    self.makeSprite()
    self.sound.play('get', self.soundProximity())

  def activateSwirl(self, dir_up = True):
    # checks to make sure we do have at least one swirl
    if self.curSwirl == None or len(self.swirls) == 0: return False
    self.swirls[self.curSwirl].activate(self, dir_up)
    return True
  
  
  def tryAsk(self):
    self.debug("tryAsk")
    #TODO
    self.sound.play('ask', self.soundProximity())
    
  def tryGive(self):
    self.debug("tryGive")
    # checks to make sure we do have at least one swirl
    if self.curSwirl == None or len(self.swirls) == 0: return False
    # check for nearby shapes
    nearby_shapes = self.map.nearShapes(self.getCenter(), self.map.character_size * 1.5, self)
    if len(nearby_shapes) > 0:
      #logging.debug("Shapes near to S#{0}: {1}".format(self.id, nearby_shapes))
      #TODO: be choosy about which shape to give to - is there one in front (closer to my eye?)
      receiver = nearby_shapes[0]
      self.debug("giving swirl to Shape #{0}...".format(receiver.id))
      receiver.faceTo(self)
      self.map.startEffect(effect.TRANSFER_EFFECT, 
          {  EFFECT_SOURCE:self,
            EFFECT_TARGET:receiver,
            EFFECT_ONCOMPLETE: lambda: receiver.receiveSwirl(self.copySwirl())
          })
    self.sound.play('give', self.soundProximity())

  def copySwirl(self):
    if self.curSwirl == None or len(self.swirls) == 0: return False
    cur_swirl = self.swirls[self.curSwirl]
    return Swirl(cur_swirl.look)

  
  def trySwirlRight(self):
    if self.curSwirl == None: return  # checks to make sure we do have at least one swirl
    self.curSwirl = ((self.curSwirl + 1) % len(self.swirls))
    #logging.debug("trySwirlRight: new curSwirl = {0}".format(self.curSwirl))
    self.makeSprite()
  
  def trySwirlLeft(self):
    if self.curSwirl == None: return  # checks to make sure we do have at least one swirl
    self.curSwirl = ((self.curSwirl - 1) % len(self.swirls))
    #logging.debug("trySwirlLeft: new curSwirl = {0}".format(self.curSwirl))
    self.makeSprite()
  

  def touchArt(self, art):
    #logging.debug("shape #{0} is touching art #{1}".format(self.id, art.id))
    frames = pacglobal.get_frames()
    # check the last time we touched this art
    if art.id in self.last_touched_art.keys():
      last_touched = self.last_touched_art[art.id]
      self.last_touched_art[art.id] = frames
      #logging.debug("art was touched at {0}, now={1}, last move at {2}".format(last_touched, frames, self.last_moved_frame))
      if self.last_moved_frame == last_touched:
        #logging.debug("still mid-touch")
        return False
      if last_touched <= frames - 1 and last_touched + ART_TOUCH_JITTER > frames: 
        self.debug("art was touched too recentely - at {0}".format(last_touched))
        return False
    else:
      self.last_touched_art[art.id] = frames
    # trigger the art-touch event!
    self.debug("touching art #{0} - triggering event!".format(art.id))
    self.map.startEffect(effect.TRANSFER_EFFECT, 
        {  EFFECT_SOURCE:art,
          EFFECT_TARGET:self,
          EFFECT_ONCOMPLETE: lambda: self.receiveSwirl(art.getSwirl())
        })


  def move(self, dx, dy):
    # Move each axis separately. Note that this checks for collisions both times.
    movedx = movedy = False
    if dx != 0:
      movedx = self.move_single_axis(dx, 0)
    if dy != 0:
      movedy = self.move_single_axis(0, dy)
    if movedx or movedy:
      # check for other map effects that happen based on movement
      self.map.checkTriggers(self)
    self.last_moved_frame = pacglobal.get_frames()
    return movedx or movedy

  def move_single_axis(self, dx, dy):
    # save initial positions
    startpos = list(self.getCenter())
    # Move the rect
    #logging.debug("Shape.move_single_axis({0}, {1})".format(dx, dy))
    self.center[0] += int(dx)
    self.center[1] += int(dy)
    # if there's a collision, un-do the move
    if self.map.wallCollision(self):
      #logging.debug("move aborted due to collision")
      self.center = startpos
      return False
    else:
      #logging.debug("shape moved to %s from %s", self.center, startpos)
      self.updatePosition()
      return True
  
  def moveTowards(self, destination):
    (destx, desty) = destination
    dx = destx - self.getCenter()[0]
    if self.autonomous:
      maxspeed = self.autoSpeed
    else:
      maxspeed = self.linearSpeed
    if(dx < -maxspeed): dx = -maxspeed
    elif(dx > maxspeed): dx = maxspeed
    dy = desty - self.getCenter()[1]
    if(dy < -maxspeed): dy = -maxspeed
    elif(dy > maxspeed): dy = maxspeed
    self.move(dx, dy)
  
  def moveUp(self):
    self.move(0, -self.linearSpeed)

  def moveDown(self):
    self.move(0, self.linearSpeed)
  
  def moveLeft(self):
    self.move(-self.linearSpeed, 0)

  def moveRight(self):
    self.move(self.linearSpeed, 0)
  
  def startMove(self, direction):
    self.going_in_dir[direction] = True
  
  def stopMove(self, direction):
    self.going_in_dir[direction] = False
  
  def moveFwd(self):
    # Move in the direction we're pointing
    theta = 2 * math.pi * ((float(self.angle)+90)%360 / 360)
    dy = math.cos(theta)
    dx = math.sin(theta)
    #print "DEBUG: angle={0}, dx={1}, dy={2}".format(theta, dx, dy)
    #print "DEBUG: Shape.moveFwd(): old mapCenter={0}".format(self.center)
    self.move(dx * self.linearSpeed, dy * self.linearSpeed)
    #print "DEBUG: Shape.moveFwd(): new mapCenter={0}".format(self.center)

  def moveBack(self):
    # Move away from the direction we're pointing
    theta = 2 * math.pi * ((float(self.angle)+90)%360 / 360)
    dy = math.cos(theta)
    dx = math.sin(theta)
    self.move(dx * -self.linearSpeed, dy * -self.linearSpeed)

  ''' a wrapper for sizeUp/sizeDown changes that checks collisions'''
  def changeSize(self, newsize):
    oldsize = self.side_length
    self.debug("old size="+str(oldsize))
    if newsize > SIZE_MAXIMUM: newsize = SIZE_MAXIMUM
    if(newsize < SIZE_MINIMUM): newsize = SIZE_MINIMUM
    self.side_length = newsize
    self.makeSprite()  # re-create the sprite with new attributes
    if self.map.wallCollision(self):  # attribute changed due to collision, restore old values
      self.side_length = oldsize
      self.makeSprite()
      self.sound.play('error')  # provide user feedback for failure
      return False
    else:
      self.debug("new size="+str(newsize))
      self.setSpeed()
      return True

  def sizeUp(self):
    return self.changeSize(int(self.side_length * 1.1))

  def sizeDown(self):
    return self.changeSize(int(self.side_length * 0.9))
  
  def setAngle(self, angle):
    startAngle = self.angle
    # update the angle
    self.angle = angle
    # check for wrap-around
    if(self.angle < 0): self.angle = 360 + self.angle
    if(self.angle >= 360): self.angle = 360 - self.angle
    #print("DEBUG: angle is now {0}".format(self.angle))
    
    # if there's a collision, un-do the rotation
    #if hasattr(self, 'map') and self.map.wallCollision(self):
    # remake the sprite for the collision test
    self.makeSprite()
    if self.map.wallCollision(self):
      #logging.debug ("rotation cancelled due to collision. angle left at {0}".format(self.angle))
      self.angle = startAngle
      self.makeSprite()
      return False
    else:
      # re-create the sprite in the new position
      #logging.debug ("new angle: {0}".format(self.angle))
      self.makeSprite()
      #logging.debug("new angle={0}, new sprite rect is: {1}".format(self.angle, self.rect))
      return True
    
    
  def changeAngle(self, delta):
    """ angle in degrees. 0 is (12 noon?) """
    return self.setAngle(self.angle + delta)
  
  
  def faceTo(self, target):
    """change shape's angle to face towards the passed target"""
    slf = self.getCenter()
    trg = target.getCenter()
    dx = -1* (slf[0] - trg[0])
    dy = slf[1] - trg[1]
    GRAPHIC_BASE_ANGLE = 90
    if(dx == 0):
      if(dy > 0): newAngle = GRAPHIC_BASE_ANGLE
      else: newAngle = 180+GRAPHIC_BASE_ANGLE
    elif(dy == 0):
      if(dx > 0): newAngle = 270+GRAPHIC_BASE_ANGLE
      else: newAngle = 90+GRAPHIC_BASE_ANGLE
    else:
      theta = math.atan2(float(dy), float(dx))
      newAngle = ((theta / (2 * math.pi) * 360) + 360) % 360
    #SohCahToa
    self.animateToAngle(newAngle)


  def rotateLeft(self):
    self.changeAngle(self.rotationSpeed)
    
  def rotateRight(self):
    self.changeAngle(-self.rotationSpeed)
  
  ''' a wrapper for lessSides/moreSides that checks for collissions
      return true on success
  '''
  def changeSides(self, newsides):
    oldsides = self.num_sides
    if(newsides == 0): newsides = 1
    if(newsides > MAX_SIDES+1): newsides = MAX_SIDES+1
    self.num_sides = newsides
    self.makeSprite()
    if self.map.wallCollision(self):  # attribute changed due to collision
      self.num_sides = oldsides
      self.makeSprite()
      self.sound.play('error')  # provide user feedback for failure
      return False
    else:  # re-create the sprite with new attributes
      self.debug ("num_sides is now {0}".format(self.num_sides))
      return True
  
  def lessSides(self):
    return self.changeSides(self.num_sides - 1)
  
  def moreSides(self):
    return self.changeSides(self.num_sides + 1)


class ShapeTest:

  def __init__(self):

    # Make the display size a member of the class
    self.display = Pacdisplay((640, 480))
    
    # Initialize pygame
    pygame.init()

    # Create a clock to manage time
    self.clock = pygame.time.Clock()

    # Set the window title
    pygame.display.set_caption("Shape Test")

    # Create the window
    self.surface = pygame.display.set_mode(self.display.getDisplaySize())
    
    self.shape = Shape(self.display.getDisplaySize(), None, int(self.display.getDisplaySize()[0] / 10), 3)
    self.sprites = sprite.Group(self.shape)
  # end of __init__
    
  def run(self):
    # Runs the game loop

    while True:
      # The code here runs when every frame is drawn
      #print "looping"

      # Handle Events
      self.handleEvents()

      # Update and draw the sprites
      self.sprites.update(pygame.time.get_ticks())
      self.sprites.draw(self.surface)

      # Update the full display surface to the screen
      pygame.display.update()

      # Limit the game to 30 frames per second
      self.clock.tick(30)

  def handleEvents(self):

    # Handle events, starting with the quit event
    for event in pygame.event.get():
      if event.type == QUIT:
        pygame.quit()
        sys.exit()

      if event.type == KEYDOWN:
        # Find which key was pressed and start moving appropriate bat
        if event.key == K_ESCAPE:
          pygame.quit()
          sys.exit()
        #elif event.key == K_w:
        elif event.key == K_DOWN:
          self.shape.lessSides()
        elif event.key == K_UP:
          self.shape.moreSides()
        elif event.key == K_LEFT:
          self.shape.rotateLeft()
        elif event.key == K_RIGHT:
          self.shape.rotateRight()
        elif event.key == K_SPACE:
          self.surface.fill(colors.BLACK)
        elif event.key == K_a:
          self.shape.colorUp()
        elif event.key == K_z:
          self.shape.colorDn()

      #if event.type == KEYUP:
        #if event.key == K_s or event.key == K_w:
        #  self.player1Bat.stopMove()
        #elif event.key == K_DOWN or event.key == K_UP:
        #  self.player2Bat.stopMove()



if __name__ == '__main__':
  game = ShapeTest()
  game.run()
