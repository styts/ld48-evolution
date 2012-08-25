from utils import AppState, resource_path
import pygame
import math
import random


class Edible(object):
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color

    def get_rect(self):
        return pygame.Rect(self.x - 5, self.y - 5, 10, 10)

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (self.x, self.y), 10, 0)
        #pygame.draw.rect(screen, self.color, self.get_rect(), 1)


class Player(object):

    def __init__(self, x, y):
        self.sprite = pygame.image.load(resource_path("data/sprites/player.png"))
        self.x = x
        self.y = y
        self.x_vel = 0
        self.y_vel = 0
        self.angle = 0

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
        return self.get_rect().colliderect(rect)

    def draw(self, app):
        rot_sprite = pygame.transform.rotate(self.sprite, self.angle)
        app.screen.blit(rot_sprite, (self.x, self.y))
        #pygame.draw.line(app.screen, (255, 0, 0), (self.x, self.y), (self.x + self.x_vel, self.y + self.y_vel))
        #pygame.draw.rect(app.screen, (250, 0, 0), self.get_rect(), 1)
        #font_ren = app.font.render("%s" % self.angle, False, (200, 200, 200))
        #app.screen.blit(font_ren, (self.x - 30, self.y - 30))


class InGame(AppState):
    edibles = []

    def process(self):
        self.player.process()

        for e in self.edibles:
            if self.player.can_eat(e.get_rect()):
                # ate!
                self.edibles.remove(e)

        # randomly add edibles sometimes
        r = random.randint(0, 100)
        if r == 0:
            self._spawn_edible()

        return super(InGame, self).process()

    def _spawn_edible(self):
        x = random.randint(0, self.app.screen_w)
        y = random.randint(0, self.app.screen_h)
        color = (random.randint(50, 255), random.randint(50, 255), random.randint(50, 255))
        e = Edible(x, y, color)
        self.edibles.append(e)

    def reset(self):
        self.player = Player(self.app.screen_w / 2, self.app.screen_h / 2)
        self.background = pygame.Surface(self.app.screen.get_size())

        # spawn some edibles
        for i in xrange(10):
            self._spawn_edible()

    def process_input(self, event):
        # quit to menu - ESC
        if event.type == pygame.KEYUP and event.key == pygame.K_ESCAPE:
            self.next_state = ("GoodBye", None)

    def draw(self):
        self.app.screen.blit(self.background, (0, 0))

        for e in self.edibles:
            e.draw(self.app.screen)

        self.player.draw(self.app)
