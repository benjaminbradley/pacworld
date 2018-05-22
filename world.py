'''
world.py
An abstract world map using 2d grid coordinates to define the environment symbolically.
'''

import random
import copy
import logging
import math  # for sqrt in move_cost

import pacdefs
import pacglobal
from art import Art


# helper functions
def get_random_value(sizes):
  #picking a size:
  #inputs: size ranges
  #  - gather all weighted values within size ranges
  #  - pick a random value based on all of the weights

  weights = []
  values = []
  
  if 'small' in sizes:
    # "small" size, sidelength distribution:
    #20% 1d
    weights.append(20)
    values.append(1)
    #50% 2d
    weights.append(50)
    values.append(2)
    #30% 3d
    weights.append(30)
    values.append(3)
  
  if 'medium' in sizes:  #"medium" size sidelength distribution:
    #4d  50%
    weights.append(50)
    values.append(4)
    #5d  50%
    weights.append(50)
    values.append(5)

  if 'large' in sizes:  #"large" size sidelength distribution:
    #6d  30%
    weights.append(30)
    values.append(6)
    #7d  40% 
    weights.append(40)
    values.append(7)
    #8d  30%
    weights.append(30)
    values.append(8)

  # add total of all weights
  total_weights = sum(weights)  # reduce(lambda x, y: x + y, weights)
  weighted_result = random.randint(0, total_weights)
  
  result_index = None
  used_weights = 0
  for i in range(len(values)):
    #print "DEBUG: i={0}, in range({1})".format(i, len(values))
    if (used_weights <= weighted_result and weighted_result <= used_weights + weights[i]):
      result_index = i
      break
    used_weights += weights[i]
  
  if result_index == None:
    logging.error ("no results! total_weights = {0}, used_weights={1}, weighted_result={2}".format(total_weights, used_weights, weighted_result))
    return 0
    
  #print "DEBUG: get_random_value(): result_index={0}, values array={1}".format(result_index, values)
  
  #print "DEBUG: result_index={0}, in range({1})".format(result_index, len(values))
  # pick a result from the available weights
  #print "DEBUG: get_random_value(): returning {0}".format(values[result_index])
  return values[result_index]
# END OF get_random_value()



def getsymbol(obj, pos):
  #print "DEBUG: getsymbol({0}, {1})".format(obj, pos)
  if obj.type == pacdefs.TYPE_ROOM:
    if pos in obj.doors.values():
      for doorside, doorpos in obj.doors.items():
        if pos == doorpos:
          if doorside == pacdefs.SIDE_N:
            return 'V'
          elif doorside == pacdefs.SIDE_E:
            return '<'
          elif doorside == pacdefs.SIDE_S:
            return 'A'
          elif doorside == pacdefs.SIDE_W:
            return '>'
      return 'D'
    elif pos[1] == obj.top:
      if pos[0] == obj.left:
        if obj.height == 1: return '['
        elif obj.width == 1: return 'n'
        else: return 'r'
      elif pos[0] == obj.right:
        if obj.height == 1: return ']'
        else: return '7'
      else:
        return '-'
    elif pos[1] == obj.bottom:
      if pos[0] == obj.left:
        if obj.height == 1: return '['
        elif obj.width == 1: return 'u'
        else: return 'L'
      elif pos[0] == obj.right:
        if obj.height == 1: return ']'
        else: return 'J'
      else:
        return '_'
    elif pos[0] == obj.left:
      if obj.width == 1: return 'i'
      else: return 'b'
    elif pos[0] == obj.right:
      return 'd'
    return '.'
  else:
    return obj.symbol


# class for a Room object
class Room():
  def __init__(self, left,top,width,height):
    self.type = pacdefs.TYPE_ROOM
    self.top = top
    self.left = left
    self.width = width
    self.height = height
    self.symbol = pacdefs.ROOM_SYMBOL,
    self.doors = {}  # dictionary of side(int) to (X,Y) tuple of ints
    self.id = None  # assigned when the room is successfully added to the map
    
    # calculated variables derived from attributes
    self.area = self.height * self.width
    self.right = self.left + self.width - 1
    self.bottom = self.top + self.height - 1
  def __str__(self):
    return "<Room#{0}:{1},{2},{3},{4} [{5}]; doors:{6}>".format(self.id, self.left, self.top, self.width, self.height, self.symbol, self.doors)
  def getInsides(self, cols, rows):
    """get an array of room sides which are "inside" the world space"""
    if hasattr(self, 'insides'): return self.insides
    self.insides = []
    if self.top > 0: self.insides.append(pacdefs.SIDE_N)
    if self.bottom < rows-1: self.insides.append(pacdefs.SIDE_S)
    if self.left > 0: self.insides.append(pacdefs.SIDE_W)
    if self.right < cols-1: self.insides.append(pacdefs.SIDE_E)
    return self.insides
  def door_at(self, pos, side):
    """return True if there is a door in this room at the position 'pos' on side 'side'"""
    return (side in self.doors.keys() and self.doors[side] == pos)


class Path():
  def __init__(self, left, top, path_width, path_len, pathDir_h):
    self.type = pacdefs.TYPE_PATH
    self.top = top
    self.left = left
    self.direction_h = pathDir_h
    self.width = path_width
    self.length = path_len
    self.id = None  # assigned when the room is successfully added to the map

    # calculated variables derived from attributes
    self.area = self.length * self.width
    if self.direction_h:
      self.symbol = pacdefs.HPATH_SYMBOL
      self.right = self.left + self.length - 1
      self.bottom = self.top + self.width - 1
    else:
      self.symbol = pacdefs.VPATH_SYMBOL
      self.right = self.left + self.width - 1
      #print "DEBUG: top={0}, length={1}".format(self.top, self.length)
      self.bottom = self.top + self.length - 1

class Intersection():
  def __init__(self, path1, path2, position):
    #NOTE: assumes that exactly one path is vertical and one path is horizontal
    # probably a safe assumption, since INTERSECTION_MIN_OVERLAP prevents intersections near the end of a pathway
    if path1.direction_h:
      hpath = path1
      vpath = path2
    else:
      hpath = path2
      vpath = path1
    self.type = pacdefs.TYPE_INTERSECTION
    self.top = position[1]
    self.left = position[0]
    self.symbol = pacdefs.INTERSECTION_SYMBOL
    self.hpath = hpath
    self.vpath = vpath


