from utils import *
from logic import *


class Victory(AppState):
    def __init__(self, app):
        self.app = app
        self.surface = pygame.image.load(resource_path('data/sprites/victory.png')).convert()

    def draw(self):
        self.app.screen.blit(self.surface, (0, 0))

    def process_input(self, event):
        if event.type == pygame.KEYUP and event.key in [pygame.K_RETURN, pygame.K_SPACE, pygame.K_ESCAPE]:
            self.next_state = ("MenuMain", None)


class Defeat(AppState):
    def __init__(self, app):
        self.app = app
        self.surface = pygame.image.load(resource_path('data/sprites/defeat.png')).convert()

    def draw(self):
        self.app.screen.blit(self.surface, (0, 0))

    def process_input(self, event):
        if event.type == pygame.KEYUP and event.key in [pygame.K_RETURN, pygame.K_SPACE, pygame.K_ESCAPE]:
            self.next_state = ("MenuMain", None)


class MenuHelp(AppState):
    def __init__(self, app):
        self.app = app
        self.surface = pygame.image.load(resource_path('data/sprites/menuhelp.png')).convert()

    def draw(self):
        self.app.screen.blit(self.surface, (0, 0))

    def process_input(self, event):
        if event.type == pygame.KEYUP and event.key in [pygame.K_RETURN, pygame.K_SPACE, pygame.K_ESCAPE]:
            self.next_state = ("MenuMain", None)


class MenuMain(AppState):
    """Text-style menu, could be reused (TODO)"""
    def __init__(self, app):
        self.app = app
        self.surface = pygame.image.load(resource_path('data/sprites/mainmenu.png')).convert()
        self.items = ["NEW GAME", "HELP", "EXIT"]
        self.next_states = [("InGame", None), ("MenuHelp", None), ("GoodBye", None)]
        self.cur_item = 0
        self.c = (248, 188, 27)
        self.c_sel = (124, 111, 27)
        self.c_sh = (149, 140, 117)

    def draw(self):
        self.app.screen.blit(self.surface, (0, 0))

        x = self.app.screen_w / 2
        y = self.app.screen_h / 2
        a = 100
        for i in xrange(self.items.__len__()):
            c = self.c if i != self.cur_item else self.c_sel
            item = self.items[i]
            ren = self.app.font_big.render(item, False, c)
            sh_ren = self.app.font_big.render(item, False, self.c_sh)
            self.app.screen.blit(sh_ren, (x + 3 - ren.get_width() / 2, y + 3))
            self.app.screen.blit(ren, (x - ren.get_width() / 2, y))
            y += a

    def _move_down(self):
        self.cur_item = self.cur_item + 1 if self.cur_item < self.items.__len__() - 1 else 0

    def _move_up(self):
        self.cur_item = self.cur_item - 1 if self.cur_item >= 1 else self.items.__len__() - 1

    def _select(self):
        self.next_state = self.next_states[self.cur_item]

    def process_input(self, event):
        if event.type == pygame.KEYUP and event.key == pygame.K_UP:
            self._move_up()
        if event.type == pygame.KEYUP and event.key == pygame.K_DOWN:
            self._move_down()
        if event.type == pygame.KEYUP and event.key == pygame.K_RETURN:
            self._select()


class MenuPaused(MenuMain):
    def __init__(self, app):
        super(MenuPaused, self).__init__(app)
        self.items = ["RESUME", "QUIT GAME"]
        self.next_states = [("InGame", "unpause"), ("MenuMain", None)]


class DeathBySea(AppState):
    def __init__(self, app):
        self.app = app
        self.surface = pygame.image.load(resource_path('data/sprites/death_by_sea.png')).convert()

    def draw(self):
        self.app.screen.blit(self.surface, (0, 0))

    def resume(self, arg):
        super(DeathBySea, self).resume(arg)
        self.ns = "InGame" if arg >= 0 else "Defeat"

    def process_input(self, event):
        if event.type == pygame.KEYUP and event.key in [pygame.K_RETURN, pygame.K_SPACE, pygame.K_ESCAPE]:
            self.next_state = (self.ns, "new")


