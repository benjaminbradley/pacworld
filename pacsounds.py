import pygame.mixer  # sounds!
from pygame import *  # for pygame.time.get_ticks()
import logging

NUM_SOUND_CHANNELS = 16
SOUNDS = {
  '3robobeat' : 'sounds/132394__blackie666__robofart.wav',    # digital ba-dum-bump (sort of) - used for startup
  'get' : 'sounds/111689__blackie666__equip.wav',          # "get a swirl" (from an art piece)
  'ask' : 'sounds/111693__blackie666__load.wav',          # "ask" (another character)
  'give' : 'sounds/118687__blackie666__fx3.wav',          # "give" (to another character)
  'error' : 'sounds/135371__blackie666__thathurts.wav',    # "error" feedback (can't do something)
  '3roboditzfade' : 'sounds/135377__blackie666__nomnomnom.wav',  # burst sound
  'glitchsaw' : 'sounds/132391__blackie666__glitchsaw.wav',      # spiral effect sound
  'wassaw' : 'sounds/132393__blackie666__was-saw.wav',           # tree effect sound
  #  ("activate" a swirl) -> the sound for that effect
  'sizeChange' : 'sounds/135375__blackie666__resonance.wav',    # activate size
  'sideChange' : 'sounds/135376__blackie666__oowh.wav',          # activate sides
  'colorChange': 'sounds/102217__blackie666__rancidreverbtriangle.wav',    # activate color
}

pacsounds_instance = None
def getPacsound():
  global pacsounds_instance
  if not pacsounds_instance:
    pacsounds_instance = Pacsounds()
  return pacsounds_instance

# The class for the sound system
class Pacsounds(object):
  #_instance = None
  #def __new__(cls, *args, **kwargs):
  #  if not cls._instance:
  #    cls._instance = super(Pacsounds, cls).__new__(cls, *args, **kwargs)
  #  return cls._instance
  
  
  def __init__(self):
    # initialize the sound mixer
    #pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=4096)
    pygame.mixer.init(48000, -16, 1, 1024)
    pygame.mixer.set_num_channels(NUM_SOUND_CHANNELS)
    logging.debug("Initializing "+str(NUM_SOUND_CHANNELS)+" sound channels...")
    self.sound_channels = []
    for i in range(NUM_SOUND_CHANNELS):
      logging.debug("Initializing sound channel "+str(i+1))
      self.sound_channels.append(pygame.mixer.Channel(i))
    
    # load sounds
    self.sound_data = {}  # hash of shortname (above) to Sound data
    self.last_play = {}    # hash of shortname to last_play (in clock ticks)
    
    for sound_name in SOUNDS.keys():
      self.sound_data[sound_name] = pygame.mixer.Sound(SOUNDS[sound_name])
      logging.debug("loaded sound '{0}' from {1}: {2} sec".format(sound_name, SOUNDS[sound_name], self.sound_data[sound_name].get_length()))
    
    logging.debug("sound_channels.len = {0}".format(len(self.sound_channels)))
  
  def play(self, soundName, volume = 1.0):
    if soundName not in self.sound_data:
      logging.error("Sound key '{0}' is missing".format(soundName))
      return
    if self.sound_data[soundName] != None and volume > 0:
      # check for recent plays of the same sound
      cur_time = pygame.time.get_ticks()
      if soundName in self.last_play.keys():
        last_time = self.last_play[soundName]
        if(cur_time < last_time + 50):
          #logging.debug("sound %s has been played too recently, skipping", soundName)
          return  # minimum threshhold for repeated sounds
      
      channel = pygame.mixer.find_channel()
      if channel == None:
        logging.warning("no free channels (out of {0}), can't play '{1}'".format(NUM_SOUND_CHANNELS, soundName))
      else:
        #logging.debug("playing sound '{0}' at {1}% volume on channel {2}".format(soundName, volume*100, channel))
        channel.set_volume(volume)
        channel.play(self.sound_data[soundName])
        self.last_play[soundName] = cur_time

# tester
if __name__ == '__main__':
  logging.basicConfig(format='%(asctime)-15s:%(levelname)s:%(filename)s#%(funcName)s(): %(message)s', level=logging.DEBUG)
  import time
  sounds = Pacsounds()
  for key in SOUNDS:
    print('playing '+key)
    sounds.play(key)
    time.sleep(sounds.sound_data[key].get_length())