class Field():
  def __init__(self, left,top,field_width,field_height):
    self.type = pacdefs.TYPE_FIELD
    self.top = top
    self.left = left
    self.width = field_width
    self.height = field_height
    self.symbol = pacdefs.FIELD_SYMBOL
    self.id = None  # assigned when the room is successfully added to the map
    
    # calculated variables derived from attributes
    self.area = self.height * self.width
    self.right = self.left + self.width - 1
    self.bottom = self.top + self.height - 1



  
def negotiateDoorPlacement(newRoom, adjacent_room, doorpos, doorside):
  #logging.debug ("Door for room {0} was placed next to an adjacent ROOM {1}: {2}".format(newRoom.id, adjacent_room.id, adjacent_room))
  # if a door is placed next to another room, add a door to the other room, or coordinate with location of existing door
  adj_doorside = pacdefs.opposite_side(doorside)
  (doorx,doory) = doorpos
  roomTop = newRoom.top
  roomRight = newRoom.right
  roomBottom = newRoom.bottom
  roomLeft = newRoom.left
  if doorside == 0:
    adj_doorx = doorx
    adj_doory = roomTop-1
  elif doorside == 1:
    adj_doorx = roomRight+1
    adj_doory = doory
  elif doorside == 2:
    adj_doorx = doorx
    adj_doory = roomBottom+1
  elif doorside == 3:
    adj_doorx = roomLeft-1
    adj_doory = doory
  
  if(adj_doorside in adjacent_room.doors.keys()):
    # can we make the doors line up? if so, do it
    adjacent_doorpos = adjacent_room.doors[adj_doorside]
    adjLeft = adjacent_room.left
    adjRight = adjacent_room.right
    adjTop = adjacent_room.top
    adjBottom = adjacent_room.bottom

    if(doorside in [pacdefs.SIDE_N, pacdefs.SIDE_S]):
      my_wallrange = range(roomLeft, roomRight+1)
      adj_wallrange = range(adjLeft, adjRight+1)
    elif(doorside in [pacdefs.SIDE_E, pacdefs.SIDE_W]):
      my_wallrange = range(roomTop, roomBottom+1)
      adj_wallrange = range(adjTop, adjBottom+1)
    overlap = set(my_wallrange) & set(adj_wallrange)

    # scenario 1: IF the other door is next to one of my walls
    #      THEN set my door position to match the existing door
    if(doorside in [pacdefs.SIDE_N, pacdefs.SIDE_S] and adjacent_doorpos[0] in my_wallrange):
      doorx = adjacent_doorpos[0]
    elif(doorside in [pacdefs.SIDE_E, pacdefs.SIDE_W] and adjacent_doorpos[1] in my_wallrange):
      doory = adjacent_doorpos[1]
    
    # scenario 2: IF my door is next to an adjacent wall
    #      THEN set the adjacent room's door to match my door
    elif(doorside in [pacdefs.SIDE_N, pacdefs.SIDE_S] and doorx in adj_wallrange):
      oldy = adjacent_doorpos[1]
      adjacent_room.doors[adj_doorside] = (doorx, oldy)
    elif(doorside in [pacdefs.SIDE_E, pacdefs.SIDE_W] and doory in adj_wallrange):
      oldx = adjacent_doorpos[0]
      adjacent_room.doors[adj_doorside] = (oldx, doory)
    
    # scenario 3: IF there is 1 or more spaces that our walls overlap
    #      THEN move both doors within this space
    elif(len(overlap) > 0):
      overlapmin = min(overlap)
      overlapmax = max(overlap)
      if(doorside in [pacdefs.SIDE_N, pacdefs.SIDE_S]):
        newdoorx = random.randint(overlapmin,overlapmax)
        adjacent_doorpos[0] = doorx = newdoorx
        # update parent data structures
        adjacent_room.doors[adj_doorside] = adjacent_doorpos
      elif(doorside in [pacdefs.SIDE_E, pacdefs.SIDE_W]):
        newdoory = random.randint(overlapmin,overlapmax)
        adjacent_doorpos[1] = doory = newdoory
        # update parent data structures
        adjacent_room.doors[adj_doorside] = adjacent_doorpos
    
    else:  #  (door coordination is impossible...)
      #TODO: add support for multiple doors in each wall, and add the matching door to the adjacent room
      logging.warning ("rendering room: adjacent room already has a door on side {0} & we could NOT coordinate them".format(adj_doorside))
    # end of (trying to coordinate door positions)
    
    #print "DEBUG: World... adding door to adjacent room at {0},{1} on side {2} -- adjacent ROOM {3}; my door is at {4},{5} on side {6} for ROOM {7}".format(adjacent_room.doors[adj_doorside][0], adjacent_room.doors[adj_doorside][1], adj_doorside, adjacent_room.id, doorx,doory,doorside, newRoom.id)
    #print "DEBUG: World... adjacent room ID {0} now has {1} door(s): {2}".format(adjacent_room.id, len(adjacent_room.doors.keys()), adjacent_room.doors)
    
  else:
    adjacent_room.doors[adj_doorside] = (adj_doorx, adj_doory)
    #print "DEBUG: World... adding door to adjacent room at {0},{1} on side {2} -- adjacent ROOM {3}; my door is at {4},{5} on side {6} for ROOM {7}".format(adj_doorx, adj_doory, adj_doorside, adjacent_room.id, doorx,doory,doorside, newRoom.id)
    #print "DEBUG: World... adjacent room ID {0} now has {1} door(s): {2}".format(adjacent_room.id, len(adjacent_room.doors.keys()), adjacent_room.doors)
  # end of (adjacent square is a room)

  # update the grid with the door location
  #logging.debug("adding door to room on side {0}".format(doorside))
  newRoom.doors[doorside] = (doorx, doory)
  door_placed = True
# end of negotiateDoorPlacement()






