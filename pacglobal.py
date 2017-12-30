import pygame

frames = 0

def get_frames():
	global frames
	return frames

def nextframe():
	global frames
	frames += 1


class UserAbort(Exception):
	pass

def checkAbort():
	event = pygame.event.poll()
	if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE: raise UserAbort()
