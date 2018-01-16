# Pygame mandala drawing function

import pygame, math, sys

# This function calls itself to add sub-trees
def DrawMandala(display, pos, color, outer_radius, angle, leaves, inner_radius_ratio, inner_radius_ratio2):
  """DrawMandala(display, pos, color, radius, angle, leaves): return None
  Draws a fractal tree at the given position.
  Arguments:
      -display: the pygame.Surface object to draw to
      -pos: an (x,y) tuple for the position of the center of the mandala
      -color: (R,G,B) tuple for the color of the mandala
      -radius: radius of the mandala
      -angle: angle (in degrees) off of base
      -leaves: number of leaves to draw (int)
  """
  cx, cy = pos
  width = 1
  #  draw the inner circle
  pygame.draw.circle(display, color, pos, int(outer_radius*inner_radius_ratio), width)
  pygame.draw.circle(display, color, pos, int(outer_radius*inner_radius_ratio2), width)
  # draw the leaves
  for l in range(0, leaves):
    # calculate leaf tip point on edge
    x2 = cx + int(math.cos(math.radians(angle + 360 * l/leaves)) * outer_radius)
    y2 = cy + int(math.sin(math.radians(angle + 360 * l/leaves)) * outer_radius)
    # calculate close point near center
    x1 = cx + int(math.cos(math.radians(angle + 360 * (l+1)/leaves)) * outer_radius*inner_radius_ratio)
    y1 = cy + int(math.sin(math.radians(angle + 360 * (l+1)/leaves)) * outer_radius*inner_radius_ratio)
    pygame.draw.line(display, color, (x1,y1), (x2,y2), width)
    
    # calculate leaf tip point on edge
    x3 = cx + int(math.cos(math.radians(angle + 360 * (l+1)/leaves)) * outer_radius)
    y3 = cy + int(math.sin(math.radians(angle + 360 * (l+1)/leaves)) * outer_radius)
    # calculate close point near center
    x4 = cx + int(math.cos(math.radians(angle + 360 * l/leaves)) * outer_radius*inner_radius_ratio)
    y4 = cy + int(math.sin(math.radians(angle + 360 * l/leaves)) * outer_radius*inner_radius_ratio)
    pygame.draw.line(display, color, (x3,y3), (x4,y4), width)


if __name__ == '__main__':  # Begin demo code
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Animated Mandala")

    clock = pygame.time.Clock()
    base_angle = 0
    leafchg = 0
    leafchg_max = 14
    leafchg_min = 12
    leaves = leafchg_min
    radius = 100
    inner_radius_ratio_chg = 0.03
    inner_radius_ratio_max = 0.6
    inner_radius_ratio_min = 0.2
    inner_radius_ratio = inner_radius_ratio_min
    inner_radius_ratio2 = inner_radius_ratio + 0.2
    
    color = (255, 128, 128)
    wait = 0

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or event.type == pygame.KEYDOWN:
                sys.exit()

        screen.fill((0, 0, 0))
        x1 = 400
        y1 = 300
        DrawMandala(screen, (x1, y1), color, radius, base_angle, leaves, inner_radius_ratio, inner_radius_ratio2)
        
        clock.tick(30)
        pygame.display.update()
        # spin it around
        base_angle -= 1
        if base_angle == 360: base_angle = 0

        if wait > 0:
          wait -= 1
        else:
          
          # TODO: change number of leaves?
          leaves += leafchg
          if(leafchg == 1 and leaves == leafchg_max):
            leafchg = -1
          elif(leafchg == -1 and leaves == leafchg_min):
            leafchg = 1

          inner_radius_ratio += inner_radius_ratio_chg
          #inner_radius_ratio2 = inner_radius_ratio + 0.2
          inner_radius_percent = (inner_radius_ratio - inner_radius_ratio_min) / (inner_radius_ratio_max - inner_radius_ratio_min)
          #print("{1}:inner_radius_percent|abs: {0}".format(abs(0.5 - inner_radius_percent), inner_radius_ratio_chg))
          inner_radius_ratio2 = inner_radius_ratio + (0.3 - 0.2 * inner_radius_percent)
          wait = 4*(abs(0.5 - inner_radius_percent) * 2)
          if(inner_radius_ratio_chg > 0 and inner_radius_ratio >= inner_radius_ratio_max):
            inner_radius_ratio_chg *= -1
            #wait = 8
          elif(inner_radius_ratio_chg < 0 and inner_radius_ratio <= inner_radius_ratio_min):
            inner_radius_ratio_chg *= -1
            #wait = 8