# The class to create a symbolic 'world', will be translated into a map
class World():
  
  def __init__(self, gridDisplaySize):
    # input: gridDisplaySize - the world is created as a 2-dimensional grid according with HxW as passed in
    # variables:
    #  grid - a grid of strings, each string identifying the contents of each grid square
    # output:
    #  objects - an array of the objects existing in the world map, with their characteristics
    
    # initialize world attributes
    (self.cols, self.rows) = gridDisplaySize
    self.totalArea = self.rows * self.cols
    # initialize data storage variables
    self.grid = [[pacdefs.SYMBOL_CLEAR for x in range(self.cols)] for y in range(self.rows)]
    
    # calculate intermediary vars
    shortside = min(self.rows, self.cols)
    longside = max(self.rows, self.cols)
    longdir_is_h = (shortside == self.rows)  # true = horizontal
    
        
    ###################################################
    # generate a new world according to the algorithm
    ###################################################
    
    self.objects = [] # List to hold the objects generated in the world (pathways, fields, etc)
    self.objectId_autoIncrement = 0


    # step 1: generate pathways
    
    #  goal is to have between 2s+o and s+2o total length of pathways
    a = int(shortside + 2*longside)
    b = int(2*shortside + longside)
    minTotalPaths = min(a,b)
    maxTotalPaths = max(a,b)
    #curTotalPaths = 0
    #TODO: cleanup vars above
    curTotalPathArea = 0
    minPathArea = int(self.totalArea*pacdefs.PATH_AREA_MIN/100)
    numPaths_longWays = 0
    numPaths_shortWays = 0


    while(curTotalPathArea < minPathArea):
      pacglobal.checkAbort()
      #print "DEBUG: World.__init__(): current total path area ({0}, {1}%) hasn't met minimum path area ({2}, {3}%)".format(curTotalPathArea, int(100*curTotalPathArea/self.totalArea), int(self.totalArea*PATH_AREA_MIN/100), PATH_AREA_MIN)
      
      # create a new path & add to the world
      
      # generate random pathway
      
      # path direction:
      pathDir_h = (random.randint(0,1) == 1)  # random dir is binary, T=horizontal
      #    a maximum of 2 (or 3 with a separation clause?) pathways may be parallel to s
      if numPaths_shortWays >= 2 and (pathDir_h != longdir_is_h):
        #    the others must be parallel to o
        #print "DEBUG: World.__init__(): too many shortWays ({0}) paths, forcing longways".format(numPaths_shortWays)
        pathDir_h = longdir_is_h
            
      path_width = get_random_value('small')
      # path length
      #minPath = int(shortside)  #  minimum length o/2 (where o is the longest of h or w)
      minPath = 4
      #  maximum length s (where s is the shortest of h or w)
      maxPath = int(longside)
      path_len = random.randint(minPath,maxPath)
      
      # placement
      if(pathDir_h):  # horizontal placement
        top = random.randint(0, self.rows-path_width)
        if path_len > self.cols: path_len = self.cols
        if self.cols == path_len: left = 0
        else: left = random.randint(0, self.cols-path_len)
      else:  # vertical placement
        if path_len > self.rows: path_len = self.rows
        if self.rows == path_len: top = 0
        else: top = random.randint(0, self.rows-path_len)
        left = random.randint(0, self.cols-path_width)
      
      newPath = Path(left,top,path_width,path_len,pathDir_h)
      #print "DEBUG: World.__init__(): new path placed at {0},{1}".format(left,top)
      #print "DEBUG: World.__init__(): new path: {0}".format(newPath)

      # check for obustructions, correct if possible
      newid = self.addObject(newPath)
      if(newid):
        curTotalPathArea += newPath.area
        if pathDir_h == longdir_is_h:
          numPaths_longWays += 1
        else:
          numPaths_shortWays += 1
        #print "DEBUG: World.__init__(): {0} shortWays paths, {1} longways paths".format(numPaths_shortWays, numPaths_longWays)
      # DEBUG: show current map
      #print "DEBUG: World.__init__(): world grid is:\n{0}".format(self.to_s())
    # end of (generate pathways)
    logging.debug ("final total path area is {0} ({1}%) from {2} paths. Goal is minimum {3}".format(curTotalPathArea, 100*curTotalPathArea/self.totalArea, numPaths_longWays+numPaths_shortWays, minPathArea))
    

    # step 2. generate fields
    # basic implementation: randomly place fields
    curTotalFieldArea = 0
    numFields = 0
    minFieldArea = int(self.totalArea*pacdefs.FIELD_AREA_MIN/100)

    while(curTotalFieldArea < minFieldArea):
      pacglobal.checkAbort()
      #print "DEBUG: World.__init__(): current total field area ({0}, {1}%) hasn't met minimum ({2}, {3}%)".format(curTotalFieldArea, int(100*curTotalFieldArea/self.totalArea), int(self.totalArea*FIELD_AREA_MIN/100), PATH_AREA_MIN)
      
      # create a new field & add to the world
      
      # generate random field
      
      # field Size
      field_sidelength = get_random_value(['medium', 'large'])
      # it will be square
      
      #print "DEBUG: World.__init__(): field size is {0} square".format(field_sidelength)
      
      # placement
      if field_sidelength >= self.rows or field_sidelength >= self.cols: field_sidelength = min(self.rows, self.cols) -1  # just in case
      #else: 
      top = random.randint(0, self.rows-field_sidelength)
      left = random.randint(0, self.cols-field_sidelength)

      newField = Field(left,top,field_sidelength,field_sidelength)
      #print "DEBUG: World.__init__(): new path placed at {0},{1}".format(left,top)
      #print "DEBUG: World.__init__(): new path: {0}".format(newPath)

      # check for obustructions, correct if possible
      newid = self.addObject(newField)
      if(newid):
        curTotalFieldArea += newField.area
        numFields += 1
        #print "DEBUG: World.__init__(): {0} shortWays paths, {1} longways paths".format(numPaths_shortWays, numPaths_longWays)

      # DEBUG: show current map
      #print "DEBUG: World.__init__(): world grid is:\n{0}".format(self.to_s())
    # end of (adding fields)
    logging.debug ("final total field area is {0} ({1}%) from {2} fields. Goal is minimum {3}".format(curTotalFieldArea, 100*curTotalFieldArea/self.totalArea, numFields, minFieldArea))
    
    
    #TODO:
    #  if two or more pathways could be connected with a field, do it
    

    # step 3. populate rooms around fields and pathways
    #  - each door must lead to either a field, a pathway, or another room
    curTotalRoomArea = 0
    minRoomArea = int(self.totalArea*pacdefs.ROOM_AREA_MIN/100)
    
    roomPlacementFailures = 0
    ROOM_PLACEMENT_MAX_FAILURES = 100
    while(curTotalRoomArea < minRoomArea and roomPlacementFailures < ROOM_PLACEMENT_MAX_FAILURES):
      pacglobal.checkAbort()
      #print "DEBUG: World.__init__(): current total room area ({0}, {1}%) hasn't met minimum room area ({2}, {3}%)".format(curTotalRoomArea, int(100*curTotalRoomArea/self.totalArea), int(self.totalArea*ROOM_AREA_MIN/100), ROOM_AREA_MIN)
      
      # create a new room & add to the world
      
      # generate random room
      
      # room dimensions
      room_width = get_random_value(['small', 'medium'])
      room_height = get_random_value(['small', 'medium'])
      
      #print "DEBUG: World.__init__(): room size is {0} high by {1} wide".format(room_height, room_width)
      
      # placement
      if room_width > self.rows: room_width = self.rows
      if self.rows == room_height: top = 0
      else: top = random.randint(0, self.rows-room_height)
      left = random.randint(0, self.cols-room_width)
      
      newRoom = Room(left,top,room_width,room_height)
      #print "DEBUG: World.__init__(): new room placed at {0},{1}".format(left,top)
      #print "DEBUG: World.__init__(): new room: {0}".format(newRoom)
      
      # check for obustructions
      newid = self.addObject(newRoom)
      if(newid):
        curTotalRoomArea += newRoom.area
      else:
        roomPlacementFailures += 1
        continue
      
      # determine orientation (place door(s))
      
      # a door is a square on the outside edge of the room which has adjacent a path or field (or intersection)
      door_placed = False
      roomLeft = newRoom.left
      roomRight = newRoom.right
      roomTop = newRoom.top
      roomBottom = newRoom.bottom
      logging.debug ("room:top={0}, bottom={1}, left={2}, right={3}  ROOM {4}".format(roomTop, roomBottom, roomLeft, roomRight, newRoom.id))
      squares_checked = {}  # hash of X,Y coordinates to boolean, dictionary
      while not door_placed:
        # pick a side to pick a random square from
        # side: 0 = North, 1 = East, South, West
        if newRoom.width == 1:
          if random.randint(0,1) == 0:  doorside = pacdefs.SIDE_E
          else: doorside = pacdefs.SIDE_W
          total_edge_squares = newRoom.height
        elif newRoom.height == 1:
          if random.randint(0,1) == 0:  doorside = pacdefs.SIDE_N
          else: doorside = pacdefs.SIDE_S
          total_edge_squares = newRoom.width
        else:
          doorside = pacdefs.SIDES[random.randint(0,len(pacdefs.SIDES)-1)]
          total_edge_squares = newRoom.width * 2 + newRoom.height * 2
          #print "DEBUG: World.__init(): total_edge_squares={0}".format(total_edge_squares)
        # choose a random square on that side
        if doorside == 0:
          doorx = random.randint(roomLeft, roomRight)
          doory = roomTop
        elif doorside == 1:
          doorx = roomRight
          doory = random.randint(roomTop, roomBottom)
        elif doorside == 2:
          doorx = random.randint(roomLeft, roomRight)
          doory = roomBottom
        elif doorside == 3:
          doorx = roomLeft
          doory = random.randint(roomTop, roomBottom)
        #TODO: prefer not to place doors on a corner
        #print "DEBUG: World.__init(): room:trying door at {0},{1}".format(doorx, doory)
        
        # only check each square once
        index = str(doorside)+':'+str(doorx)+'x'+str(doory)
        if index in squares_checked.keys():
          #print "DEBUG: already checked square {0}".format(index)
          continue
        else:
          squares_checked[index] = True  # mark this square as checked
          if(len(squares_checked.keys()) == total_edge_squares):
            #logging.debug ("checked all possible room squares for door placement, none qualify... will need to place door randomly for ROOM {0}.".format(newRoom.id))
            # if a door is not placed by any other means, do so now by random selection:
            # pick a random side
            #print "DEBUG placing door on random side within {0}".format(insides)
            insides = newRoom.getInsides(self.cols, self.rows)
            doorside = insides[random.randint(0, len(insides)-1)]
            # pick a random space on that side
            if doorside in [pacdefs.SIDE_N,pacdefs.SIDE_S]:
              doorx = random.randint(roomLeft, roomRight)
              if doorside == pacdefs.SIDE_N: doory = roomTop
              else: doory = roomBottom  # doorside == pacdefs.SIDE_S
            else:  # doorside in [pacdefs.SIDE_E,pacdefs.SIDE_W]
              doory = random.randint(roomTop, roomBottom)
              if doorside == pacdefs.SIDE_E: doorx = roomRight
              else: doorx = roomLeft  # doorside == pacdefs.SIDE_W
            
            newRoom.doors[doorside] = (doorx, doory)
            #print "DEBUG: ROOM {0}: new door placed randomly at {1} on side {2}".format(newRoom.id, newRoom.doors[doorside], doorside)
            door_placed = True
            # DON'T continue - we need to check for door in adjacent room
          # end of (we've checked all squares, assign one randomly)
          else:
            # we're checking a random square for door placement
            
            # it should not be against the edge of the map
            if doorx == 0 or doorx == self.cols-1 or doory == 0 or doory == self.rows-1:
              #print "DEBUG: door placed against map edge, aborting"
              continue
        
        # VALIATION RULE: the door must be adjacent to a pathway or field
        
        # get the adjacent square type
        if doorside == 0:
          adj_doorx = doorx
          adj_doory = roomTop-1
        elif doorside == 1:
          adj_doorx = roomRight+1
          adj_doory = doory
        elif doorside == 2:
          adj_doorx = doorx
          adj_doory = roomBottom+1
        elif doorside == 3:
          adj_doorx = roomLeft-1
          adj_doory = doory
        
        #print "DEBUG: ROOM {0} door placement: checking adjacent square at {1},{2}".format(newRoom.id, adj_doorx, adj_doory)
        adjacent_square = self.grid[adj_doory][adj_doorx]
        
        if adjacent_square == None:
          if door_placed:
            # we will allow a door next to undefined territory if there are no better options
            #print "DEBUG: allowing door next to nothing due to lack of better options"
            continue
          else:
            #print "DEBUG: adjacent square is undefined, disallowing door"
            continue
        
        if adjacent_square.type not in [pacdefs.TYPE_PATH, pacdefs.TYPE_FIELD, pacdefs.TYPE_INTERSECTION, pacdefs.TYPE_ROOM]:
          # not a qualifying adjacentcy type
          #print "DEBUG: adjacent square is not allowed ({0})",format(adjacent_square.type)
          if door_placed:
            #print "DEBUG: we've tried placing a door randomly, and it's no good. aborting"
            continue
          
        if adjacent_square.type == pacdefs.TYPE_ROOM:
          #CHECKADJDOOR (but this one is in reverse, newRoom = self, existing = adjacent)
          #TODO: refactor
          #FUNCTION: negotiateDoorPlacement(newRoom, adjacent_room, doorpos)
          negotiateDoorPlacement(newRoom, adjacent_square, (doorx,doory), doorside)
          #TODO: does this return a status? if so what happens with it?
          
        else:
          # update the grid with the door location
          newRoom.doors[doorside] = (doorx, doory)
          door_placed = True
      # end of (while not door_placed)
      
      
      # so, the door has been placed now.
      # check to make sure we didn't cover over an existing door, and if we did, do the adjacent-door compatibility test
      for side in list(set(pacdefs.SIDES) - set([doorside])):
        #  check the other 3 sides (insides which are not the doorside)
        if side not in newRoom.getInsides(self.cols, self.rows): continue
        #   check every adjacent square on that side
        if side == pacdefs.SIDE_N:
          adj_yrange = [roomTop - 1]
          adj_xrange = range(roomLeft, roomRight+1)
        elif side == pacdefs.SIDE_S:
          adj_yrange = [roomBottom + 1]
          adj_xrange = range(roomLeft, roomRight+1)
        elif side == pacdefs.SIDE_E:
          adj_yrange = range(roomTop, roomBottom)
          adj_xrange = [roomRight + 1]
        elif side == pacdefs.SIDE_W:
          adj_yrange = range(roomTop, roomBottom)
          adj_xrange = [roomLeft - 1]
        #checked_rooms = {}  # dictionary of roomID to boolean
        adj_doorside = (side + 2) % 4
        for adj_doorx in adj_xrange:
          for adj_doory in adj_yrange:
            adj_doorpos = (adj_doorx, adj_doory)
            #print "DEBUG: checking adjacent square at {0} to prevent covering existing doors".format(adj_doorpos)
            adjacent_square = self.grid[adj_doory][adj_doorx]
            # if we're next to a room
            if adjacent_square != None and adjacent_square.type == pacdefs.TYPE_ROOM:
              ## and we haven't checked this room before
              #if adjacent_square.id in checked_rooms.keys(): continue
              # check to see if there is a door in this square
              if adj_doorside in adjacent_square.doors.keys() and adjacent_square.doors[adj_doorside] == adj_doorpos:
                # if there is a door here
                #print "DEBUG: found an existing door in ROOM {0} at {1} on side {2}".format(adjacent_square.id, adj_doorpos, adj_doorside)
                # check for door compatibility
                negotiateDoorPlacement(adjacent_square, newRoom, adj_doorpos, adj_doorside)
      
      # room completely placed on map
      roomPlacementFailures = 0

      # DEBUG: show current map
      #logging.debug ("World.__init__(): world grid is:\n{0}".format(self.to_s()))
    
    if(curTotalRoomArea < minRoomArea):
      logging.debug("Exceeded room placement failure threshhold {0} with only {1} total room area (minimum should be {2})".format(ROOM_PLACEMENT_MAX_FAILURES, curTotalRoomArea, minRoomArea))

    # step 4. place rocks
    #  - 4 or 5 randomly around the map? maybe skip this step? or it's used to identify inaccessible enclosed spaces?
    
    # polishing pass to extend pathways to whatever is at the logical end
    # if all spaces are empty, or only other path crossing, extend the path
    # continue until non-path obstruction or edge-of-map is hit
    for path in self.objects:
      if path.type != pacdefs.TYPE_PATH: continue
      # check either end of path
      for side in [-1,1]:
        # handle horizontal paths
        if path.direction_h:
          bottom = path.top + path.width - 1
          right = path.left + path.length - 1
          if side == -1: startx = path.left  # check left side
          else: startx = right # side == 1
          dx = side
          extraclear = True # is this extra row/column clear of non-path obstacles?
          while extraclear:
            if(startx+dx < 0 or self.cols <= startx+dx):
              break
            for y in range(path.top, bottom+1):
              # check grid contents at startx + dx, y
              gridsquare = self.grid[y][startx + dx]
              if gridsquare != None and gridsquare.type != pacdefs.TYPE_PATH:
                # if non-path obstacle encountered
                extraclear = False
            if extraclear == True: #for the whole row/col, then
              # extend the path into this row/column
              if side == -1: path.left -= 1
              path.length += 1
              for y in range(path.top, bottom+1):
                self.grid[y][startx + dx] = path
              #   and move on to the next adjacent row/col, if it's not beyond the edge of the map
              dx += side
        else: # vertical paths
          bottom = path.top + path.length - 1
          right = path.left + path.width - 1
          if side == -1: starty = path.top  # check top side
          else: starty = bottom # side == 1
          dy = side
          extraclear = True # is this extra row/column clear of non-path obstacles?
          while extraclear:
            if(starty+dy < 0 or self.rows <= starty+dy):
              break
            for x in range(path.left, right+1):
              # check grid contents at x, starty + dy
              gridsquare = self.grid[starty + dy][x]
              if gridsquare != None and gridsquare.type != pacdefs.TYPE_PATH:
                # if non-path obstacle encountered
                extraclear = False
            if extraclear == True: #for the whole row/col, then
              # extend the path into this row/column
              if side == -1: path.top -= 1
              path.length += 1
              for x in range(path.left, right+1):
                self.grid[starty + dy][x] = path
              #   and move on to the next adjacent row/col, if it's not beyond the edge of the map
              dy += side
    
  # end of World.__init__()
  
  
  def addArt(self, themap):
    """adds random art to the world"""
    # how much art to generate
    # we want roughly one piece per 2 screens
    screenArea = themap.displayGridSize[0] * themap.displayGridSize[1]
    worldArea = self.cols * self.rows
    minTotalArts = 1 + int(worldArea / (screenArea * 2))
    #logging.debug("generating {0} art pieces...".format(minTotalArts))
    curTotalArts = 0
    themap.arts = []
    art_locations = []  # list of (x,y) tuples, locations of placed art
    artStyleCount = {}
    while curTotalArts < minTotalArts:
    # until enough art generated
      pacglobal.checkAbort()
      placement_ok = False
      # calculate art style weights based on existing placements
      art_style_weights = []
      for art_style in pacdefs.STYLES:
        # ensure one of each before duplicating
        if(len(artStyleCount.keys()) < len(pacdefs.STYLES)):
          if(art_style in list(artStyleCount.keys())): weight = 0
          else: weight = 1
        else:
          placed = artStyleCount.get(art_style, 0)
          remaining = minTotalArts - placed
          weight = remaining / minTotalArts
        art_style_weights.append(weight)
      new_art_style = random.choices(pacdefs.STYLES, art_style_weights)[0]
      #logging.debug("With current placement {0}, weights are {1} and this choice is {2}".format(artStyleCount, art_style_weights, new_art_style))
      if new_art_style not in list(artStyleCount.keys()):
        artStyleCount[new_art_style] = 0
      artStyleCount[new_art_style] += 1
      # create new art
      newArt = Art(themap, 0, 0, new_art_style)  # use dummy position (0,0) until placement is finalized
      placement_attempts = 0
      while not placement_ok:
        placement_attempts += 1
        artx = random.randint(0, self.cols-1)
        arty = random.randint(0, self.rows-1)
        newart_location = (artx,arty)
        # check art placement
        # make sure there is not already art in this square...
        if newart_location in art_locations:
          # collision with existing art, try again
          continue
        # what is at this location?
        current_contents = self.grid[arty][artx]
        if current_contents is not None and current_contents.type in [pacdefs.TYPE_FIELD, pacdefs.TYPE_ROOM]:
          #only place art in rooms or fields (not on pathways)
          newArt.setPos(artx, arty)
          # check density
          if len(newArt.art_onscreen()) < int(float(placement_attempts) / 10) + 1:  # limit of arts on the same screen
            placement_ok = True
          else:
            logging.debug("Art #{0} - placement attempt {1} failed, threshold is {2}".format(curTotalArts+1, placement_attempts, int(placement_attempts / 10) + 1))
      # add art to the list of objects
      if(self.addObject(newArt)):
        curTotalArts += 1
        themap.arts.append(newArt)
        art_locations.append(newart_location)
        logging.debug ("added {0} to the map at {1}".format(str(newArt), newart_location))
    # now there's enough art in the world
    return themap.arts
  # end of World.addArt()
  
  def copyGrid(self):
    # a deepcopy is too deep - we want to retain references to all the existing world objects (paths, rooms, etc)
    # a shallow copy is not deep enough - it only copies the first level (i.e. rows)
    # so we implement a manual shallow copy to ensure that all rows AND columns are copied, with references to the existing objects
    newGrid = []
    for r in range(self.rows):
      newGrid.append(copy.copy(self.grid[r]))
    return newGrid
  # end of World.copyGrid()
  
  def addObject(self, newObject):
    # if this is an object that gets placed on the world
    if(newObject.type in pacdefs.WORLD_OBJ_TYPES):
      # copy current grid
      newGrid = self.copyGrid()
    
      if(newObject.type == pacdefs.TYPE_FIELD):
        basex = newObject.left
        basey = newObject.top
        if(newObject.width <= 0):
          logging.error ("field width must be greater than 0!")
          exit()
        for w in range(newObject.width):
          posx = basex + w
          for h in range(newObject.height):
            posy = basey + h
        
            # check for obstructions
            if self.grid[posy][posx] != pacdefs.SYMBOL_CLEAR:
              #print "WARN: field obstructed at {0},{1}".format(posx,posy)
              obstruction = self.grid[posy][posx]
              if obstruction.type in [pacdefs.TYPE_PATH, pacdefs.TYPE_INTERSECTION]:
                # field overwrites paths and intersections
                newGrid[posy][posx] = newObject
                continue
              
              # otherwise, obstruction kills the road
              return False
            else:
              # no obstructions, continue:
            
              #print "DEBUG: added new symbol at {0},{1}".format(posx,posy)
              newGrid[posy][posx] = newObject
      
      
      elif(newObject.type == pacdefs.TYPE_ART):
        curSquare = newGrid[newObject.top][newObject.left]
        if curSquare == None:  return False  # won't place art in no-mans-land
        # otherwise, proceed
        # object is added to the world and granted a unique ID via code below
        # do not add to world grid as background structure must be preserved  -- newGrid[newObject.top][newObject.left] = newObject

      elif(newObject.type == pacdefs.TYPE_PATH):
        x = newObject.left
        y = newObject.top
        if(newObject.length <= 0):
          logging.error ("path length must be greater than 0!")
          exit()
        #print "DEBUG: adding path, ranging i to {0}...".format(newObject['length'])
        adjacent_paths = {}  # dictionary of object IDs (for easy uniquifying)
        intersected_paths = {} # dictionary of object IDs (for easy uniquifying)
        for i in range(newObject.length):
          # check for adjacencies
          if newObject.direction_h:
            adjx = x + i
            adjy1 = y - 1
            adjy2 = y + newObject.width
            if adjy1 >= 0 and self.grid[adjy1][adjx] != None and self.grid[adjy1][adjx].type == pacdefs.TYPE_PATH:
              #print "WARN: adjacent path at {0},{1}".format(adjx,adjy1)
              adjacent_paths[self.grid[adjy1][adjx].id] = True
            elif adjy2 < self.rows and self.grid[adjy2][adjx] != None and self.grid[adjy2][adjx].type == pacdefs.TYPE_PATH:
              #print "WARN: adjacent path at {0},{1}".format(adjx,adjy2)
              adjacent_paths[self.grid[adjy2][adjx].id] = True
          else:
            adjy = y + i
            adjx1 = x - 1
            adjx2 = x + newObject.width
            if adjx1 >= 0 and self.grid[adjy][adjx1] != None and self.grid[adjy][adjx1].type == pacdefs.TYPE_PATH:
              #print "WARN: adjacent path at {0},{1}".format(adjx1,adjy)
              adjacent_paths[self.grid[adjy][adjx1].id] = True
            elif adjx2 < self.cols and self.grid[adjy][adjx2] != None and self.grid[adjy][adjx2].type == pacdefs.TYPE_PATH:
              #print "WARN: adjacent path at {0},{1}".format(adjx2,adjy)
              adjacent_paths[self.grid[adjy][adjx2].id] = True
        
          #print "DEBUG: ranging j to {0}...".format(newObject['width'])
          for j in range(newObject.width):
            if newObject.direction_h:
              posx = x + i
              posy = y + j
              newObject.symbol = pacdefs.HPATH_SYMBOL
            else:
              posx = x + j
              posy = y + i
              newObject.symbol = pacdefs.VPATH_SYMBOL
            # check for obstructions
            if self.grid[posy][posx] != pacdefs.SYMBOL_CLEAR:
              #print "WARN: path obstructed at {0},{1}".format(posx,posy)
              obstruction = self.grid[posy][posx]
              if obstruction.type == pacdefs.TYPE_INTERSECTION:
                #print "DEBUG: obstruction is an intersection, ignored at {0},{1}".format(posx,posy)
                # intersection is a freebie, unchanged, but does not block
                continue
              if obstruction.type in [pacdefs.TYPE_PATH]:
                #  ok for large pathways to intersect in the middle
                im_large =  (newObject.length >= pacdefs.LARGE_PATH_MIN)
                its_large = (obstruction.length >= pacdefs.LARGE_PATH_MIN)
                if im_large and its_large:
                  #print "DEBUG: testing intersection of 2 large paths"
                  # intersection should be at least INTERSECTION_MIN_OVERLAP=4 away from either end for both pathways
                  # NOTE: intersection point should be adjusted by path width
                  # check current path
                  if i < pacdefs.INTERSECTION_MIN_OVERLAP: return False
                  if i > newObject.length-pacdefs.INTERSECTION_MIN_OVERLAP: return False
                  # check other path
                  if newObject.direction_h:  # new path is horizontal, obstruction is vertical
                    # check 'top' end first
                    if posy < obstruction.top+pacdefs.INTERSECTION_MIN_OVERLAP: return False
                    # check bottom
                    if posy > obstruction.top+obstruction.length-pacdefs.INTERSECTION_MIN_OVERLAP: return False
                  else:  # new path NOT horizontal, so obstruction is horizontal
                    # check left
                    if posx < obstruction.left+pacdefs.INTERSECTION_MIN_OVERLAP: return False
                    # check right
                    if posx > obstruction.left+obstruction.length-pacdefs.INTERSECTION_MIN_OVERLAP: return False
                
                  # all qualifiers passed for large-large intersection, make it so!
                  #print "DEBUG: intersection happening at {0},{1}".format(posx, posy)
                  newGrid[posy][posx] = Intersection(newObject, obstruction, (posx, posy))
                  intersected_paths[obstruction.id] = True
                  continue
              
              
                # medium pathways should only touch at corners at their ends
                #TODO
              
              # otherwise, obstruction kills the road
              return False
            else:
              # no obstructions, continue:
            
              #print "DEBUG: added new symbol at {0},{1}".format(posx,posy)
              newGrid[posy][posx] = newObject
          

        # check cumulative obstructions
        if len(adjacent_paths) > 0 and len(adjacent_paths) != len(intersected_paths):
          #print "DEBUG: more adjacent paths ({0}) than intersections ({1}), throwing out".format(len(adjacent_paths), len(intersected_paths))
          return False

    
      elif(newObject.type == pacdefs.TYPE_ROOM):
        basex = newObject.left
        basey = newObject.top
        if(newObject.width <= 0):
          logging.error ("room width must be greater than 0!")
          exit()
        if(newObject.height <= 0):
          logging.error ("room height must be greater than 0!")
          exit()
        for w in range(newObject.width):
          posx = basex + w
          for h in range(newObject.height):
            posy = basey + h
          
            # check for obstructions
            if self.grid[posy][posx] != pacdefs.SYMBOL_CLEAR:
              # all obstructions kill a room
              return False
            
            else:
              # no obstructions, continue:
            
              #print "DEBUG: added new symbol at {0},{1}".format(posx,posy)
              newGrid[posy][posx] = newObject
          # end for h in height
        # end for w in width
      
      else:
        logging.critical ("Unknown type {0}".format(newObject.type))
        exit()
    
      # if everything works out ok, save the new grid
      self.grid = newGrid
      #print "DEBUG: object added, new grid is: \n{0}".format(self.to_s())
    #else:  # end of (if object gets added to the world grid)
      #self.dynamicObjects.append(newObject)
      
    self.objectId_autoIncrement += 1
    newObject.id = self.objectId_autoIncrement
    logging.debug ("'{0}' object added, new objId is: {1}".format(newObject.type, newObject.id))
    self.objects.append(newObject)
    return newObject.id  # success
  # end of World.addObject()

  def to_s(self, highlights = []):
    """converts world grid to a string for display to console"""
    gridstr = '_'
    for i in range(self.cols):  # add number ruler at top
      gridstr += str(i%10)
    gridstr += "\n"
    for i,row in enumerate(self.grid):
      disprow = [ '@' if (i,j) in highlights else pacdefs.SYMBOL_BACKGROUND if obj == pacdefs.SYMBOL_CLEAR else getsymbol(obj, (j, i)) for j,obj in enumerate(row) ]
      rowstr = ''.join(disprow)
      gridstr += str(i%10)+rowstr+str(i%10)+"\n"
    gridstr += "_"
    for i in range(self.cols):  # add number ruler at bottom
      gridstr += str(i%10)
    return gridstr


  def map_distance(self, c1, c2):
    """euclidian distance between the two pairs of map coordinates"""
    return int(math.sqrt((c1[0] - c2[0]) ** 2 + (c1[1] - c2[1]) ** 2))

  #####################################
  # PATHFINDING METHODS
  #####################################
  
  def move_cost(self, c1, c2):
    """ Compute the cost of movement from one coordinate to
    another. 
    The cost is the Euclidean distance.
    """
    # just check first/last squares to save time
    c1gridx = min(c1[1], self.cols-1)
    c1gridy = min(c1[0], self.rows-1)
    c2gridx = min(c2[1], self.cols-1)
    c2gridy = min(c2[0], self.rows-1)
    first_square = self.grid[c1gridy][c1gridx]
    last_square = self.grid[c2gridy][c2gridx]
    # add a multiplier for unmapped terrain, to encourage AIs to stick to pathways
    mult = 1
    if(first_square == None): mult += 0.5
    if(last_square == None): mult += 0.5
    dist = math.sqrt((c1[0] - c2[0]) ** 2 + (c1[1] - c2[1]) ** 2)
    return dist * mult

  def _successors__check_adjacent__accessible(self,coord_a,coord_b):
    if not (0 <= coord_b[0] <= self.rows - 1 and
        0 <= coord_b[1] <= self.cols - 1):
      # illegal square, outside of world map
      return False
    # if it's inside the map, check if there's a wall between the two squares:
    current_square = self.grid[coord_a[0]][coord_a[1]]
    adjacent_square = self.grid[coord_b[0]][coord_b[1]]
    current_room = (current_square != None and current_square.type == pacdefs.TYPE_ROOM)
    adjacent_room = (adjacent_square != None and adjacent_square.type == pacdefs.TYPE_ROOM)
    #if c == (1,9) and coord_b[0] == 0 and coord_b[1] == 9:
    #  logging.debug("DEBUG CASE: current_square={0}, adjacent_square={1}, curroom={2},adjroom={3}".format(current_square,adjacent_square,current_room,adjacent_room))
    # if neither square is a room, it's clear
    if not current_room and not adjacent_room:
      return True
    else:
      # one or both squares is a room
      # if both squares are room, and they are in the same room, it's clear
      if current_room and adjacent_room and current_square.id == adjacent_square.id:
        return True
      else:
        # otherwise, check to see if there is a door between the two squares
        if coord_b[0] < coord_a[0]: cursidedir = pacdefs.SIDE_N
        elif coord_b[0] > coord_a[0]: cursidedir = pacdefs.SIDE_S
        elif coord_b[1] > coord_a[1]: cursidedir = pacdefs.SIDE_E
        elif coord_b[1] < coord_a[1]: cursidedir = pacdefs.SIDE_W
        else:
          logging.error("[FORMAT (y,x)] couldn't determine orientation of current ({0}) vs adjacent ({1}) squares".format(coord_a, (coord_b[0],coord_b[1])))
        adjsidedir = pacdefs.opposite_side(cursidedir)
        # each square is accessible if: not a room OR room with a door in the right place
        current_square_accessible = not current_room or (current_square != pacdefs.SYMBOL_CLEAR and current_square.type == pacdefs.TYPE_ROOM and current_square.door_at((coord_a[1],coord_a[0]), cursidedir))
        adjacent_square_accessible = not adjacent_room or (adjacent_square != pacdefs.SYMBOL_CLEAR and adjacent_square.type == pacdefs.TYPE_ROOM and adjacent_square.door_at((coord_b[1],coord_b[0]), adjsidedir))
        if(current_square_accessible and adjacent_square_accessible):
          return True
        else:
          return False
        # if there is not a door, it's blocked
  # end of self._successors__check_adjacent__accessible()

  def successors(self, c):
    """ Compute the successors of coordinate 'c': all the 
    coordinates that can be reached by one step from 'c'.
    """
    slist = []
    diagonals_accessible_vert = []
    diagonals_accessible_horiz = []
    
    # check verticals first, 
    for drow in (-1, 1):
      dcol = 0
      newrow = c[0] + drow
      newcol = c[1] + dcol
      newcoord = (newrow, newcol)