class InGame(AppState):
    def __init__(self, app):
        super(InGame, self).__init__(app)

        self.grounds = []
        for i in xrange(1, 5):
            self.grounds.append(pygame.image.load(resource_path('data/sprites/ground/%s.png' % i)).convert())

        self.reset()

    def resume(self, arg):
        super(InGame, self).resume(arg)
        #print arg
        if arg and arg == "new":
            self.new_level()
        elif arg and arg == "unpause":
            pass  # do nothing
        else:
            self.reset()
        #print self.sea_counter, self.sea.state

    def process(self):

        self.player.process(self.safehouse)

        # eat any edibles
        for e in self.edibles:
            if self.player.can_eat(e.get_rect()):
                self.player.eat(e)
                self.edibles.remove(e)

        # randomly add edibles sometimes
        r = random.randint(0, SPAWN_RATE)  # oftenness of edibles, spawn rate
        if r == 0:
            self._spawn_edible()

        self.bird.process()
        sea_x = self.sea.process()
        if sea_x > self.player.get_rect().x and self.sea.state == "FLOODING":
            if self.bird.state == "PASSIVE":
                self.bird.show()
        if self.bird.state == "SLIDE_IN" and not self.bird.evaluated:
            self._evaluate()
            self.player.reset_color()
            self.safehouse.reset()
            self._reset_edibles()
        #print self.bird.state, "secount", self.sea_counter, self.sea.state, self.sea.sea_alpha

        if self.bird.state == "PASSIVE" and not self.sea_counter:
            self.sea.reset()

        # decrement sea counter
        if self.sea.state == "PASSIVE":
            self.sea_counter -= 1
            if self.sea_counter <= 0:
                self.sea.flood()
                self.sea_counter = FLOOD_TIME * 30

        # test death by sea
        pr = self.player.get_rect()
        if self.sea.sea_alpha == 255 and pr.x < self.sea.x and not self.player.is_safe():
            l = self.hud.die("player")
            self.next_state = ("DeathBySea", l)

        return super(InGame, self).process()

    def _evaluate(self):
        self.bird.eval()
        percent = self.player.camouflage(self.safehouse.color)
        e = random.randint(0, 100)
        live = e <= percent
        char = "bird" if live else "player"
        res = self.hud.die(char)
        if res < 0:
            self.next_state = ("Defeat", None)
        elif res > 0:
            self.next_state = ("Victory", None)

    def _spawn_edible(self):

        while True:  # don't allow fruits inside the safehouse
            x = random.randint(0, self.app.screen_w)
            y = random.randint(0, self.app.screen_h)
            if not self.safehouse.r.inflate(30, 30).colliderect(pygame.Rect(x, y, 24, 24)) and y > 42:  # make hud visible
                break

        name = Edible.colors.keys()[random.randint(0, Edible.colors.keys().__len__() - 1)]
        e = Edible(x, y, name)
        self.edibles.append(e)

    def _reset_edibles(self):
        self.edibles = []
        for i in xrange(10):
            self._spawn_edible()

    def _reset_bg(self):
        self.background.fill((172, 168, 157))
        for i in xrange(1, 20):  # we need 20?
            s = random.choice(self.grounds)
            x = random.randint(0, self.app.screen_w - 30)
            y = random.randint(42, self.app.screen_h - 30)
            self.background.blit(s, (x, y))

    def new_level(self):
        self.sea_counter = FLOOD_TIME * 30

        self._reset_bg()

        self.sea.reset()
        self.bird.reset()
        self._playa_reset()
        self.safehouse.reset()

        self._reset_edibles()

    def reset(self):
        self.background = pygame.Surface(self.app.screen.get_size())
        self._reset_bg()

        self.sea = Sea(self.app)
        self.bird = Bird()
        self.hud = HUD(self.app)

        self._playa_reset()
        self.safehouse = Safehouse(self.app.screen_w / 2 - Safehouse.a / 2, self.app.screen_h / 2 - Safehouse.a / 2)

        self.new_level()

    def _playa_reset(self):
        self.player = Player(self.app.screen_w / 2 - 32, self.app.screen_h / 2 - 32)
        self.player.reset_color()

    def process_input(self, event):
        # quit to menu - ESC
        if event.type == pygame.KEYUP and event.key == pygame.K_ESCAPE:
            self.next_state = ("MenuPaused", None)

    def draw(self):
        self.app.screen.blit(self.background, (0, 0))

        for e in self.edibles:
            e.draw(self.app.screen)

        self.sea.draw(self.app.screen)
        self.safehouse.draw(self.app.screen, self.player)

        self.player.draw(self.app)
        self.bird.draw(self.app.screen)
        self.hud.draw(self.app.screen, self.sea_counter / 30)

        if self.sea.state == "PASSIVE":
            f_ren = self.app.font.render("Flood in %s sec" % (self.sea_counter / 30), False, (0, 0, 50))
            self.app.screen.blit(f_ren, (150, 5))

        f_ren = self.app.font_med.render("%s%%" % (self.player.camouflage(self.safehouse.color)), False, (255, 255, 255))
        self.app.screen.blit(f_ren, (530, 5))
