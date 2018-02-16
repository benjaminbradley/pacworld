# Pygame spiral drawing function
# Copyright David Barker 2010
# linked from http://www.pygame.org/project-DrawSpiral()+function-1649-.html
# downloaded on 2013-07-31

import pygame, sys, math


def DrawSpiral(display, pos, radius, rotation = math.pi, numSpokes = 1, clockwise = True, startAngle = 0.0, color = (243, 243, 21), lineWidth = 1):
    """DrawSpiral(display, pos, radius, rotation = math.pi, numSpokes = 1, clockwise = True, startAngle = 0): return None
    Draws a spiral at the given position.
    Arguments:
        -display: the pygame.Surface object to draw to
        -pos: a tuple for the position of the centre of the spiral
        -radius: the radius of the spiral
        -rotation: the angle through which a single spoke will have turned by the time it reaches its end
        -numSpokes: the number of spokes to draw
        -clockwise: a boolean variable specifying which direction the spiral should turn in
        -startAngle: the starting angle of the first spoke
        -lineWidth: width of spiral lines
    """
    resolution = radius / 2.0
    radiusIncrement = radius / resolution
    rotationIncrement = rotation / resolution
    spokeRotationIncrement = (math.pi * 2.0) / float(numSpokes)
    spokeRotation = startAngle

    if clockwise:
        direction = -1
    else:
        direction = 1

    for i in range(0, numSpokes):
        spoke = []
        spoke.append(pos)

        curAngle = spokeRotation
        curRadius = 0.0

        while curRadius <= radius:
            newx = curRadius * math.sin(curAngle)
            newy = curRadius * math.cos(curAngle)
            spoke.append((pos[0] + newx, pos[1] + (direction * newy)))

            curRadius += radiusIncrement
            curAngle += rotationIncrement

        #FIXME: use lines instead of aalines until issue 395 is resolved: https://github.com/pygame/pygame/issues/395
        pygame.draw.lines(display, color, False, spoke, lineWidth)
        
        spokeRotation += spokeRotationIncrement


if __name__ == '__main__':  # Begin demo code
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Spirals!")

    clock = pygame.time.Clock()

    minRad = curRad = 20.0
    maxRad = curRad * 3
    curRot = math.pi
    startAngle = 0.0
    radStep = 2.0

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

        screen.fill((0, 0, 0))
        DrawSpiral(screen, pos = pygame.mouse.get_pos(), radius = curRad, rotation = curRot, numSpokes = 5, clockwise = True, startAngle = startAngle)

        curRad += radStep
        if curRad < minRad or curRad > maxRad: radStep = -radStep
        curRot += 0.1
        startAngle -= 0.05
        
        clock.tick(30)
        pygame.display.update()
