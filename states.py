from utils import *
from logic import *


class DeathBySea(AppState):
    def __init__(self, app):
        self.app = app
        self.surface = pygame.image.load(resource_path('data/sprites/death_by_sea.png')).convert()

    def draw(self):
        self.app.screen.blit(self.surface, (0, 0))

    def process_input(self, event):
        if event.type == pygame.KEYUP and event.key == pygame.K_ESCAPE:
            self.next_state = ("GoodBye", None)


class InGame(AppState):

    def process(self):
        self.player.process(self.safehouse)

        for e in self.edibles:
            if self.player.can_eat(e.get_rect()):
                self.player.eat(e)
                self.edibles.remove(e)

        # randomly add edibles sometimes
        r = random.randint(0, 50)  # oftenness of edibles
        if r == 0:
            self._spawn_edible()

        self.safehouse.process()
        sp = self.sea.process()
        if not sp:
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

        self.edibles = []

        # spawn some edibles
        for i in xrange(10):
            self._spawn_edible()

    def reset(self):
        self.player = Player(self.app.screen_w / 2 - 32, self.app.screen_h / 2 - 32)
        self.background = pygame.Surface(self.app.screen.get_size())
        self.background.fill((200, 200, 200))

        self.sea = Sea(self.app)
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

        if not self.sea.flooding:
            f_ren = self.app.font.render("Flood: %s" % (self.sea_counter / 30), False, (0, 0, 50))
            self.app.screen.blit(f_ren, (150, 5))
