import logging
import math
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


def draw_polygon(surface, centerpoint, points, color, width, rotation_degrees = 0):
  # initialize surface with transparent background
  if(color == (0,0,0)): alpha=(1,1,1)
  else: alpha=(0,0,0)
  maxx = max([c[0] for c in points])
  maxy = max([c[1] for c in points])
  tempimg = pygame.Surface((maxx+width, maxy+width))
  tempimg.set_colorkey(alpha)
  tempimg.fill(alpha)
  # draw shape on new surface
  pygame.draw.polygon(tempimg, color, points, width)
  # rotate, if needed
  if(rotation_degrees != 0):
    tempimg = pygame.transform.rotate(tempimg, rotation_degrees)
  # blit shape onto surface at centerpoint
  upleftx = centerpoint[0]-tempimg.get_width()/2
  uplefty = centerpoint[1]-tempimg.get_height()/2
  surface.blit(tempimg, (upleftx, uplefty))


def draw_triangle(surface, centerpoint, size, color, width, rotation_degrees = 0):
  points = []
  points.append((0, 0)) # top left
  points.append((size,0)) # top right
  points.append((round(size/2), round(math.sqrt(size*size*.75)))) # bottom middle
  draw_polygon(surface, centerpoint, points, color, width, rotation_degrees)


def draw_square(surface, centerpoint, size, color, width, rotation_degrees = 0):
  points = []
  points.append((0, 0)) # top left
  points.append((size,0)) # top right
  points.append((size,size)) # bottom right
  points.append((0,size)) # bottom left
  draw_polygon(surface, centerpoint, points, color, width, rotation_degrees)


def draw_text(surface, text, topleft):
  font = pygame.font.Font(None, 20)
  textBitmap = font.render(text, True, (255,0,0))
  surface.blit(textBitmap, topleft)


if __name__ == '__main__':  # Begin test code
  logging.basicConfig(format='%(asctime)-15s:%(levelname)s:%(filename)s#%(funcName)s(): %(message)s', level=logging.DEBUG)
  import pygame
  screen_width = 800
  screen_height = 600
  screen = pygame.display.set_mode((screen_width, screen_height))
  pygame.display.set_caption("Test Pacglobal")
  
  rotation = 0
  going = True
  while going:
    screen.fill((0,0,0))

    for i in range(1, 4):
      draw_triangle(screen, (i*100, 100), 20*i, (i*50, 100, 100), 0, rotation)
      draw_square(screen, (i*100, 200), 20*i, (100, i*50, 100), 0, rotation)
      pygame.display.update()
      
    for event in pygame.event.get():
      if event.type == pygame.QUIT or event.type == pygame.KEYDOWN:
        going = False
    pygame.time.Clock().tick(30)
    rotation += 10
    if(rotation == 360): rotation = 0
