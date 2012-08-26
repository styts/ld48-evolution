import pygame
import os
from utils import resource_path
from states import *


class App():
    screen_w = 1024
    screen_h = 768

    appstate = None  # holds an AppState subclass instance (Menu, InGame, etc.)

    _dirty_rects = []

    def __init__(self):
        os.environ['SDL_VIDEO_CENTERED'] = '1'

        pygame.init()
        pygame.display.set_mode((App.screen_w, App.screen_h))  # , FULLSCREEN)
        pygame.display.set_caption('Evolution Game')
        self.screen = pygame.display.get_surface()
        self.is_running = True  # used to trigger exit by ESC

        self.clock = pygame.time.Clock()

        self.font = pygame.font.Font(resource_path(os.path.join('data', 'fonts', 'visitor2.ttf')), 24)  # or 25?
        self.font_big = pygame.font.Font(resource_path(os.path.join('data', 'fonts', 'visitor2.ttf')), 64)

        self._appstates = []
        self._appstates.append(MenuMain(self))
        self._appstates.append(MenuHelp(self))
        self._appstates.append(InGame(self))
        self._appstates.append(DeathBySea(self))

        #self.appstate = self._get_appstate("InGame")
        #self.appstate.reset()

        self.appstate = self._get_appstate("MenuMain")

        ## Main Loop
        while self.is_running:
            self.process()
        pygame.quit()  # cleanup finally

    def _get_appstate(self, s):
        for astate in self._appstates:
            if astate.__class__.__name__ == s:
                return astate

    def process(self):
        self.clock.tick(30)

        p = self.appstate.process()
        if p:
            next_state, state_arg = p
            if next_state:
                if next_state == "GoodBye":
                    self.is_running = False
                else:
                    # appstate wants to change!
                    self.appstate = self._get_appstate(next_state)
                    self.appstate.resume(state_arg)

        events = pygame.event.get()
        for event in events:
            p = self.appstate.process_input(event)

            # ESC quits app
            if event.type == pygame.QUIT:
                self.is_running = False

        ## DRAW
        self.appstate.draw()

        # write fps
        fps_surf = self.font.render("FPS: %2.2f" % self.clock.get_fps(), False, (255, 255, 255), (0, 0, 0))
        self.screen.blit(fps_surf, (0, 0))

        pygame.display.flip()
        pygame.event.pump()

app = App()
