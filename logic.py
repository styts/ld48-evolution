from utils import AppState, resource_path
import pygame


class Player(object):

    def __init__(self, x, y):
        self.sprite = pygame.image.load(resource_path("data/sprites/player.png"))
        self.x = x
        self.y = y
        self.x_vel = 0
        self.y_vel = 0

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

    def process_input(self, event):
        # work the keys for moving
        # fixme: keydown?
        pass


        # if event.type == pygame.KEYUP and event.key == pygame.K_UP:
        #     self._accel(0, 1)
        # if event.type == pygame.KEYUP and event.key == pygame.K_DOWN:
        #     self._accel(0, -1)
        # if event.type == pygame.KEYUP and event.key == pygame.K_LEFT:
        #     self._accel(-1, 0)
        # if event.type == pygame.KEYUP and event.key == pygame.K_RIGHT:
        #     self._accel(1, 0)

    def draw(self, screen):
        screen.blit(self.sprite, (self.x, self.y))


class InGame(AppState):
    def process(self):
        self.player.process()
        return super(InGame, self).process()

    def reset(self):
        self.player = Player(self.app.screen_w / 2, self.app.screen_h / 2)

    def process_input(self, event):
        # quit to menu - ESC
        if event.type == pygame.KEYUP and event.key == pygame.K_ESCAPE:
            self.next_state = ("GoodBye", None)

        self.player.process_input(event)  # keys move me

    def draw(self):
        self.player.draw(self.app.screen)
