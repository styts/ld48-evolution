from utils import resource_path
import pygame
import math
import random

FLOOD_TIME = 40


class Sea(object):
    sprites = []
    c = (25, 123, 192)

    def __init__(self, app):
        self.sprites.append(pygame.image.load(resource_path('data/sprites/sea1.png')).convert_alpha())
        self.sprites.append(pygame.image.load(resource_path('data/sprites/sea2.png')).convert_alpha())

        self.cur_sprite = None
        self.x = -150
        self.solidsea = pygame.Surface(app.screen.get_size())
        self.solidsea.fill(Sea.c)
        self.sea_alpha = 255
        self.speed = 0
        self._i = 0
        self.flooding = False

    def flood(self):
        self.flooding = True
        self.x = -150
        self.speed = 10
        self._i = 0  # sprite index
        self.sea_alpha = 255

    def process(self):
        self.x += self.speed
        if random.randint(0, 10) == 0:  # once in a while, flip the sprite
            self._i = 1 if not self._i else 0
        if self.x > self.solidsea.get_width():
            self.sea_alpha -= 5
            self.solidsea.set_alpha(max(0, self.sea_alpha))
        if self.sea_alpha == 250:
            self.flooding = False
            return False
        else:
            return True

    def draw(self, screen):
        if self.x > self.solidsea.get_width():
            # blue screen
            if self.sea_alpha:
                screen.blit(self.solidsea, (0, 0))
        else:
            # wave
            spr = self.sprites[self._i]
            screen.blit(spr, (self.x, 0))
            screen.fill(Sea.c, pygame.Rect(0, 0, self.x, screen.get_height()))


class Safehouse(object):
    colors = [
        (120, 0, 0),  # r
        (0, 120, 0),  # g
        (0, 0, 120),  # b
        (0, 120, 120),
        (120, 0, 120),
        (120, 120, 0),
        (0, 180, 180),
        (180, 0, 180),
        (180, 180, 0),
    ]
    a = 100

    def __init__(self, x, y):
        self.color = random.choice(Safehouse.colors)
        self.r = pygame.Rect(x, y, Safehouse.a, Safehouse.a)
        self.lock = pygame.image.load(resource_path('data/sprites/lock.png')).convert_alpha()
        self.invis = pygame.image.load(resource_path('data/sprites/invisibility.png')).convert_alpha()

    def process(self):
        pass

    def draw(self, surface, player):
        pygame.draw.rect(surface, self.color, self.r)
        if player.is_safe():
            surface.blit(self.lock, (self.r.x + self.r.width - 24, self.r.y + self.r.height - 24))
        if player.is_invisible(self.color):
            surface.blit(self.invis, (self.r.x + self.r.width - 48, self.r.y + self.r.height - 24))


class Edible(object):
    colors = {'cherry': (50, -20, -20), 'berry': (-20, -20, 50), 'lime': (-20, 50, -20), 'blacky': (-50, -50, -50)}
    #colors = {'cherry': (40, -0, -0), 'berry': (-0, -0, 40), 'lime': (-0, 40, -0), 'blacky': (-40, -40, -40)}
    sprites = {'cherry': pygame.image.load(resource_path('data/sprites/cherry.png')),
               'berry': pygame.image.load(resource_path('data/sprites/berry.png')),
               'lime': pygame.image.load(resource_path('data/sprites/lime.png')),
               'blacky': pygame.image.load(resource_path('data/sprites/blacky.png'))}

    def __init__(self, x, y, name):
        self.x = x
        self.y = y
        self.color = Edible.colors[name]
        self.name = name
        self.sprite = Edible.sprites[name]

    def get_rect(self):
        # just a center point actually
        return pygame.Rect(self.x + 12, self.y + 12, 1, 1)  # 24: sprite width

    def draw(self, screen):
        screen.blit(self.sprite, (self.x, self.y))
        #pygame.draw.rect(screen, self.color, self.get_rect(), 1)


class Player(object):

    def __init__(self, x, y):
        self.sprite = pygame.image.load(resource_path("data/sprites/player.png")).convert_alpha()
        self.x = x
        self.y = y
        self.x_vel = 0
        self.y_vel = 0
        self.angle = 0
        self.color = (0, 0, 0)
        self.safe = False
        self.reset_color()

    def reset_color(self):
        self.color = (0, 0, 0)

    def process(self, safehouse):
        keys = pygame.key.get_pressed()
        #print keys
        if keys[pygame.K_LEFT]:
            self._accel(-1, 0)
        if keys[pygame.K_RIGHT]:
            self._accel(1, 0)
        if keys[pygame.K_UP]:
            self._accel(0, -1)
        if keys[pygame.K_DOWN]:
            self._accel(0, 1)

        # move according to velocities
        self.x += self.x_vel
        self.y += self.y_vel

        #self._head_rect = pygame.Rect(self.x + 45, self.y + 23, 20, 20)

        # reduce velocities (~ friction)
        a = 0.68
        if self.x_vel > a:
            self.x_vel -= a
        elif -self.x_vel > a:
            self.x_vel += a
        else:
            self.x_vel = 0
        if self.y_vel > a:
            self.y_vel -= a
        elif -self.y_vel > a:
            self.y_vel += a
        else:
            self.y_vel = 0

        # safe?
        if safehouse.r.contains(self.get_rect()):
            self.safe = True
        else:
            self.safe = False

    def is_safe(self):
        return self.safe

    def camouflage(self, bg_col):
        # how close are the colors
        d_r = abs(self.color[0] - bg_col[0])
        d_g = abs(self.color[1] - bg_col[1])
        d_b = abs(self.color[2] - bg_col[2])
        a = [d_r, d_g, d_b]
        s = sum(a)

        pogreshnost = 30
        s = s - pogreshnost
        cam = max(0, min(100, 100 - s))
        #print a, s, cam
        return cam

    def is_invisible(self, c):
        return self.camouflage(c) == 100  # 100% of camouflage

    def _accel(self, x_acc, y_acc):
        self.x_vel += x_acc
        self.y_vel += y_acc
        self.angle = math.degrees(math.atan2(self.x_vel, self.y_vel) - math.pi / 2)

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.sprite.get_width(), self.sprite.get_height())

    def can_eat(self, rect):
        return self.get_rect().contains(rect)

    def eat(self, edible):
        def n(colval):
            return max(0, min(255, colval))
        r, g, b = edible.color
        sr, sg, sb = self.color
        self.color = (n(sr + r), n(sg + g), n(sb + b))

    def draw(self, app):
        rot_sprite = pygame.transform.rotate(self.sprite, self.angle)
        rot_sprite.fill(self.color, None, pygame.BLEND_RGBA_MULT)
        app.screen.blit(rot_sprite, (self.x, self.y))
        #pygame.draw.line(app.screen, (255, 0, 0), (self.x, self.y), (self.x + self.x_vel, self.y + self.y_vel))
        #pygame.draw.rect(app.screen, (250, 0, 0), self.get_rect(), 1)
        #font_ren = app.font.render("%s" % self.angle, False, (200, 200, 200))
        #app.screen.blit(font_ren, (self.x - 30, self.y - 30))
