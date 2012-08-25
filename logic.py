from utils import AppState, resource_path
import pygame
import math
import random


class Safehouse(object):
    a = 100

    def __init__(self, x, y):
        self.color = (40, 80, 40)
        self.r = pygame.Rect(x, y, Safehouse.a, Safehouse.a)

    def process(self):
        pass

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.r)


class Edible(object):
    colors = {'cherry': (50, -20, -20), 'berry': (-20, -20, 50), 'lime': (-20, 50, -20)}
    sprites = {'cherry': pygame.image.load(resource_path('data/sprites/cherry.png')),
               'berry': pygame.image.load(resource_path('data/sprites/berry.png')),
               'lime': pygame.image.load(resource_path('data/sprites/lime.png'))}

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
        #self.color = (255, 255, 255)

    def process(self):
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


class InGame(AppState):
    #edibles = []
    #safehouse = None

    def process(self):
        self.player.process()

        for e in self.edibles:
            if self.player.can_eat(e.get_rect()):
                self.player.eat(e)
                self.edibles.remove(e)

        # randomly add edibles sometimes
        r = random.randint(0, 100)
        if r == 0:
            self._spawn_edible()

        # safehouse
        self.safehouse.process()

        return super(InGame, self).process()

    def _spawn_edible(self):

        while True:  # don't allow fruits inside the safehouse
            x = random.randint(0, self.app.screen_w)
            y = random.randint(0, self.app.screen_h)
            if not self.safehouse.r.colliderect(pygame.Rect(x, y, 24, 24)):
                break

        name = Edible.colors.keys()[random.randint(0, Edible.colors.keys().__len__() - 1)]
        e = Edible(x, y, name)
        self.edibles.append(e)

    def reset(self):
        self.edibles = []
        self.player = Player(self.app.screen_w / 2 - 32, self.app.screen_h / 2 - 32)
        self.background = pygame.Surface(self.app.screen.get_size())
        self.background.fill((200, 200, 200))

        self.safehouse = Safehouse(self.app.screen_w / 2 - Safehouse.a / 2, self.app.screen_h / 2 - Safehouse.a / 2)

        # spawn some edibles
        for i in xrange(10):
            self._spawn_edible()

    def process_input(self, event):
        # quit to menu - ESC
        if event.type == pygame.KEYUP and event.key == pygame.K_ESCAPE:
            self.next_state = ("GoodBye", None)

    def draw(self):
        self.app.screen.blit(self.background, (0, 0))

        self.safehouse.draw(self.app.screen)

        for e in self.edibles:
            e.draw(self.app.screen)

        self.player.draw(self.app)
