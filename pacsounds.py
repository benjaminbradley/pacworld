import pygame.mixer	# sounds!

NUM_SOUND_CHANNELS = 1
SOUNDS = {
	'3robobeat' : 'sounds/132394__blackie666__robofart.wav',
	'3roboditzfade' : 'sounds/135377__blackie666__nomnomnom.wav'
}

# The class for the sound system
class Pacsounds():
	
	def __init__(self):
		# initialize the sound mixer
		#pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=4096)
		pygame.mixer.init(48000, -16, 1, 1024)
		pygame.mixer.set_num_channels(NUM_SOUND_CHANNELS)
		print("DEBUG: Initializing "+str(NUM_SOUND_CHANNELS)+" sound channels...")
		self.sound_channels = []
		for i in range(NUM_SOUND_CHANNELS):
			print("DEBUG: Initializing sound channel "+str(i+1))
			self.sound_channels.append(pygame.mixer.Channel(i))
		
		# load sounds
		self.sound_data = {}	# hash of shortname (above) to Sound data
		
		for sound_name in SOUNDS.keys():
			self.sound_data[sound_name] = pygame.mixer.Sound(SOUNDS[sound_name])
			print "DEBUG: loaded sound '{0}' from {1}: {2} sec".format(sound_name, SOUNDS[sound_name], self.sound_data[sound_name].get_length())
		
		print "DEBUG: sound_channels.len = {0}".format(len(self.sound_channels))
	
	def play(self, soundName):
		if self.sound_data[soundName] != None:
			self.sound_channels[0].play(self.sound_data[soundName])
