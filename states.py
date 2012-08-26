from utils import *
from logic import *


class MenuHelp(AppState):
    def __init__(self, app):
        self.app = app
        self.surface = pygame.image.load(resource_path('data/sprites/menuhelp.png')).convert()

    def draw(self):
        self.app.screen.blit(self.surface, (0, 0))

    def process_input(self, event):
        if event.type == pygame.KEYUP and event.key == pygame.K_ESCAPE:
            self.next_state = ("MenuMain", None)


class MenuMain(AppState):
    """Text-style menu, could be reused (TODO)"""
    def __init__(self, app):
        self.app = app
        self.surface = pygame.image.load(resource_path('data/sprites/mainmenu.png')).convert()
        self.items = ["NEW GAME", "HELP", "EXIT"]
        self.next_states = ["InGame", "MenuHelp", "GoodBye"]
        self.cur_item = 0
        self.c = (248, 188, 27)
        self.c_sel = (124, 111, 27)

    def draw(self):
        self.app.screen.blit(self.surface, (0, 0))

        x = self.app.screen_w / 2
        y = self.app.screen_h / 2
        a = 100
        for i in xrange(self.items.__len__()):
            c = self.c if i != self.cur_item else self.c_sel
            item = self.items[i]
            ren = self.app.font_big.render(item, False, c)
            self.app.screen.blit(ren, (x - ren.get_width() / 2, y))
            y += a

    def _move_down(self):
        self.cur_item = self.cur_item + 1 if self.cur_item < self.items.__len__() - 1 else 0

    def _move_up(self):
        self.cur_item = self.cur_item - 1 if self.cur_item >= 1 else self.items.__len__() - 1

    def _select(self):
        self.next_state = (self.next_states[self.cur_item], None)

    def process_input(self, event):
        if event.type == pygame.KEYUP and event.key == pygame.K_UP:
            self._move_up()
        if event.type == pygame.KEYUP and event.key == pygame.K_DOWN:
            self._move_down()
        if event.type == pygame.KEYUP and event.key == pygame.K_RETURN:
            self._select()


class DeathBySea(AppState):
    def __init__(self, app):
        self.app = app
        self.surface = pygame.image.load(resource_path('data/sprites/death_by_sea.png')).convert()

    def draw(self):
        self.app.screen.blit(self.surface, (0, 0))

    def process_input(self, event):
        if event.type == pygame.KEYUP and event.key == pygame.K_ESCAPE:
            self.next_state = ("MainMenu", None)


class InGame(AppState):
    def __init__(self, app):
        super(InGame, self).__init__(app)
        self.reset()

    def process(self):
        self.player.process(self.safehouse)

        for e in self.edibles:
            if self.player.can_eat(e.get_rect()):
                self.player.eat(e)
                self.edibles.remove(e)

        # randomly add edibles sometimes
        r = random.randint(0, 40)  # oftenness of edibles, spawn rate
        if r == 0:
            self._spawn_edible()

        self.safehouse.process()
        self.bird.process()
        sea_x = self.sea.process()
        if sea_x > self.player.get_rect().x:
            if self.bird.state == "PASSIVE":
                self.bird.show()
            if self.bird.state == "FINISHED":
                self.semi_reset()

        # decrement sea counter
        self.sea_counter -= 1
        if self.sea_counter <= 0:
            self.sea.flood()
            self.sea_counter = FLOOD_TIME * 30

        # test death by sea
        pr = self.player.get_rect()
        if self.sea.sea_alpha == 255 and pr.x < self.sea.x and not self.player.is_safe():
            self.next_state = ("DeathBySea", None)

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

    def semi_reset(self):
        self.safehouse = Safehouse(self.app.screen_w / 2 - Safehouse.a / 2, self.app.screen_h / 2 - Safehouse.a / 2)
        self.sea_counter = FLOOD_TIME * 30
        self.sea.x = -150
        self.bird.state = "PASSIVE"
        self.player.reset_color()

        self.edibles = []

        # spawn some edibles
        for i in xrange(10):
            self._spawn_edible()

    def reset(self):
        self.player = Player(self.app.screen_w / 2 - 32, self.app.screen_h / 2 - 32)
        self.background = pygame.Surface(self.app.screen.get_size())
        self.background.fill((200, 200, 200))

        self.sea = Sea(self.app)
        self.bird = Bird()
        self.semi_reset()

    def process_input(self, event):
        # quit to menu - ESC
        if event.type == pygame.KEYUP and event.key == pygame.K_ESCAPE:
            self.next_state = ("GoodBye", None)

    def draw(self):
        self.app.screen.blit(self.background, (0, 0))

        for e in self.edibles:
            e.draw(self.app.screen)

        self.sea.draw(self.app.screen)
        self.safehouse.draw(self.app.screen, self.player)

        self.player.draw(self.app)
        self.bird.draw(self.app.screen)

        if self.sea.state == "PASSIVE":
            f_ren = self.app.font.render("Flood in %s sec" % (self.sea_counter / 30), False, (0, 0, 50))
            self.app.screen.blit(f_ren, (150, 5))

        f_ren = self.app.font.render("Camouflage %s%%" % (self.player.camouflage(self.safehouse.color)), False, (255, 255, 255))
        self.app.screen.blit(f_ren, (350, 5))
