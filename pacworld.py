#!/usr/bin/env python

import pygame # Provides what we need to make a game
import sys # Gives us the sys.exit function to close our program
import getopt
import random
import logging

from pygame.locals import *
from pygame import *

import pacglobal
#import colors
from shape import Shape
from shape import *
from map import Map
import world
from world import World
from pacsounds import Pacsounds,getPacsound
from pacdisplay import Pacdisplay
from player import Player

INPUT_KEYBOARD = 'kb'
INPUT_JOYSTICK = 'joy'
JOYSTICK_NOISE_LEVEL = 0.1

MAX_RANDOM_SEED = 65535

KB_QWERTY = 1
KB_DVORAK = 2
KB_MAP = {
  KB_QWERTY: {
    'top' : K_w,
    'left' : K_a,
    'bottom': K_s,
    'right': K_d,
    'Lshoulder': K_q,
    'Rshoulder': K_e,
  },
  KB_DVORAK: {
    'top' : K_COMMA,
    'left' : K_a,
    'bottom': K_o,
    'right': K_e,
    'Lshoulder': K_QUOTE,
    'Rshoulder': K_PERIOD,
  }
}

# Our main game class
class Pacworld:
  def usage(self):
    print('USAGE:')
    print('{0} [options]'.format(sys.argv[0]))
    print('options are:')
    print('  -h --help    print this help')
    print('  -f        start fullscreen')
    print('  -s --seed=[number]    specify a seed for the random number generator')
    print('  -c --scale=[number]    create a map which is SCALE^2 times larger than the initial display resolution')
    print('  -a        begin in autonomous (self-playing) mode')
  
  def __init__(self, argv):
    logging.basicConfig(format='%(asctime)-15s:%(levelname)s:%(filename)s#%(funcName)s(): %(message)s', level=logging.DEBUG, filename='log/pacworld.log')
    logging.debug("Initializing Pacworld()...")

    # set defaults for CLI arguments
    SCALE_FACTOR = 3  # total map is SCALE_FACTOR^2 times the screen size
    self.crazySeed = None
    self.is_fullscreen = False
    self.start_autonomous = False
    
    try:
      opts, args = getopt.getopt(argv, "hs:c:fa", ["help", "seed=", "scale=", "fullscreen", "autonomous"])
    except getopt.GetoptError:
      self.usage()
      sys.exit(2)
    for opt, arg in opts:
      if opt in ("-h", "--help"):
        self.usage()
        sys.exit()
      elif opt in ("-s", "--seed"):
        self.crazySeed = int(arg)
        logging.info("USING CHOSEN SEED: {0}".format(self.crazySeed))
      elif opt in ("-c", "--scale"):
        SCALE_FACTOR = int(arg)
      elif opt in ("-f", "--fullscreen"):
        self.is_fullscreen = True
      elif opt in ("-a", "--autonomous"):
        self.start_autonomous = True
    
    # if no random seed was given, make one up:
    if self.crazySeed is None:
      self.crazySeed = random.randint(0, MAX_RANDOM_SEED)
      logging.info("USING RANDOM SEED: {0}".format(self.crazySeed))
      print("USING RANDOM SEED: {0}".format(self.crazySeed))
    
    # Initialize pygame
    pygame.init()
    
    self.sound = getPacsound()
    
    # Create a clock to manage time
    self.clock = pygame.time.Clock()
    
    # Initialize keyboard
    self.cur_kb_map = KB_MAP[KB_DVORAK]
    
    # Initialize the joysticks (if present)
    pygame.joystick.init()
    
    # Get count of joysticks
    joystick_count = pygame.joystick.get_count()
    self.input_mode = [INPUT_KEYBOARD]
    if joystick_count == 0:
      logging.warning("no joysticks found, using only keyboard for input")
    else:
      logging.info("joystick present, enabling joystick for input")
      self.input_mode.append(INPUT_JOYSTICK)
    
    if(INPUT_JOYSTICK in self.input_mode):
      self.joystick = pygame.joystick.Joystick(0)
      self.joystick.init()
      self.button_status = []
      self.num_buttons = self.joystick.get_numbuttons()
      for i in range( self.num_buttons ):
        self.button_status.append(self.joystick.get_button(i))
      self.num_axes = self.joystick.get_numaxes()
      if(self.num_axes == 4):
        self.joy_axis_x = 2
        self.joy_axis_y = 3
    
    # Set the window title
    pygame.display.set_caption("WORKING NAME: Pacworld")
    
    # capture current screen res for fullscreen mode
    self.fullscreen_resolution = (display.Info().current_w, display.Info().current_h)
    # set window size
    self.windowed_resolution = (800,600)
    # initialize display system
    if self.is_fullscreen:
      flags = pygame.FULLSCREEN
      self.display = Pacdisplay(self.fullscreen_resolution)
      pygame.mouse.set_visible(False)
    else:
      flags = 0
      self.display = Pacdisplay(self.windowed_resolution)
    self.character_size = 80 #int(self.display.getDisplaySize()[0] / 10)  #TODO: make this a configurable value (CLI arg?)
    logging.debug("Character size set to {0}".format(self.character_size))
    # Create the window
    self.surface = pygame.display.set_mode(self.display.getDisplaySize(), flags)
    font = pygame.font.Font(None, 30)
    textBitmap = font.render("Generating world...", True, colors.WHITE)
    #textRect = textBitmap.get_rect().width
    #print "DEBUG: textRect is: {0}".format(textRect)
    textWidth = textBitmap.get_rect().width
    self.surface.blit(textBitmap, [self.display.getDisplaySize()[0]/2 - textWidth/2, self.display.getDisplaySize()[1]/2])
    pygame.display.update()
    
    
    random.seed(self.crazySeed)
    
    mapSize = [SCALE_FACTOR*x for x in self.display.getDisplaySize()]
    
    gridSize = int(self.character_size * 1.5)
    gridDisplaySize = (int(mapSize[0] / gridSize), int(mapSize[1] / gridSize))  # assumes square grid cells
    logging.debug("gridDisplaySize is {0}".format(gridDisplaySize))

    # Create the world, passing through the grid size
    theworld = World(gridDisplaySize)
  
    # Create the world map, passing through the display size and world map
    self.map = Map(mapSize, self.display, self.character_size, theworld)
    art = theworld.addArt(self.map)
    shapes = self.map.addShapes()
    self.sprites = sprite.Group(shapes, art)

    # Create the player object and add it's shape to a sprite group
    self.player = Player()
    self.player.selectShape(self.map.shapes[0])  # just grab the first shape for the player
    self.player.shape.autonomous = self.start_autonomous

    self.map.player = self.player
    #self.player.shape.mapTopLeft = [int(5.5*self.map.grid_cellwidth-self.shape.side_length/2), int(5.5*self.map.grid_cellheight-self.shape.side_length/2)]
    
    logging.info("USING RANDOM SEED: {0}".format(self.crazySeed))

    # play a "startup" sound
    self.sound.play('3robobeat')
  

  def run(self):
    # Runs the game loop
    
    while True:
      # The code here runs when every frame is drawn
      curtime = pygame.time.get_ticks()
      #print "looping"
      
      # Handle Events
      self.handleEvents(curtime)
      
      # update the map
      self.map.update(curtime)
      
      # Update the sprites
      self.sprites.update(curtime)

      # Draw the background
      self.map.draw(self.surface)
      
      # draw the sprites
      #print "DEBUG: drawing shape via sprite group. shape rect is: {0}".format(self.shape.rect)
      # draw the shape by itself onto the display. it's always there.
      self.player.shape.draw(self.surface)
      windowRect = self.map.player.shape.getWindowRect()
      # NOTE: we only want to show the art that is currently onscreen, and it needs to be shifted to its correct position
      for artpiece in self.player.shape.art_onscreen():
        # if artpiece is on the screen, we will draw it
        #logging.debug("drawing art at {0}".format(artpiece.rect))
        artpiece.draw(self.surface, windowRect)
      
      # draw any other shapes that are currently onscreen
      for shape in self.map.shapes:
        # if artpiece is on the screen, we will draw it
        if not shape.onScreen(windowRect): continue
        #logging.debug("drawing shape {0} at {1}".format(shape.id, shape.mapTopLeft))
        shape.draw(self.surface)
      
      
      # Update the full display surface to the screen
      pygame.display.update()
      
      # display debug if enabled
      pygame.display.set_caption("fps: " + str(int(self.clock.get_fps())))

      # Limit the game to 30 frames per second
      self.clock.tick(30)
      
      # advance frame counter
      pacglobal.nextframe()


  def toggleFullscreen(self):
    screen = pygame.display.get_surface()
    bits = screen.get_bitsize()
    if self.is_fullscreen:
      self.is_fullscreen = False
      flags = screen.get_flags() & ~pygame.FULLSCREEN
      self.display.setDisplaySize(self.windowed_resolution)
    else:
      self.is_fullscreen = True
      flags = screen.get_flags() | pygame.FULLSCREEN
      self.display.setDisplaySize(self.fullscreen_resolution)
    pygame.display.quit()
    pygame.display.init()
    self.surface = pygame.display.set_mode(self.display.getDisplaySize(),flags,bits)
    pygame.mouse.set_visible(not self.is_fullscreen)
    self.player.shape.updatePosition()


  def handleEvents(self, ticks):
    
    # Handle events, starting with the quit event
    for event in pygame.event.get():
      if event.type == QUIT:
        pygame.quit()
        sys.exit()

      if(INPUT_KEYBOARD in self.input_mode and event.type == KEYDOWN and event.key == K_ESCAPE):
        pygame.quit()
        sys.exit()

      if self.player.shape.in_dance(): continue # ignore all player input while in dance

      if(INPUT_JOYSTICK in self.input_mode):
        # check for joystick movement
        joy_value_y = round(self.joystick.get_axis( self.joy_axis_y ))
        joy_value_x = round(self.joystick.get_axis( self.joy_axis_x ))
        logging.debug("joystick movement = {0},{1}".format(joy_value_x, joy_value_y))
        if(joy_value_y != 0 or joy_value_x != 0):
          self.player.notIdle(ticks)
        # -1 = left, 1 = right
        if(joy_value_y == 1):  # -1 = up, down = 1
          self.player.shape.startMove(DIR_DOWN)
        elif(joy_value_y == -1):
          self.player.shape.startMove(DIR_UP)
        else:  # joy_value_y == 0
          self.player.shape.stopMove(DIR_DOWN)
          self.player.shape.stopMove(DIR_UP)
        if(joy_value_x == 1):
          self.player.shape.startMove(DIR_RIGHT)
        elif(joy_value_x == -1):
          self.player.shape.startMove(DIR_LEFT)
        else:  # joy_value_x == 0
          self.player.shape.stopMove(DIR_RIGHT)
          self.player.shape.stopMove(DIR_LEFT)
        
        # Possible joystick actions: JOYAXISMOTION JOYBALLMOTION JOYBUTTONDOWN JOYBUTTONUP JOYHATMOTION
        if event.type == pygame.JOYBUTTONDOWN:
          #logging.debug("Joystick button pressed.")
          self.player.notIdle(ticks)
          for i in range( self.num_buttons ):
            if(self.joystick.get_button(i) and not self.button_status[i]):
              self.button_status[i] = True
              logging.debug("joystick Button "+str(i+1)+" pressed.")
              if(i == 0):  # "bottom" button
                self.player.shape.tryAsk()
              elif(i == 1):  # "right" button
                self.player.shape.trySwirlRight()
              elif(i == 2):  # "left" button
                self.player.shape.trySwirlLeft()
              elif(i == 3):  # "top" button
                self.player.shape.tryGive()
              elif(i in [4,5]):
                self.player.shape.activateSwirl(True)
              elif(i in [6,7]):
                self.player.shape.activateSwirl(False)
              elif(i == 8):
                self.player.shape.reset()
              elif(i == 9):  # button 10 triggers program exit
                logging.info("That was RANDOM SEED {0}. Hope you had fun.".format(self.crazySeed))
                logging.debug("Quitting program.")
                pygame.quit()
                sys.exit()
              
        if event.type == pygame.JOYBUTTONUP:
          #logging.debug("Joystick button released.")
          for i in range( self.num_buttons ):
            if(not self.joystick.get_button(i) and self.button_status[i]):
              self.button_status[i] = False
              #logging.debug("Button "+str(i+1)+" released.")
      # end of : input_mode == INPUT_JOYSTICK

      if(INPUT_KEYBOARD in self.input_mode):
        if event.type == KEYDOWN:
          self.player.notIdle(ticks)
          # Find which key was pressed

          if event.key == self.cur_kb_map['top']:  # "top" button
            self.player.shape.tryGive()
          elif event.key == self.cur_kb_map['left']:  # "left" button
            self.player.shape.trySwirlLeft()
          elif event.key == self.cur_kb_map['bottom']:  # "bottom" button
            self.player.shape.tryAsk()
          elif event.key == self.cur_kb_map['right']:  # "right" button
            self.player.shape.trySwirlRight()
          elif event.key == self.cur_kb_map['Lshoulder']:  # "left shoulder" button
            self.player.shape.activateSwirl(False)
          elif event.key == self.cur_kb_map['Rshoulder']:  # "right shoulder" button
            self.player.shape.activateSwirl(True)
          elif event.key == K_f:  # toggle fullscreen
            self.toggleFullscreen()
          elif event.key == K_DOWN:
            self.player.shape.startMove(DIR_DOWN)
          elif event.key == K_UP:
            self.player.shape.startMove(DIR_UP)
          elif event.key == K_RIGHT:
            self.player.shape.startMove(DIR_RIGHT)
          elif event.key == K_LEFT:
            self.player.shape.startMove(DIR_LEFT)
          elif event.key == K_t:  # NOTE: "teleport" effect - FOR DEBUG ONLY ??
            self.player.shape.reset()
          elif event.key == K_SPACE:
            # DEBUG - activate autonomosity
            nearby_shapes = self.map.nearShapes(self.player.shape.getCenter(), self.map.character_size * 1.5, self.player.shape)
            if len(nearby_shapes) > 0:
              #logging.debug("Shapes near to S#{0}: {1}".format(self.id, nearby_shapes))
              receiver = nearby_shapes[0]
              receiver.autonomous = not receiver.autonomous
              logging.debug("toggling autonomy for shape #{0}, now {1}".format(receiver.id, receiver.autonomous))
            else:
              logging.debug("no nearby shapes")
      
        if event.type == KEYUP:
          if event.key == K_DOWN:
            self.player.shape.stopMove(DIR_DOWN)
          elif event.key == K_UP:
            self.player.shape.stopMove(DIR_UP)
          elif event.key == K_RIGHT:
            self.player.shape.stopMove(DIR_RIGHT)
          elif event.key == K_LEFT:
            self.player.shape.stopMove(DIR_LEFT)
          #if event.key == K_s or event.key == K_w:
          #  self.player1Bat.stopMove()
          #elif event.key == K_DOWN or event.key == K_UP:
          #  self.player2Bat.stopMove()
      # end of (INPUT_KEYBOARD)
    # end for (events)
    
    # movement should be smooth, so not tied to event triggers
    if(INPUT_JOYSTICK in self.input_mode):
      fbAxis = round(self.joystick.get_axis(0), 3)
      if(abs(fbAxis) > JOYSTICK_NOISE_LEVEL):
        #print "DEBUG: fbAxis is: "+str(fbAxis)
        self.player.shape.move(0, fbAxis * self.player.shape.linearSpeed)
    
      lrAxis = round(self.joystick.get_axis(1), 3)
      if(abs(lrAxis) > JOYSTICK_NOISE_LEVEL):
        #print "DEBUG: lrAxis is: "+str(lrAxis)
        self.player.shape.move(lrAxis * self.player.shape.linearSpeed, 0)

    # after processing any pending user events, check for idle condition
    self.player.checkIdle(ticks)



if __name__ == '__main__':
  try:
    game = Pacworld(sys.argv[1:])
    game.run()
  except pacglobal.UserAbort:
    logging.debug("Aborted by user during startup.")
    print("Aborted by user during startup.")
