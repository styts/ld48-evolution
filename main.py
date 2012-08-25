import pygame
import os
from utils import resource_path


class AppState(object):
    """The App class takes care of the state transitions between the finite state automaton which consists of AppStates
    Those could be: Menu, InGame, LevelComplete, GameOver, HighScores, etc.
    They should all implement the following methods.
    """
    i_wait = 0  # gets decremented every frame if > 0 (used for pausing)
    next_state = None  # holds None or a string with class name of the place to go
    hover_button = None
    CLICK_DELAY = 3  # nr of frames (3 ~ 100ms)

    def process(self):
        """Handles the mouse and keyboard"""

        if self.needs_wait():
            return None

        if self.next_state:
            return self.next_state

    def draw(self):
        """Draws stuff on app.screen ( don't forget to call app.dirty(rect) )"""
        raise NotImplementedError("Should be implemented in AppState subclass")

    def resume(self, arg):
        """Called form App when being switched to"""
        #raise NotImplementedError("Should be implemented in AppState subclass")
        self.hover_button = None
        self.next_state = None

    def _reset_background(self):
        """ draw the background"""
        self.app.screen.blit(self.app.background, (0, 0))
        #self.app.screen.fill((0, 0, 0))
        self.app.dirty(self.app.background.get_rect())

    def needs_wait(self):
        #print self.i_wait
        if self.i_wait > 0:
            self.i_wait = self.i_wait - 1
            return True
        return False

    def process_input(self, event):
        pass

    def wait(self, cycles):
        self.i_wait = cycles

    def __init__(self, app):
        self.app = app


class MainMenu(AppState):
    pass


class InGame(AppState):
    def process_input(self, event):
        # quit to menu - ESC
        if event.type == pygame.KEYUP and event.key == pygame.K_ESCAPE:
            self.next_state = ("GoodBye", None)

    def draw(self):
        pass


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

        self.font = pygame.font.Font(resource_path(os.path.join('data', 'fonts', 'visitor2.ttf')), 25)

        self._appstates = []
        #self._appstates.append(MainMenu(self))
        self._appstates.append(InGame(self))

        self.appstate = self._get_appstate("InGame")

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
        #self.dirty(self.screen.blit(fps_surf, (0, 0)))
        self.screen.blit(fps_surf, (0, 0))

        #pygame.display.update(self._dirty_rects)
        pygame.display.flip()  # (self.screen, (0, 0))
        pygame.event.pump()

app = App()
