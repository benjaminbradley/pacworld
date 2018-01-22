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

def centerBetween(point1, point2):
  """returns a 2-tuple(x,y) for the point between 2 other points"""
  x1,y1 = point1
  x2,y2 = point2
  cx = int((x1 + x2) / 2)
  cy = int((y1 + y2) / 2)
  return (cx,cy)
