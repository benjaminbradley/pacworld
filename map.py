'''
map.py
The entire world map, rendered as a static background image.
May have dynamic effects drawn on top.
Tracks the currently displayed subsection of the world map (windowRect)
'''

import sys
import random
import pygame
from pygame import *
import logging
import math

import pacglobal
import pacdefs
from pacdisplay import Pacdisplay
import wall
from wall import Wall
import colors
import world
from shape import Shape
from effect import *  # Effect, EFFECT_*

# The class for the background
class Map(sprite.Sprite):
  
  def __init__(self, mapSize, display, character_size, theworld):
    # Initialize the sprite base class
    super(Map, self).__init__()
    
    # calculate grid size based on max possible map size
    self.grid_cellheight = grid_cellheight = int(mapSize[1] / theworld.rows)
    self.grid_cellwidth = grid_cellwidth = int(mapSize[0] / theworld.cols)
    logging.debug ("cell size is {0} wide x {1} high".format(grid_cellwidth, grid_cellheight))
    self.displayGridSize = (int(display.getDisplaySize()[0] / grid_cellwidth), int(display.getDisplaySize()[1] / grid_cellheight))
    # re-calculate mapsize based on grid size
    mapSize = (theworld.cols*grid_cellwidth, theworld.rows*grid_cellheight)

    # Set our image to a new surface, the size of the World Map
    self.display = display
    self.mapSize = mapSize
    logging.debug ("mapSize is {0}".format(self.mapSize))
    self.character_size = character_size
    self.image = Surface(self.mapSize)
    
    # Fill the image with a green colour (specified as R,G,B)
    self.image.fill(colors.BLACK)
    
    self.world = theworld
    self.walls = [] # List to hold the walls
    self.wallgrid = [[[] for x in range(self.world.cols)] for y in range(self.world.rows)]  # [y][x] grid of arrays of walls in that grid square
    self.arts = []  # list to hold the arts
    self.shapes = []  # list to hold the shapes

    # NEXT: render the world map from the 'world' class argument
    
    for worldObj in sorted(theworld.objects, key=lambda obj: pacdefs.RENDER_ORDER[obj.type]):
      pacglobal.checkAbort()
      logging.debug ("rendering the next world object: {0}".format(worldObj))
      if worldObj.type == pacdefs.TYPE_PATH:
        left = worldObj.left * grid_cellwidth
        top = worldObj.top * grid_cellheight
        if worldObj.direction_h:
          right = (worldObj.left+worldObj.length) * grid_cellwidth
          bottom = (worldObj.top+worldObj.width) * grid_cellheight
        else:
          right = (worldObj.left+worldObj.width) * grid_cellwidth
          bottom = (worldObj.top+worldObj.length) * grid_cellheight
        width = right - left
        height = bottom - top
        rect = (left, top, width, height)
        pygame.draw.rect(self.image, (111,111,111), rect)
        # draw markers along the path
        marker_length = int(grid_cellwidth*.2)
        if worldObj.direction_h:
          midy = (top+bottom)/2
          for gridx in range(worldObj.left, worldObj.left+worldObj.length):
            ctrx = (gridx+.5)*grid_cellwidth
            pygame.draw.line(self.image, (255,255,255), (ctrx-(marker_length/2),midy), (ctrx+(marker_length/2),midy))
        else:
          midx = (left+right)/2
          for gridy in range(worldObj.top, worldObj.top+worldObj.length):
            ctry = (gridy+.5)*grid_cellheight
            pygame.draw.line(self.image, (255,255,255), (midx, ctry-(marker_length/2)), (midx, ctry+(marker_length/2)))
      
      
      elif worldObj.type == pacdefs.TYPE_ROCK:
        left = worldObj.x * grid_cellwidth
        top = worldObj.y * grid_cellheight
        width = grid_cellwidth
        height = grid_cellheight
        rect = (left, top, width, height)
        rock_color = (111, 111, 111)
        pygame.draw.rect(self.image, rock_color, rect)
        # draw a rock "peak"
        peak_color = pacglobal.adjustColor(rock_color, .4)
        linelength = int(.1*grid_cellwidth)
        randx = left + random.randint(0, int(.6*grid_cellwidth))+linelength
        randy = top + random.randint(0, int(.7*grid_cellheight))+2*linelength
        pygame.draw.line(self.image, peak_color, (randx, randy), (randx+linelength, randy-linelength))
        pygame.draw.line(self.image, peak_color, (randx+2*linelength, randy), (randx+linelength, randy-linelength))


      elif worldObj.type == pacdefs.TYPE_ART:
        # let the sprite manager draw it
        pass

      elif worldObj.type == pacdefs.TYPE_INTERSECTION:
        # draw a grey rectangle
        left = worldObj.left * grid_cellwidth
        top = worldObj.top * grid_cellheight
        width = worldObj.width * grid_cellwidth
        height = worldObj.height * grid_cellheight
        #right = (worldObj['left']+worldObj['width']) * grid_cellwidth
        #bottom = (worldObj['top']+worldObj['length']) * grid_cellheight
        #topLt = (left, top)
        #topRt = (right, top)
        #bottomLt = (left, bottom)
        #bottomRt = (right, bottom)
        rect = (left, top, width, height)
        logging.debug ("intersection rect at {0}".format(rect))
        pygame.draw.rect(self.image, (222,222,222), rect)

      elif worldObj.type == pacdefs.TYPE_FIELD:
        # draw a brown rectangle
        left = worldObj.left * grid_cellwidth
        top = worldObj.top * grid_cellheight
        width = worldObj.width * grid_cellwidth
        height = worldObj.height * grid_cellheight
        rect = (left, top, width, height)
        #print "DEBUG: field rect at {0}".format(rect)
        field_color = (160,82,45)
        pygame.draw.rect(self.image, (160,82,45), rect)
        # draw diagonal hashes on the field
        hash_color = pacglobal.adjustColor(field_color, .4)  # hashes are slightly lighter than bg
        hash_length = round(grid_cellwidth*.2)
        for gridx in range(worldObj.left, worldObj.left+worldObj.width):
          for gridy in range(worldObj.top, worldObj.top+worldObj.height):
            # draw alternating slashes in the middle of each grid square
            ctrx = (gridx+.5)*grid_cellwidth
            ctry = (gridy+.5)*grid_cellheight
            if (gridx+gridy) % 2 == 1:
              pygame.draw.line(self.image, hash_color, (ctrx-hash_length/2, ctry-hash_length/2), (ctrx+hash_length/2, ctry+hash_length/2))
            else:
              pygame.draw.line(self.image, hash_color, (ctrx+hash_length/2, ctry-hash_length/2), (ctrx-hash_length/2, ctry+hash_length/2))

      elif worldObj.type == pacdefs.TYPE_ROOM:
        room_bgcolor = colors.BLUE
        # calculate corners & dimensions
        left = worldObj.left * grid_cellwidth
        top = worldObj.top * grid_cellheight
        width = worldObj.width * grid_cellwidth
        height = worldObj.height * grid_cellheight
        right = left + width
        bottom = top + height
        logging.debug ("rendering ROOM {4} [vert={0}..{1}, horiz={2}..{3}]".format(top,bottom,left,right,worldObj.id))
        # define interior & paint it
        rect = (left, top, width, height)
        #print "DEBUG: room rect at {0}".format(rect)
        pygame.draw.rect(self.image, room_bgcolor, rect)
        ROOM_RANDROTBG = 0.75 # percent chance that a room's background will have random rotation for each square
        # draw pattern on room background
        BGPAT_NONE = 0
        BGPAT_SQUARE = 1
        BGPAT_TRIANGLE = 2
        BGPAT_STRIPEV = 3
        BGPAT_STRIPEH = 4
        BGPAT_STRIPED1 = 5
        BGPAT_STRIPED2 = 6
        BGPATTERNS = [BGPAT_NONE, BGPAT_SQUARE, BGPAT_TRIANGLE, BGPAT_STRIPEV, BGPAT_STRIPEH, BGPAT_STRIPED1, BGPAT_STRIPED2]
        bgpat = random.choice(BGPATTERNS)
        bgcolor_accent = pacglobal.adjustColor(room_bgcolor, -.2)
        if bgpat in [BGPAT_SQUARE, BGPAT_TRIANGLE]:
          # determine rotation, or random for each square
          if(random.random() < ROOM_RANDROTBG):
            rot_angle = -1
          else:
            rot_angle = random.randint(0, 359)
          # cycle through each grid square
          for gridx in range(worldObj.left, worldObj.left+worldObj.width):
            for gridy in range(worldObj.top, worldObj.top+worldObj.height):
              # draw square/triangle in each
              if(rot_angle == -1): rotation_degrees = random.randint(0, 359)
              else: rotation_degrees = rot_angle
              ctrx = (gridx+.5)*grid_cellwidth
              ctry = (gridy+.5)*grid_cellheight
              ctr = (ctrx, ctry)
              size = round(grid_cellheight*.15)
              if(bgpat == BGPAT_TRIANGLE):
                pacglobal.draw_triangle(self.image, ctr, size, bgcolor_accent, 1, rotation_degrees)
              elif(bgpat == BGPAT_SQUARE):
                pacglobal.draw_square(self.image, ctr, size, bgcolor_accent, 1, rotation_degrees)
        elif bgpat in [BGPAT_STRIPEV, BGPAT_STRIPEH, BGPAT_STRIPED1, BGPAT_STRIPED2]:
          # determine line spacing for room
          linespacing_pct = .1*random.randint(1,5)
          # draw background lines in room rect
          if bgpat==BGPAT_STRIPEV:
            linespacing = int(linespacing_pct*grid_cellwidth)
            for x in range(left+linespacing, right, linespacing):
              pygame.draw.line(self.image, bgcolor_accent, (x, top), (x, bottom), 1)
          elif bgpat==BGPAT_STRIPEH:
            linespacing = int(linespacing_pct*grid_cellheight)
            for y in range(top+linespacing, bottom, linespacing):
              pygame.draw.line(self.image, bgcolor_accent, (left, y), (right, y), 1)
          elif bgpat in [BGPAT_STRIPED1, BGPAT_STRIPED2]:
            linespacing_x = int(linespacing_pct*grid_cellwidth)
            linespacing_y = int(linespacing_pct*grid_cellheight)
            dx = linespacing_x
            dy = linespacing_y
            while(dx <= width+height or dy <= height+width):
              if bgpat == BGPAT_STRIPED1:
                #start at topleft corner and wrap around
                if(dx <= width):
                  liney1 = top
                  linex1 = left+dx
                else:
                  liney1 = left+dx - right + top
                  linex1 = right-1
                if(dy <= height):
                  linex2 = left
                  liney2 = top+dy
                else:
                  linex2 = top+dy - bottom + left
                  liney2 = bottom-1
              else: #bgpat==BGPAT_STRIPED2
                #start at bottomleft corner and wrap around
                if(dx <= width):
                  liney1 = bottom
                  linex1 = left+dx
                else:
                  liney1 = bottom - (dx - width)
                  linex1 = right-1
                if(dy <= height):
                  linex2 = left
                  liney2 = bottom - dy
                else:
                  linex2 = dy - height + left
                  liney2 = top
              pygame.draw.line(self.image, bgcolor_accent, (linex1, liney1), (linex2, liney2), 1)
              dx += linespacing_x
              dy += linespacing_y
        #DEBUG MODE: draw the objectId in the middle
        if pacdefs.DEBUG_ROOM_SHOWID:
          pacglobal.draw_text(self.image, str(worldObj.id), (left+(width/2), top+(height/2)))
        
        # draw 4 walls
        roomWalls = {}  # dictionary of side to array of wallDefs (each wallDef is a tuple of 2 points, each one an (x,y) tuple)
        # draw walls that have doors in them
        #NOTE: assumes no more than one door per wall
        num_doors = len(worldObj.doors.keys())
        if num_doors > 1: logging.debug ("multiple doors! Room has {0} doors.".format(num_doors))
        for side,doorpos in worldObj.doors.items():
          #need to keep track of which sides have been processed, 
          #add the defaults later for walls with no doors
          doorx = doorpos[0]
          doory = doorpos[1]
          logging.debug ("rendering ROOM {0} has a door at {1} on side {2}".format(worldObj.id,doorpos,side))
          if side == pacdefs.SIDE_N:
            doorLeft = doorx * grid_cellwidth
            doorRight = (doorx+1) * grid_cellwidth
            # add 2 walls, on either side of the door
            roomWalls[side] = []
            roomWalls[side].append([(left,top), (doorLeft,top)])
            roomWalls[side].append([(doorRight,top), (right,top)])
        
          if side == pacdefs.SIDE_E:
            doorTop = doory * grid_cellheight
            doorBottom = (doory+1) * grid_cellheight
            logging.debug ("rendering ROOM door top/bottom is {0}/{1}".format(doorTop,doorBottom))
            # add 2 walls, on either side of the door
            roomWalls[side] = []
            roomWalls[side].append([(right,top), (right,doorTop)])
            roomWalls[side].append([(right,doorBottom), (right,bottom)])
        
          if side == pacdefs.SIDE_S:
            doorLeft = doorx * grid_cellwidth
            doorRight = (doorx+1) * grid_cellwidth
            # add 2 walls, on either side of the door
            roomWalls[side] = []
            roomWalls[side].append([(left,bottom), (doorLeft,bottom)])
            roomWalls[side].append([(doorRight,bottom), (right,bottom)])
        
          if side == pacdefs.SIDE_W:
            doorTop = doory * grid_cellheight
            doorBottom = (doory+1) * grid_cellheight
            # add 2 walls, on either side of the door
            roomWalls[side] = []
            roomWalls[side].append([(left,top), (left,doorTop)])
            roomWalls[side].append([(left,doorBottom), (left,bottom)])
        # end of for each door (creating walls w/ doors)
          
        # check all directions and add a default wall if none is defined
        for side in pacdefs.SIDES:
          if side not in roomWalls.keys() or len(roomWalls[side]) == 0:
            logging.debug ("drawing default wall for side {0}".format(side))
            roomWalls[side] = []
            if side == pacdefs.SIDE_N: roomWalls[side].append([(left,top), (right,top)])
            if side == pacdefs.SIDE_E: roomWalls[side].append([(right,top), (right, bottom)])
            if side == pacdefs.SIDE_S: roomWalls[side].append([(right,bottom), (left,bottom)])
            if side == pacdefs.SIDE_W: roomWalls[side].append([(left,bottom), (left,top)])

        for walls in roomWalls.values():
          for wallPoints in walls:
            # create the wall def
            newwall = Wall(self.mapSize, wallPoints[0], wallPoints[1])
            # add to walls array
            self.addWall( newwall )
            # draw on image
            newwall.draw(self.image)

    # draw a border, registering each line as a wall
    topLt = (0, 0)
    topRt = (self.mapSize[0], 0)
    botLt = (0, self.mapSize[1])
    botRt = (self.mapSize[0], self.mapSize[1])
    wallDefs = [
      (topLt, topRt),
      (topRt, botRt),
      (botRt, botLt),
      (botLt, topLt)
    ]
    for wallPoints in wallDefs:
      newwall = Wall(self.mapSize, wallPoints[0], wallPoints[1])  # create the wall def
      self.addWall( newwall )  # add to walls array and index
      newwall.draw(self.image)  # draw on image
    
    if pacdefs.DEBUG_SHOWGRID:
      for gridx in range(1, self.world.cols):
        pygame.draw.line(self.image, (255,0,0), (gridx*grid_cellwidth, 0), (gridx*grid_cellwidth, self.world.rows*grid_cellwidth), 1)
      for gridy in range(1, self.world.rows):
        pygame.draw.line(self.image, (255,0,0), (0, gridy*grid_cellheight), (self.world.cols*grid_cellheight, gridy*grid_cellheight), 1)
    
    
    # Create the sprite rectangle from the image
    self.rect = self.image.get_rect()
    
    # holds current effects happening on the map
    self.effects = []  # array of Effects


  def addWall(self, new_wall):
    # add to array of walls
    self.walls.append( new_wall )
    # add to grid-based index
    (x1,y1) = new_wall.p1
    (x2,y2) = new_wall.p2
    # ensure that x1 <= x2 and y1 <= y2
    if(x1 > x2 or y1 > y2): (x1,y1,x2,y2) = (x2,y2,x1,y1)
    if(x1 == x2): #wall is horizontal
      gridx = min(int(x1 / self.grid_cellwidth), self.world.cols-1)
      yi = y1
      while(yi < y2):
        gridy = min(int(yi / self.grid_cellheight), self.world.rows-1)
        if new_wall not in self.wallgrid[gridy][gridx]: self.wallgrid[gridy][gridx].append(new_wall)
        yi += self.grid_cellheight
    else: # wall is vertical
      gridy = min(int(y1 / self.grid_cellheight), self.world.rows-1)
      xi = x1
      while(xi < x2):
        gridx = min(int(xi / self.grid_cellwidth), self.world.cols - 1)
        if new_wall not in self.wallgrid[gridy][gridx]: self.wallgrid[gridy][gridx].append(new_wall)
        xi += self.grid_cellwidth


  def get_nearby_walls(self, coordsYX):
    nearby_walls = []
    for dy in range(-1,2):
      for dx in range(-1,2):
        y = min(max(coordsYX[0]+dy,0), self.world.rows-1)
        x = min(max(coordsYX[1]+dx,0), self.world.cols-1)
        nearby_walls += self.wallgrid[y][x]
    nearby_walls = list(set(nearby_walls))
    return nearby_walls


  def draw(self, surface):
    # Draw a subsurface of the world map
    # with dimensions of the displaySize
    # centered on the position defined as center (within limits)
    # to the display that has been passed in
    
    #print "DEBUG: Map.draw(): map size is {0}".format(self.image.get_size())
    windowRect = self.player.shape.getWindowRect()
    screenImage = self.image.subsurface( windowRect )
    surface.blit(screenImage, (0,0))
    for effect in self.effects:
      if effect.onScreen(windowRect):
        effect.draw(surface, windowRect)  # NOTE: map effects are drawn directly onto the display !!! coordinates must be localized

  def update(self, ticks):
    # check for current effects to continue
    for i,effect in enumerate(self.effects):
      if effect.update(ticks):
        pass
      else:
        #TODO: does this work?
        del self.effects[i]  # FIXME: is more explicit garbage collection needed here?

  def newMapEffect(self, effect):
    self.effects.append(effect)


  def wallCollision(self, target):
    target_coords = target.get_gridCoordsYX()
    nearby_walls = self.get_nearby_walls(target_coords)
    for wall in nearby_walls:
      a = wall
      b = target
      #We calculate the offset of the second mask relative to the first mask.
      mapTopLeft = b.calcMapTopLeft()
      offset_x = mapTopLeft[0]
      offset_y = mapTopLeft[1]
      # See if the two masks at the offset are overlapping.
      if a.mask.overlap(b.mask, (offset_x, offset_y)):
        #print "DEBUG: Map.wallCollision(): collision detected with wall {0}!".format(wall.rect)
        #print "DEBUG: Map.wallCollision(): target top/bottom, left/right is: {0}, {1}; {2}, {3}".format(target.rect.top, target.rect.bottom, target.rect.left, target.rect.right)
        #print "DEBUG: Map.wallCollision(): wall top/bottom, left/right is: {0}, {1}; {2}, {3}".format(wall.rect.top, wall.rect.bottom, wall.rect.left, wall.rect.right)
        #print "DEBUG: Map.wallCollision(): offset x,y is: {0}, {1}".format(offset_x, offset_y)
        return True
    return False

  def checkTriggers(self, target):
    for art in self.arts:
      a = art
      b = target
      #We calculate the offset of the second mask relative to the first mask.
      mapTopLeft = b.getMapTopLeft()
      offset_x = mapTopLeft[0] - art.x
      offset_y = mapTopLeft[1] - art.y
      #logging.debug("checking for collisions between self ({0}) and art ({1}) at offset {2},{3}".format(target.getMapTopLeft(), (art.x,art.y), offset_x, offset_y))
      # See if the two masks at the offset are overlapping.
      if a.mask.overlap(b.mask, (offset_x, offset_y)):
        #logging.debug("collision detected with art at {0},{1}!".format(art.x, art.y))
        # handle collision
        target.touchArt(art)
    return False

  def startEffect(self, effect_type, effect_options):
    # initialize effect variables
    logging.debug("starting new effect, type: {0}, options={1}".format(effect_type, effect_options))
    self.newMapEffect(Effect(effect_type, effect_options))


  def addShapes(self):
    """adds more shapes to the world"""
    # how many shapes to generate
    # we want roughly one piece per screen
    screenArea = self.displayGridSize[0] * self.displayGridSize[1]
    worldArea = self.world.cols * self.world.rows
    minTotalShapes = 1 + int(worldArea / screenArea)
    #logging.debug("generating {0} shape pieces...".format(minTotalShapes))
    curTotalShapes = 0
    shapes = []
    while curTotalShapes < minTotalShapes:
    # until enough shape generated
      # create new shape, placed randomly
      num_sides = random.randint(3,6)
      newShape = Shape(self.display, self, self.character_size, num_sides)
      newShape.autonomous = True  # all new shapes will be autonomous by default
      
      # add shape to the list of objects
      if(self.world.addObject(newShape)):
        curTotalShapes += 1
        shapes.append(newShape)
        logging.debug ("shape #{0} added to the map, id {1} with position {2} and rect={3}".format(curTotalShapes, newShape, newShape.getMapTopLeft(), newShape.rect))
    # now there's enough shape in the world
    self.shapes = shapes
    return shapes
  # end of Map.addShapes()

  def nearShapes(self, mapCenter, radius, ignore = None):
    matches = []
    for shape in self.shapes:
      if shape == ignore: continue
      # calculate distance between the shapes
      mapTopLeft = shape.getMapTopLeft()
      dx = abs(mapCenter[0] - mapTopLeft[0])
      dy = abs(mapCenter[1] - mapTopLeft[1])
      if(dy == 0):
        dist = dx
      elif(dx == 0):
        dist = dy
      else:
        # a^2 + b^2 = c^2
        dist = math.sqrt(dx*dx+dy*dy)
      if(dist < radius):
        matches.append(shape)
    return matches
  # end of nearShapes()


  def gridToScreenCoord(self, gridCoord):  #TODO: Rename -- add -TopLeft to end of function name
    return (gridCoord[0] * self.grid_cellwidth, gridCoord[1] * self.grid_cellheight)

  def gridToScreenCoordCenter(self, gridCoord):
    return [gridCoord[0] * self.grid_cellwidth + int(self.grid_cellwidth/2), gridCoord[1] * self.grid_cellheight + int(self.grid_cellheight/2)]

  def getSwirlSaturationPercent(self):
    num_shapes = len(self.shapes)
    total_swirls = 0
    for shape in self.shapes:
      total_swirls += len(shape.swirls)
    swirl_saturation_pct = int(100*total_swirls/(num_shapes*3))
    return [total_swirls, num_shapes, swirl_saturation_pct]

# end of class Map


if __name__ == '__main__':
  # Make the display size a member of the class
  display = Pacdisplay((640, 480))
  
  # Initialize pygame
  pygame.init()

  # Set the window title
  pygame.display.set_caption("Map Test")
  
  # Create the window
  window = pygame.display.set_mode(display.getDisplaySize())
    
  # Create the background, passing through the display size
  mapSize = [4*x for x in display.getDisplaySize()]
  map = Map(mapSize, display, display.getDisplaySize()[0]/10, World(mapSize))

  # Draw the background
  map.draw(window, (10,10))
  pygame.display.update()

  done = False
  while not done:
    for event in pygame.event.get():
      if event.type == QUIT:
        pygame.quit()
        sys.exit()
      if event.type == KEYDOWN and event.key == K_DOWN:
        pygame.quit()
        sys.exit()



#EOF