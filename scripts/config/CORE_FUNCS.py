import contextlib
with contextlib.redirect_stdout(None):
    import pygame; pygame.init()
    from pygame.locals import *
import math


vec = pygame.math.Vector2

#rotations a point about an origin point using an angle in degrees
def rotate(origin, point, angle):
    ox, oy = origin
    px, py = point
    angle = math.radians(-angle)

    qx = ox + math.cos(angle) * (px - ox) - math.sin(angle) * (py - oy)
    qy = oy + math.sin(angle) * (px - ox) + math.cos(angle) * (py - oy)
    return qx, qy