#      logging.debug("[FORMAT: (y,x)]a checking successors for {0}: checking {1}".format(c, newcoord))
      if(self._successors__check_adjacent__accessible(c,newcoord)):
        slist.append(newcoord)
        # then check diagonals from verticals (if possible)
        for dcol in (-1, 1):
          newrow = c[0] + drow
          newcol = c[1] + dcol
          diagcoord = (newrow,newcol)
#          logging.debug("[FORMAT: (y,x)]b checking successors for {0}: checking {1}".format(newcoord, (newrow,newcol)))
          if(self._successors__check_adjacent__accessible(newcoord,diagcoord)):
            diagonals_accessible_vert.append(diagcoord)
    

    # check horizontals
    for dcol in (-1, 1):
      drow = 0
      newrow = c[0] + drow
      newcol = c[1] + dcol
#      logging.debug("[FORMAT: (y,x)]c checking successors for {0}: checking {1}".format(c, (newrow,newcol)))
      if(self._successors__check_adjacent__accessible(c,(newrow,newcol))):
        slist.append((newrow, newcol))
        # finally, if for any diagonals that weren't accessible via verticals, check diagonals from horizontals
        newcoord = (newrow, newcol)
        for drow in (-1, 1):
          newrow = c[0] + drow
          newcol = c[1] + dcol
          diagcoord = (newrow,newcol)
