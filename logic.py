from utils import AppState
import pygame


class Player(object):
    x = 100
    y = 200
    x_vel = 0
    y_vel = 0


class InGame(AppState):
    def reset(self):
        self.player = Player()

    def process_input(self, event):
        # quit to menu - ESC
        if event.type == pygame.KEYUP and event.key == pygame.K_ESCAPE:
            self.next_state = ("GoodBye", None)

    def draw(self):
        pass
