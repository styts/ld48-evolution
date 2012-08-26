import sys
import os
import pygame


def make_shadow(surface, alpha=150):
    siz = surface.get_size()
    shadow = pygame.Surface(siz, pygame.SRCALPHA)
    # for each pixel in button glyph
    for a in xrange(siz[0]):
        for b in xrange(siz[1]):
            # set corresponding value in shadow surface to be semi-transparent
            c = surface.get_at((a, b))
            s = c if all(c) == 0 else (0, 0, 0, alpha)
            shadow.set_at((a, b), s)
    return shadow


def fill_with_color(surf, color, alpha_decr=0):
    s = surf.copy()
    s.fill(color, None, pygame.BLEND_RGBA_MULT)

    sprite = s
    for a in xrange(sprite.get_width()):
        for b in xrange(sprite.get_height()):
            c = sprite.get_at((a, b))
            s = (c.r, c.g, c.b, max(0, c.a - alpha_decr) if c.r or c.g or c.b else 0)
            sprite.set_at((a, b), s)
    return sprite


def resource_path(relative):
    """Used by pyInstaller. Correct path prefix when running as frozen app/exe"""

    if getattr(sys, 'frozen', None):
        basedir = sys._MEIPASS  # production
    else:
        basedir = os.path.join(os.path.dirname(__file__))  # dev

    #print basedir

    return os.path.join(
        basedir,
        relative
    )


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
