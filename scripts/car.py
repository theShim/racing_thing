import contextlib
with contextlib.redirect_stdout(None):
    import pygame; pygame.init()
    from pygame.locals import *
    
import math
import random
import os

from scripts.particles import Trail, TyreSpark

from scripts.config.SETTINGS import WIDTH, HEIGHT
from scripts.config.CORE_FUNCS import vec, rotate

    ##############################################################################################

class Car(pygame.sprite.Sprite):

    #pre-loading/caching all of the car sprites, again to save time later
    images = [pygame.image.load('assets/car/' + img) for img in os.listdir('assets/car') if img.startswith("img_")]
    images = [pygame.transform.scale(img, (14*4, 20*4)) for img in images]

    IMAGES = {}
    #some funky sprite stacking stuff. would recommend watching dafluffypotato's video on it, where i got this idea from
    for angle in range(360):
        sprite = pygame.Surface((122, 122), pygame.SRCALPHA)
        for i, img in enumerate(images):
            rotated_img = pygame.transform.rotate(img, angle)
            sprite.blit(rotated_img, (sprite.get_width()//2 - rotated_img.get_width()//2, sprite.get_height()//2 + 8 - rotated_img.get_height()//2 - i*3))

        #using a mask to create the black outline of the car sprites
        mask = pygame.mask.from_surface(sprite)
        pygame.draw.polygon(sprite, (0, 0, 0), mask.outline(), 2)
        IMAGES[angle] = sprite


    def __init__(self, all_sprites: pygame.sprite.Group, pos=vec(WIDTH//2, HEIGHT//2)):
        super().__init__()
        self.images = Car.IMAGES.copy()
        self.all_sprites = all_sprites #
        self.z = 10

        #the current position and hitbox of the player
        self.pos = vec(pos) - vec(self.images[0].get_size())/2
        self.rect = self.images[0].get_rect(topleft=self.pos)
        self.width, self.height = self.images[0].get_size()

        self.vel = vec() #velocity
        self.acc = vec(.1, .1) #acceleration
        self.max_vel = 2 #speed cap / terminal velocity

        #few tyre objects just to produce tyre sparks and trail effects
        self.tyres = [
            vec(self.pos.x + self.width/2, self.pos.y + self.height/2),
            vec(self.pos.x + self.width/3, self.pos.y + self.height - 40),
            vec(self.pos.x + 2*self.width/3, self.pos.y + self.height - 40)
        ]
        
        self.rotation = 0 #the current rotation of the player
        self.prev_rotation = self.rotation #the rotation of the player last frame step
        self.drift_duration = 0 #how long the player should be drifting for
        self.turnSpeed = 2 #the speed at which the player can turn left or right
        self.speed = 6 #a scalar multiplier for the speed generally
        self.boost = 1 #a scalar multiplier for the speed while they dash (for the blue/orange/pink sparks)

        #jumping stuff for the sparks
        self.hopped = 0 
        self.hop_held = False
        self.hop_height = 10


    def move(self, keys):

        #drifting
        if keys[pygame.K_LSHIFT]:
            if keys[pygame.K_LEFT]:
                self.prev_rotation += self.turnSpeed / 1.25
            if keys[pygame.K_RIGHT]:
                self.prev_rotation -= self.turnSpeed / 1.25
            radians = math.radians(self.prev_rotation)

            if keys[pygame.K_UP]:
                self.drift_duration += 1
            else:
                self.drift_duration = 0

        else:
            if 40 < self.drift_duration <= 80:
                self.boost = 1.6
            elif 80 < self.drift_duration <= 120:
                self.boost = 2.6
            elif 120 < self.drift_duration:
                self.boost = 3.6
                
            self.prev_rotation = self.rotation
            radians = math.radians(self.rotation)
            self.drift_duration = 0


        max_vel = self.max_vel
        # #accelerating
        if keys[pygame.K_DOWN]:
            self.vel.x = min(self.vel.x + self.acc.x, max_vel / 2)
            self.vel.y = min(self.vel.y + self.acc.y, max_vel / 2)
        elif keys[pygame.K_UP]:
            self.vel.x = max(self.vel.x - self.acc.x, -max_vel)
            self.vel.y = max(self.vel.y - self.acc.y, -max_vel)

        #slowing down
        else:
            if self.vel.x >= 0: self.vel.x = max(self.vel.x - self.acc.x, 0)
            else:              self.vel.x = min(self.vel.x + self.acc.x, max_vel)

            if self.vel.y >= 0: self.vel.y = max(self.vel.y - self.acc.y, 0)
            else:              self.vel.y = min(self.vel.y + self.acc.y, max_vel)

        #applying friction
        vel = self.vel.copy()
        if vel.x != 0.0 and vel.y != 0.0:
            vel *= 1/math.sqrt(2)

        #gradually lowering the effect of the boost
        if self.boost > 1:
            self.boost -= 0.05

        #the actual math, converting the angle to a vector velocity as (cos(a), sin(a)), then applying that velocity to the position
        dx = math.sin(radians) * vel.x * self.speed * self.boost
        dy = math.cos(radians) * vel.y * self.speed * self.boost

        self.pos.x += dx
        self.pos.y += dy

        #jumping stuff
        if self.hopped != 0:
            self.pos.y -= self.hopped
            if self.hopped == 1:
                self.hopped -= 2
            elif self.hopped == -self.hop_height:
                self.hopped = 0
            else:
                self.hopped -= 1

    #turning left or right
    def rotate(self, keys):
        if keys[pygame.K_LEFT]:
            self.rotation += self.turnSpeed
        if keys[pygame.K_RIGHT]:
            self.rotation -= self.turnSpeed

    #jumping
    def hop(self, keys):
        if keys[pygame.K_LSHIFT]:
            if self.hopped == 0 and self.hop_held == False:
                self.hopped = self.hop_height
                self.hop_held = True
                self.before_hop = self.pos.copy()
        else:
            self.hop_held = False

    #main update method
    def update(self, screen, offset):
        keys = pygame.key.get_pressed()
        self.rotate(keys)
        self.move(keys)
        self.hop(keys)

        #updating tyre positions every frame
        self.tyres = [
            vec(self.pos.x + self.width/2, self.pos.y + self.height/2),
            vec(self.pos.x + self.width/3, self.pos.y + self.height - 40),
            vec(self.pos.x + 2*self.width/3, self.pos.y + self.height - 40)
        ]
        self.render(screen, offset)

    #blitting the current rotation of the player on screen, and tyre stuff in terms of particle effects
    def render(self, screen, offset):
        img = self.images[int(self.rotation%360)].copy()
        self.rect = img.get_rect(topleft=self.pos)
        screen.blit(img, self.pos-offset)

        #tyre
        for tyre in self.tyres[1:]:
            p = vec(rotate(self.tyres[0], tyre, self.rotation))

            if pygame.key.get_pressed()[pygame.K_LSHIFT]:
                if self.hopped == 0:
                    self.all_sprites.add(Trail(self.all_sprites, p))
                    radians = math.radians(self.rotation)

                    x = math.sin(radians) * self.vel.x
                    y = math.cos(radians) * self.vel.y

                    for i in range(4):
                        p.x += x * 1.5
                        p.y += y * 1.5
                        self.all_sprites.add(Trail(self.all_sprites, p))

                    if self.drift_duration > 40 and int(random.uniform(0, 3))/10 == 0:
                        radians = math.radians(self.rotation)
                        x = math.sin(radians) * self.vel.x
                        y = math.cos(radians) * self.vel.y
                        self.all_sprites.add(TyreSpark(self.all_sprites, p, random.uniform(2, 4), radians, self.drift_duration)) 

#wheel class, could be a dataclass
class Wheel:
    def __init__(self, pos):
        self.pos = vec(pos)
        self.angle = 0