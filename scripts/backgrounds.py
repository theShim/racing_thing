import contextlib
with contextlib.redirect_stdout(None):
    import pygame; pygame.init()
    from pygame.locals import *
    
import math
import random
import os

from scripts.particles import Trail, TyreSpark

from scripts.config.SETTINGS import SIZE
from scripts.config.CORE_FUNCS import vec

    ##############################################################################################

#background sprite, nothing special other than the camera offset
class RaceTrack(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.z = 0

        self.image = pygame.image.load("assets/race_track.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, vec(self.image.get_size()) * 3)

    def update(self, screen, offset):
        screen.blit(self.image, -offset)