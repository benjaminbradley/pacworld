# Pygame fractal tree drawing function

import pygame, math, sys

# This function calls itself to add sub-trees
def DrawFractalTree(display, pos, base_angle, max_depth, branch_angle, branch_ratio, color):
  """DrawFractalTree(display, pos, base_angle, max_depth, branch_angle, branch_ratio, color): return None
  Draws a fractal tree at the given position.
  Arguments:
      -display: the pygame.Surface object to draw to
      -pos: an (x,y) tuple for the position of the base of the tree
      -base_angle: angle of the trunk in degrees
      -max_depth: max number of iterations left
      -branch_angle: angle off of center for each branch in degrees
      -branch_ratio: ratio of branch size to trunk size
      -color: (R,G,B) tuple for the color of the branches
  """
  x1, y1 = pos
  if max_depth > 0:
    # compute this branch's next endpoint
    x2 = x1 + int(math.cos(math.radians(base_angle)) * max_depth * branch_ratio)
    y2 = y1 + int(math.sin(math.radians(base_angle)) * max_depth * branch_ratio)
    width = 1
    # draw the trunk for this iteration of the tree
    pygame.draw.line(display, color, (x1,y1), (x2,y2), width)
    # recurse into the next level of branches
    #ASSUME: 2 branches - one left and one right
    DrawFractalTree(display, (x2, y2), base_angle - branch_angle, max_depth - 1, branch_angle, branch_ratio, color)
    DrawFractalTree(display, (x2, y2), base_angle + branch_angle, max_depth - 1, branch_angle, branch_ratio, color)


if __name__ == '__main__':  # Begin demo code
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Fractal Trees!")

    clock = pygame.time.Clock()
    branch_ratio = 10.0                   # branch length factor
    base_angle = -90
    steps = 8
    maxd_beg = 2
    maxd_end = 8
    maxd = maxd_beg
    maxd_chgdir = 1
    spread_beg = 12
    spread_end = 30
    spread = spread_beg
    spread_chgdir = 1
    
    color = (128, 255, 128)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

        screen.fill((0, 0, 0))
        x1 = 400
        y1 = 590
        DrawFractalTree(screen, (x1, y1), base_angle, maxd, spread, branch_ratio, color)
        
        clock.tick(10)
        pygame.display.update()
        maxdchg = max(1,int((maxd_end - maxd_beg) / steps))
        maxd += maxd_chgdir * maxdchg
        if(maxd > maxd_end):
          maxd_chgdir = 0
          spreadchg = max(1,int((spread_end - spread_beg) / steps))
          spread += spread_chgdir * spreadchg
          if(spread > spread_end):
            spread_chgdir = -1
          elif(spread < spread_beg):
            maxd_chgdir = -1
            spread_chgdir = 0
        elif(maxd < maxd_beg):
          maxd_chgdir = 1
          spread_chgdir = 1