#          logging.debug("[FORMAT: (y,x)]d checking successors for {0}: checking {1}".format(newcoord, (newrow,newcol)))
          if(self._successors__check_adjacent__accessible(newcoord,diagcoord)):
            diagonals_accessible_horiz.append(diagcoord)

    diagonals_accessible = list(set(diagonals_accessible_vert) & set(diagonals_accessible_horiz))
    #logging.debug("Intersection of V-diag [{0}] & H-diag [{1}] is: {2}".format(diagonals_accessible_vert, diagonals_accessible_horiz, diagonals_accessible))
    if len(diagonals_accessible) > 0:
      slist.extend(diagonals_accessible)
    
    #logging.debug("[FORMAT: (y,x)] final successors for {0} are: {1}".format(c, slist))
    return slist
  # end of successors()


  ### END OF PATHFINDING METHODS ####################################

### END OF class World

if __name__ == '__main__':
  # if no random seed was given, make one up:
  crazySeed = random.randint(0, 65535)
  random.seed(crazySeed)
  
  #gridDisplaySize = (20, 10)
  gridDisplaySize = (40, 20)
  #gridDisplaySize = (100, 35)
  
  '''
  print("random number tests...")
  for size in ['small', 'medium', 'large']:
    for time in range(10):
      print("a {0} random number is: {1}".format(size, get_random_value([size])))
  for time in range(5):
    print("a random number in small-med: {0}".format(get_random_value(['small', 'medium'])))
  for time in range(5):
    print("a random number in med-large: {0}".format(get_random_value(['medium', 'large'])))
  for time in range(10):
    print("a random number in small-large: {0}".format(get_random_value(['small', 'large'])))
  exit()
  '''
  
  # Create the world, passing through the display size
  themap = World(gridDisplaySize)

  # show the final product
  print("USING RANDOM SEED: {0}",format(crazySeed))
  print("final world map is:")
  print(themap.to_s())



#EOF