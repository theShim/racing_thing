import contextlib
with contextlib.redirect_stdout(None):
    import pygame; pygame.init()
    from pygame.locals import *
    
import math
import random

from scripts.config.CORE_FUNCS import vec

    ##############################################################################################

class Trail(pygame.sprite.Sprite):
    def __init__(self, parent, pos, col=(0, 0, 0)):
        super().__init__()
        self.parent = parent #the all_sprites group, used to remove the sprite once its no longer needed
        self.z = 5

        self.pos = vec(pos) #position
        self.col = col #colour
        self.alpha = 255 #alpha value representing the current transparency 

        #the actual trail image, basically just a black circle
        self.surf = pygame.Surface((10, 10), pygame.SRCALPHA)
        pygame.draw.circle(self.surf, (15, 15, 15), (5, 5), 5)

    #main update method, causing the alpha to decay and drawing it
    def update(self, screen, offset):
        self.alpha -= 10
        if self.alpha <= 0:
            return self.parent.remove(self)
        self.draw(screen, offset)

    def draw(self, screen, offset):
        self.surf.set_alpha(self.alpha) #updating alpha transparency
        screen.blit(self.surf, self.pos-offset)


class Spark(pygame.sprite.Sprite):
    def __init__(self, parent, pos, scale, angle, speed=None, colour=(255, 255, 255), spin=False, grav=False):
        super().__init__()
        self.parent = parent
        self.z = 8

        self.pos = vec(pos)
        self.scale = scale
        self.angle = angle #current rotation
        self.speed = random.uniform(3, 6) if speed == None else speed #random speed
        self.colour = colour

        self.spin = spin #whether the spark should be spinning around or not
        self.grav = grav #whether the spark should be affected by gravity

        #pre-move the sparks a bit just so it doesnt' all start underneath the player
        for i in range(int(self.scale*2)+1):
            self.move()

    #moving the sparks, again with the vector velocity stuff
    def move(self):
        self.pos += vec(math.sin(self.angle), math.cos(self.angle)) * self.speed

    #gravity math
    def apply_gravity(self, friction, force, terminal_velocity):
        movement = vec(math.sin(self.angle), math.cos(self.angle)) * self.speed
        movement[1] = min(terminal_velocity, movement[1] + force)
        movement[0] *= friction
        self.angle = math.atan2(movement[1], movement[0])

    #main update loop
    def update(self, screen, offset):
        self.speed -= 0.1
        if self.speed < 0:
            return self.parent.remove(self)
        
        if self.spin:
            self.angle += 0.1
        if self.grav:
            self.apply_gravity(0.975, 0.2, 8)
        self.move()
        
        self.draw(screen, offset)

    def draw(self, screen, offset):
        #creating the spark polygon
        points = [
            vec(math.sin(self.angle), math.cos(self.angle)) * self.scale * self.speed,
            vec(math.sin(self.angle - math.pi/2), math.cos(self.angle - math.pi/2)) * 0.3 * self.scale * self.speed,
            vec(math.sin(self.angle - math.pi), math.cos(self.angle - math.pi)) * 3 * self.scale * self.speed + vec(random.random(), random.random())*self.speed,
            vec(math.sin(self.angle + math.pi/2), math.cos(self.angle + math.pi/2))  * 0.3 * self.scale * self.speed,
        ]
        points = list(map(lambda x: x+self.pos-offset, points)) #offsetting the polygon positions by where the player is and camera

        #solid fill
        pygame.draw.polygon(screen, self.colour, points)
        #border fill
        pygame.draw.polygon(screen, list(map(lambda x:sorted([x-30, 0, 255])[1], self.colour)), points, math.ceil(self.scale/4))


#more sparks but of specific colours depending on the current boost duration
#theres prolly a better way to implement it but whatever
class TyreSpark(Spark):

    @classmethod
    def cache_sprites(cls):
        cls.blue_turbo = pygame.image.load("assets/car/blue_turbo.png").convert_alpha()
        cls.yellow_turbo = pygame.image.load("assets/car/yellow_turbo.png").convert_alpha()
        cls.pink_turbo = pygame.image.load("assets/car/pink_turbo.png").convert_alpha()

    def __init__(self, parent, pos, scale, angle, duration):
        if 40 < duration <= 80:
            c = self.blue_turbo.get_at(
                (
                    random.randint(0, self.blue_turbo.get_width()-1),
                    random.randint(0, self.blue_turbo.get_height()-1),
                )
            ) 
        elif 80 < duration <= 120:
            c = self.yellow_turbo.get_at(
                (
                    random.randint(0, self.yellow_turbo.get_width()-1),
                    random.randint(0, self.yellow_turbo.get_height()-1),
                )
            ) 
            try:
                c[0] += 40
            except:
                c[0] = 255
        elif 120 < duration:
            c = self.pink_turbo.get_at(
                (
                    random.randint(0, self.pink_turbo.get_width()-1),
                    random.randint(0, self.pink_turbo.get_height()-1),
                )
            ) 
            try:
                c[0] += 30
            except:
                c[0] = 255
            try:
                c[1] -= 40
            except:
                c[1] = 255
            try:
                c[2] += 60
            except:
                c[2] = 255
        super().__init__(parent, pos, scale, angle, colour=c)

