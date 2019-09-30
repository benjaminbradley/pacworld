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

def adjustColor(colorTuple, percent):
  newColor = list(colorTuple)
  for n in range(0,3):
    newColor[n] = round(colorTuple[n] * (1+percent))
    if(newColor[n] < 0): newColor[n] = 0
    if(newColor[n] > 255): newColor[n] = 255
  return tuple(newColor)

def blendColor(origColor, destColor, percent = 0.5):
  """blends origColor towards destColor by percent. 0%=origColor, 100%=destColor"""
  newColor = list(origColor)
  for n in range(0,3):
    totaldiff = max(destColor[n], origColor[n]) - min(destColor[n], origColor[n])
    applieddiff = round(totaldiff * percent)
    if(origColor[n] < destColor[n]): newColor[n] = origColor[n] + applieddiff
    else: newColor[n] = origColor[n] - applieddiff
  return tuple(newColor)
