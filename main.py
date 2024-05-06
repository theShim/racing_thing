import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
os.environ['SDL_VIDEO_CENTERED'] = '1'

import contextlib
with contextlib.redirect_stdout(None):
    import pygame
    from pygame.locals import *
    
import sys
import time

from scripts.car import Car
from scripts.particles import TyreSpark
from scripts.backgrounds import RaceTrack

from scripts.config.SETTINGS import *
from scripts.config.CORE_FUNCS import * 

    ##############################################################################################

class Game:
    def __init__(self):
        #intiaising pygame stuff
        self.initialise()

        #initalising pygame window
        flags = pygame.RESIZABLE | pygame.SCALED
        self.screen = pygame.display.set_mode(SIZE, flags)
        self.clock = pygame.time.Clock()
        self.offset = vec()

        #caching sprites once at the beginning to avoid re-loading them over and over again
        TyreSpark.cache_sprites()

        #container or "group" of all the sprites being rendered on screen
        self.all_sprites = pygame.sprite.Group()

        self.player = Car(self.all_sprites, pos=(WIDTH//2, HEIGHT//2)) #the player car
        self.all_sprites.add(self.player)
        self.bg = RaceTrack()                                          #the background
        self.all_sprites.add(RaceTrack())

    def initialise(self):
        pygame.init()  #general pygame
        pygame.font.init() #font stuff
        pygame.display.set_caption(WINDOW_TITLE) #Window Title 

        pygame.mixer.pre_init(44100, 16, 2, 4096) #music stuff
        pygame.mixer.init()

        pygame.event.set_blocked(None) #setting allowed events to reduce lag
        pygame.event.set_allowed([pygame.QUIT, pygame.KEYDOWN, pygame.KEYUP, pygame.MOUSEWHEEL])

    # a psuedo-camera offset so that the player is always at the centre of the screen
    # the dividing by 12 helps give the effect of the camera "following" the player
    def calculate_offset(self):
        self.offset.x += (self.player.rect.centerx - WIDTH/2 - self.offset.x) / 12
        self.offset.y += (self.player.rect.centery - HEIGHT/2 - self.offset.y) / 12

    #the main event loop
    def run(self):
        last_time = time.perf_counter()
        running = True
        while running:
            #deltatime (i don't use it in this example but it's good to use for "framerate independence")
            self.dt = time.perf_counter() - last_time
            self.dt *= FPS
            last_time = time.perf_counter()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        running = False
                    
            self.screen.fill((30, 30, 30)) #filling the void background
            self.calculate_offset() #updating the camera offset every frame

            # rendering the sprites in order of back to front
            # each sprite has its own "z" value representing the order it should be blit in
            for spr in sorted(self.all_sprites.sprites(), key=lambda spr: spr.z):
                spr.update(self.screen, self.offset)

            if DEBUG: #just displays FPS
                debug_info = f"FPS: {int(self.clock.get_fps())}"
                pygame.display.set_caption(f"{WINDOW_TITLE} | {debug_info}")

            pygame.display.update()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()
    

    ##############################################################################################

if __name__ == "__main__":
    game = Game()
    game.run()