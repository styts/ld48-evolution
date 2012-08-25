from utils import AppState, resource_path
import pygame


class Player(object):
    x = 100
    y = 200
    x_vel = 0
    y_vel = 0

    def __init__(self, x, y):
        self.sprite = pygame.image.load(resource_path("data/sprites/player.png"))

    def process(self):
        pass
        # residual movement?

    def process_input(self, event):
        pass
        # todo work the keys for moving

    def draw(self, screen):
        screen.blit(self.sprite, (self.x, self.y))


class InGame(AppState):
    def reset(self):
        self.player = Player(self.app.screen_w/2, self.app.screen_h/2)

    def process_input(self, event):
        # quit to menu - ESC
        if event.type == pygame.KEYUP and event.key == pygame.K_ESCAPE:
            self.next_state = ("GoodBye", None)

    def draw(self):
        self.player.draw(self.app.screen)
