#!/usr/bin/env python

import pygame # Provides what we need to make a game
import sys # Gives us the sys.exit function to close our program
import getopt
import gc
import os
import random
import resource
import logging
import time

from pygame.locals import *
import pygame

import pacglobal
#import colors
from shape import Shape
from shape import *
from map import Map
import world
from world import World
import ArtRenderer
import pacmenu
from pacjoy import Pacjoy
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
INPUT_GAMEPAD = 'USB Gamepad'
INPUT_JOYSTICK = 'USB Joystick'
GAMEPAD_BUTTON_MAP = {
  INPUT_GAMEPAD: {  # 8-button, SNES-like
    'top': 0,
    'left': 3,
    'bottom': 2,
    'right': 1,
    'Lshoulder': 4,
    'Rshoulder': 5,
    'Lcenter': 8,
    'Rcenter': 9,
    'joy_axis_y': 4,
    'joy_axis_x': 3,
  },
  INPUT_JOYSTICK: {  # 10-button, Playstation-like
    'top': 3,
    'left': 2,
    'bottom': 0,
    'right': 1,
    'Lshoulder': 4,
    'Rshoulder': 5,
    'Lshoulder2': 6,
    'Rshoulder2': 7,
    'Lcenter': 8,
    'Rcenter': 9,
    'joy_axis_y': 3,
    'joy_axis_x': 2,
    'analog_axis_y': 0,
    'analog_axis_x': 1,
  }
}
GAMEPAD_FUNCTION_MAP = {
  INPUT_GAMEPAD: {  # 8-button, SNES-like
    'move_y':       GAMEPAD_BUTTON_MAP[INPUT_GAMEPAD]['joy_axis_y'],
    'move_x':       GAMEPAD_BUTTON_MAP[INPUT_GAMEPAD]['joy_axis_x'],
    'ask':          [],
    'give':         [GAMEPAD_BUTTON_MAP[INPUT_GAMEPAD]['top']],
    'swirl_right':  [],
    'swirl_left':   [GAMEPAD_BUTTON_MAP[INPUT_GAMEPAD]['left']],
    'doswirl_up':   [GAMEPAD_BUTTON_MAP[INPUT_GAMEPAD]['right']],
    'doswirl_dn':   [GAMEPAD_BUTTON_MAP[INPUT_GAMEPAD]['bottom']],
    'reset':        [GAMEPAD_BUTTON_MAP[INPUT_GAMEPAD]['Lcenter']],
    'quit':         [],
  },
  INPUT_JOYSTICK: {  # 10-button, Playstation-like
    'move_y':       GAMEPAD_BUTTON_MAP[INPUT_JOYSTICK]['joy_axis_y'],
    'move_x':       GAMEPAD_BUTTON_MAP[INPUT_JOYSTICK]['joy_axis_x'],
    'ask':          [GAMEPAD_BUTTON_MAP[INPUT_JOYSTICK]['bottom']],
    'give':         [GAMEPAD_BUTTON_MAP[INPUT_JOYSTICK]['top']],
    'swirl_right':  [GAMEPAD_BUTTON_MAP[INPUT_JOYSTICK]['right']],
    'swirl_left':   [GAMEPAD_BUTTON_MAP[INPUT_JOYSTICK]['left']],
    'doswirl_up':   [GAMEPAD_BUTTON_MAP[INPUT_JOYSTICK]['Rshoulder'],GAMEPAD_BUTTON_MAP[INPUT_JOYSTICK]['Rshoulder2']],
    'doswirl_dn':   [GAMEPAD_BUTTON_MAP[INPUT_JOYSTICK]['Lshoulder'],GAMEPAD_BUTTON_MAP[INPUT_JOYSTICK]['Lshoulder2']],
    'reset':        [GAMEPAD_BUTTON_MAP[INPUT_JOYSTICK]['Lcenter']],
    'quit':         [GAMEPAD_BUTTON_MAP[INPUT_JOYSTICK]['Rcenter']],
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
      self.newRandomSeed()
    
    # Initialize pygame
    pygame.init()
    # reset allowed types on the events queue
    pygame.event.set_allowed(None)
    pygame.event.set_allowed(QUIT)
    
    self.sound = getPacsound()
    
    # Create a clock to manage time
    self.clock = pygame.time.Clock()
    self.frametime = [] # array of recent frametimes, to calculate a rolling average
    self.frametime_idx = 0
    self.min_frametime = 1000
    self.max_frametime = 0
    
    # Initialize keyboard
    self.cur_kb_map = KB_MAP[KB_DVORAK]
    self.input_mode = [INPUT_KEYBOARD]
    pygame.event.set_allowed([KEYDOWN,KEYUP])
    
    # Initialize the joysticks (if present)
    pygame.joystick.init()
    
    # Get count of joysticks
    joystick_count = pygame.joystick.get_count()
    if joystick_count == 0:
      logging.warning("no joysticks found, using only keyboard for input")
    else:
      joy_name = pygame.joystick.Joystick(0).get_name().strip()
      if(joy_name in GAMEPAD_BUTTON_MAP.keys()):
        logging.info("{} present, enabling joystick for input".format(joy_name))
        self.cur_button_map = GAMEPAD_BUTTON_MAP[joy_name]
        self.cur_pad_map = GAMEPAD_FUNCTION_MAP[joy_name]
        self.input_mode.append(INPUT_JOYSTICK)
        pygame.event.set_allowed([JOYBUTTONDOWN,JOYBUTTONUP,JOYAXISMOTION])
      else:
        logging.error("Joystick present, but not currently mapped, name='{}'".format(joy_name))
    
    
    if(INPUT_JOYSTICK in self.input_mode):
      self.pacjoy = Pacjoy(pygame.joystick.Joystick(0))
      self.button_status = []
      self.num_buttons = self.pacjoy.get_numbuttons()
      for i in range( self.num_buttons ):
        self.button_status.append(self.pacjoy.get_button(i))
      joy_axis_x = self.cur_pad_map['move_x']
      joy_axis_y = self.cur_pad_map['move_y']
      # check for variations on RPi
      if(joy_name == INPUT_GAMEPAD):
        if(pygame.joystick.Joystick(0).get_numaxes() == 2):
          joy_axis_x = 0
          joy_axis_y = 1
          logging.debug("Adjusting x/y axes for RPi: x={}, y={}".format(joy_axis_x, joy_axis_y))
      self.pacjoy.setXaxis(joy_axis_x)
      self.pacjoy.setYaxis(joy_axis_y)
    else:
      self.pacjoy = None
    
    # Set the window title
    pygame.display.set_caption("Flat Flip Friends")
    
    # capture current screen res for fullscreen mode
    self.fullscreen_resolution = (pygame.display.Info().current_w, pygame.display.Info().current_h)
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
    
    ArtRenderer.renderArt(self.character_size)
    
    random.seed(self.crazySeed)
    
    self.mapSize = [SCALE_FACTOR*x for x in self.display.getDisplaySize()]
    
    gridSize = int(self.character_size * 1.5)
    self.gridDisplaySize = (int(self.mapSize[0] / gridSize), int(self.mapSize[1] / gridSize))  # assumes square grid cells
    logging.debug("gridDisplaySize is {0}".format(self.gridDisplaySize))

    self.last_worldgen = int(time.time())
    # generate world, map, and all the things in it
    self.generateWorld(self.start_autonomous)

    # play a "startup" sound
    self.sound.play('3robobeat')


  def newRandomSeed(self):
    self.crazySeed = random.randint(0, MAX_RANDOM_SEED)
    logging.info("USING RANDOM SEED: {0}".format(self.crazySeed))
    print("USING RANDOM SEED: {0}".format(self.crazySeed))


  def generateWorld(self, start_autonomous):
    now = int(time.time())
    worldage = now - self.last_worldgen
    logging.debug("World regenerated after {} seconds".format(worldage))
    self.last_worldgen = now
    # run garbage collection
    gc.collect()
    # log memory usage
    usage = resource.getrusage(resource.RUSAGE_SELF)
    logging.debug("Process memory usage is: {}".format(usage.ru_maxrss))
    
    self.surface.fill((0,0,0))
    # show notice
    font = pygame.font.Font(None, 52)
    textBitmap = font.render("Flat Flip Friends", True, colors.WHITE)
    textWidth = textBitmap.get_rect().width
    textHeight = textBitmap.get_rect().height
    self.surface.blit(textBitmap, [self.display.getDisplaySize()[0]/2 - textWidth/2, self.display.getDisplaySize()[1]/2 - textHeight*2])
    font = pygame.font.Font(None, 30)
    textBitmap = font.render("Generating world...", True, colors.WHITE)
    textWidth = textBitmap.get_rect().width
    self.surface.blit(textBitmap, [self.display.getDisplaySize()[0]/2 - textWidth/2, self.display.getDisplaySize()[1]/2])
    pygame.display.update()

    # Create the world, passing through the grid size
    theworld = World(self.gridDisplaySize)
    logging.debug("rendered world:\n{0}".format(theworld.to_s()))

    # Create the world map, passing through the display size and world map
    self.map = Map(self.mapSize, self.display, self.character_size, theworld)
    art = theworld.addArt(self.map)
    shapes = self.map.addShapes()
    self.sprites = pygame.sprite.Group(shapes, art)

    # Create the player object and add it's shape to a sprite group
    self.player = Player()
    self.player.selectShape(self.map.shapes[0])  # just grab the first shape for the player
    self.player.shape.autonomous = self.start_autonomous

    self.map.player = self.player

  def get_framespeed_info(self, clock):
    rawtime = clock.get_rawtime()
    if(len(self.frametime) < 30):
      self.frametime.append(rawtime)
    else:
      self.frametime[self.frametime_idx] = rawtime
    self.frametime_idx = (self.frametime_idx + 1) % 30
    average_frametime = int(sum(self.frametime) / len(self.frametime))
    if(average_frametime < self.min_frametime): self.min_frametime = average_frametime
    if(50 < pacglobal.get_frames() and average_frametime > self.max_frametime): self.max_frametime = average_frametime
    return str(self.min_frametime) + ' < ' + str(average_frametime) + ' < ' + str(self.max_frametime)


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
      
      # check swirl saturation
      (total_swirls, num_shapes, swirl_saturation_pct) = self.map.getSwirlSaturationPercent()
      if swirl_saturation_pct >= pacdefs.MAX_SWIRL_SATURATION_PERCENT or pacdefs.MAX_WORLD_REGEN_TIME < time.time() - self.last_worldgen:
        self.newRandomSeed()
        self.generateWorld(self.player.shape.autonomous)
      elif pacdefs.DEBUG_NUMSWIRLS:
        # debug number of swirls
        font = pygame.font.Font(None, 30)
        textBitmap = font.render("{} swirls / {} shapes / {} %".format(total_swirls, num_shapes, swirl_saturation_pct), True, colors.WHITE)
        self.surface.blit(textBitmap, (10,10))
      
      # Update the full display surface to the screen
      pygame.display.update()
      
      # Limit the game to 30 frames per second
      self.clock.tick(30)

      # display debug if enabled
      if(pacdefs.DEBUG_FRAMESPEED):
        pygame.display.set_caption("fps: " + str(int(self.clock.get_fps())) + " | framespeed: " + self.get_framespeed_info(self.clock))

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


  def doMenu(self):
    menu_choice = pacmenu.getMenu().dialog(self.surface, self.pacjoy)
    if menu_choice == pacmenu.MENU_POWEROFF:
      confirm = pacmenu.getConfirmMenu().dialog(self.surface, self.pacjoy)
      if confirm == pacmenu.MENU_CONFIRM:
        os.system("/sbin/poweroff")


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
        joy_value_y = self.pacjoy.get_joy_axis_y()
        joy_value_x = self.pacjoy.get_joy_axis_x()
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
            if(self.pacjoy.get_button(i) and not self.button_status[i]):
              self.button_status[i] = True
              logging.debug("joystick Button "+str(i+1)+" pressed.")
              if(i in self.cur_pad_map['ask']):
                self.player.shape.tryAsk()
              elif(i in self.cur_pad_map['swirl_right']):
                self.player.shape.trySwirlRight()
              elif(i in self.cur_pad_map['swirl_left']):
                self.player.shape.trySwirlLeft()
              elif(i in self.cur_pad_map['give']):
                self.player.shape.tryGive()
              elif(i in self.cur_pad_map['doswirl_up']):
                self.player.shape.activateSwirl(True)
              elif(i in self.cur_pad_map['doswirl_dn']):
                self.player.shape.activateSwirl(False)
              elif(i in self.cur_pad_map['reset']):
                self.player.shape.reset()
              elif(i in self.cur_pad_map['quit']):
                logging.info("That was RANDOM SEED {0}. Hope you had fun.".format(self.crazySeed))
                logging.debug("Quitting program.")
                pygame.quit()
                sys.exit()
          # multi-button combinations
          if(self.pacjoy.get_button(self.cur_button_map['Lshoulder']) and self.pacjoy.get_button(self.cur_button_map['Rshoulder'])
            and self.pacjoy.get_button(self.cur_button_map['Lcenter']) and self.pacjoy.get_button(self.cur_button_map['Rcenter'])):
            self.doMenu()
        
        
        if event.type == pygame.JOYBUTTONUP:
          #logging.debug("Joystick button released.")
          for i in range( self.num_buttons ):
            if(not self.pacjoy.get_button(i) and self.button_status[i]):
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
          elif event.key == K_b:  # generate new world
            self.newRandomSeed()
            self.generateWorld(self.player.shape.autonomous)
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
          elif event.key == K_BACKQUOTE:
            self.doMenu()
        
        if event.type == KEYUP:
          if event.key == K_DOWN:
            self.player.shape.stopMove(DIR_DOWN)
          elif event.key == K_UP:
            self.player.shape.stopMove(DIR_UP)
          elif event.key == K_RIGHT:
            self.player.shape.stopMove(DIR_RIGHT)
          elif event.key == K_LEFT:
            self.player.shape.stopMove(DIR_LEFT)
      # end of (INPUT_KEYBOARD)
    # end for (events)
    
    # movement should be smooth, so not tied to event triggers
    if(INPUT_JOYSTICK in self.input_mode and \
      ('analog_axis_y' in self.cur_pad_map.keys() and 'analog_axis_x' in self.cur_pad_map.keys())):
      fbAxis = round(self.pacjoy.get_axis(self.cur_pad_map['analog_axis_y']), 3)
      if(abs(fbAxis) > JOYSTICK_NOISE_LEVEL):
        self.player.shape.move(0, fbAxis * self.player.shape.linearSpeed)
      lrAxis = round(self.pacjoy.get_axis(self.cur_pad_map['analog_axis_x']), 3)
      if(abs(lrAxis) > JOYSTICK_NOISE_LEVEL):
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
