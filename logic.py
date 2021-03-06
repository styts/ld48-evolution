from utils import resource_path, fill_with_color, make_shadow
import pygame
import math
import random

SPAWN_RATE = 40  # lower means more food
FLOOD_TIME = 20  # seconds till flood

PLAYER_LIVES = 3  # maximums
BIRD_LIVES = 5
DIFFICULTY = 2


class HUD(object):
    def __init__(self, app):
        self.app = app

        self.hud = pygame.image.load(resource_path('data/sprites/hud.png')).convert_alpha()

        self.heart = pygame.image.load(resource_path('data/sprites/heart_ico.png')).convert_alpha()
        self.heart_dead = pygame.image.load(resource_path('data/sprites/heart_dead_ico.png')).convert_alpha()

        self.bird = pygame.image.load(resource_path('data/sprites/bird_ico.png')).convert_alpha()
        self.bird_dead = pygame.image.load(resource_path('data/sprites/bird_dead_ico.png')).convert_alpha()

        self.init()

    def init(self):
        self.player_lives = PLAYER_LIVES
        self.bird_lives = BIRD_LIVES

    def die(self, who):
        if who == "player":
            self.player_lives -= 1
        elif who == "bird":
            self.bird_lives -= 1
        if self.player_lives > 0 and self.bird_lives > 0:
            return 0
        elif self.player_lives <= 0:
            return -1
        elif self.bird_lives <= 0:
            return 1

    def draw(self, screen, fl_left):
        screen.blit(self.hud, (0, 0))
        x = 728
        a = 30
        # draw player lives
        for i in xrange(PLAYER_LIVES):
            if i < self.player_lives:
                sprite = self.heart
            else:
                sprite = self.heart_dead
            screen.blit(sprite, (x + (i - 1) * a, 5))

        # draw enemy lives
        for i in xrange(BIRD_LIVES):
            if i < self.bird_lives:
                sprite = self.bird
            else:
                sprite = self.bird_dead
            screen.blit(sprite, (screen.get_width() - 80 - (i - 1) * a, 5))

        # draw flood bar
        max_w = 150
        w = max_w / FLOOD_TIME * (fl_left)
        c = (42, 74, 164)
        if fl_left > 0:
            pygame.draw.rect(screen, c, pygame.Rect(255, 5, w, 25))


class Bird(object):
    states = ["PASSIVE", "SLIDE_OUT", "SEARCH", "SLIDE_IN"]
    srch_frames = 35  # ~ 1.2 seconds
    sprites = []
    shadows = []

    def __init__(self):
        s1 = pygame.image.load(resource_path('data/sprites/bird1.png')).convert_alpha()
        s2 = pygame.image.load(resource_path('data/sprites/bird2.png')).convert_alpha()
        self.sprites.append(s1)
        self.sprites.append(s2)
        # self.shadows.append(make_shadow(s1, 100))
        # self.shadows.append(make_shadow(s2, 100))

        self._i = 0
        self.reset()

    def process(self):
        if random.randint(0, 10) == 0:  # once in a while, flip the sprite
            self._i = 1 if not self._i else 0

        if self.state == "SLIDE_OUT":
            if self.x <= 246:
                self.x += 4
            else:
                self.state = "SEARCH"
        if self.state == "SEARCH":
            if self.srch_frames:
                self.srch_frames -= 1
            else:
                self.state = "SLIDE_IN"
        if self.state == "SLIDE_IN":
            if self.x:
                self.x -= 4
            else:
                self.state = "PASSIVE"

    def draw(self, screen):
        # sh = self.shadows[self._i]
        # screen.blit(sh, (self.x - 300 + 23, 200 + 23))
        spr = self.sprites[self._i]
        screen.blit(spr, (self.x - 300, 150))

    def reset(self):
        self.state = "PASSIVE"
        self.x = -50

    def eval(self):
        self.evaluated = True

    def show(self):
        self.state = "SLIDE_OUT"
        self.srch_frames = 35
        self.x = 0
        self._i = 0
        self.evaluated = False


class Sea(object):
    sprites = []
    c = (25, 123, 192)
    states = ["PASSIVE", "FLOODING", "STABLE", "DRYING"]

    def __init__(self, app):
        self.sprites.append(pygame.image.load(resource_path('data/sprites/sea1.png')).convert_alpha())
        self.sprites.append(pygame.image.load(resource_path('data/sprites/sea2.png')).convert_alpha())

        self.cur_sprite = None
        self.x = -150
        self.solidsea = pygame.Surface(app.screen.get_size())
        self.solidsea.fill(Sea.c)
        self.sea_alpha = 255
        self.speed = 0
        self._i = 0
        self.state = "PASSIVE"
        #self.stable_frames = 80

    def reset(self):
        self.state = "PASSIVE"
        self.sea_alpha = 255
        self.speed = 0
        self.x = -150
        self._i = 0  # sprite index
        self.stable_frames = 60

    def flood(self):
        self.reset()
        self.state = "FLOODING"
        self.speed = 10
        self.sea_alpha = 255
        self.solidsea.fill(Sea.c)
        self.solidsea.set_alpha(self.sea_alpha)

    def process(self):
        if self.state == "FLOODING":
            self.x += self.speed
            if random.randint(0, 10) == 0:  # once in a while, flip the sprite
                self._i = 1 if not self._i else 0
            if self.x > self.solidsea.get_width():
                self.state = "STABLE"
                #self.stable_frames = 120

        if self.state == "STABLE":
            self.stable_frames -= 1
            if not self.stable_frames:
                self.state = "DRYING"

        if self.state == "DRYING":
            self.sea_alpha -= 4
            self.solidsea.set_alpha(max(0, self.sea_alpha))
            if self.sea_alpha < 0:
                self.state = "PASSIVE"
        #print self.state, self.sea_alpha
        return self.x

    def draw(self, screen):
        if self.state == "DRYING" or self.state == "STABLE":
            screen.blit(self.solidsea, (0, 0))
        if self.state == "FLOODING":
            # wave
            spr = self.sprites[self._i]
            screen.blit(spr, (self.x, 0))
            screen.fill(Sea.c, pygame.Rect(0, 0, self.x, screen.get_height()))


class Safehouse(object):
    # colors = [
    #     (120, 0, 0),
    #     (0, 120, 0),
    #     (0, 0, 120),
    #     (0, 120, 60),
    #     (120, 0, 60),
    #     (120, 60, 0),
    #     (0, 120, 120),
    #     (120, 0, 120),
    #     (120, 120, 0),
    # ]
    a = 110  # side of it

    def __init__(self, x, y, diffuculty):
        self.r = pygame.Rect(x, y, Safehouse.a, Safehouse.a)
        self.lock = pygame.image.load(resource_path('data/sprites/lock.png')).convert_alpha()
        self.invis = pygame.image.load(resource_path('data/sprites/invisibility.png')).convert_alpha()
        self.orig_sprite = pygame.image.load(resource_path('data/sprites/safehouse.png')).convert_alpha()
        self.diffuculty = diffuculty

    def reset(self):
        #self.color = random.choice(Safehouse.colors)
        self.color = [0, 0, 0]
        n = random.randint(1, self.diffuculty)  # needed to collect
        vs = Edible.colors.values()
        vs.remove(Edible.colors['blacky'])
        for i in xrange(0, n):
            c = random.choice(vs)
            for j in xrange(0, 3):
                v = self.color[j] + c[j]
                self.color[j] = max(0, min(255, v))
        self.color = tuple(self.color)
        # fill sprite wiht a color
        self.sprite = fill_with_color(self.orig_sprite, self.color, 0)

    def draw(self, surface, player):
        surface.blit(self.sprite, self.r.move(-23, -13))
        #pygame.draw.rect(surface, self.color, self.r, 1)
        if player.is_safe():
            surface.blit(self.lock, (self.r.x + self.r.width - 24, self.r.y + self.r.height - 24))
        if player.is_invisible(self.color):
            surface.blit(self.invis, (self.r.x + self.r.width - 48, self.r.y + self.r.height - 24))


class Edible(object):
    colors = {'cherry': (80, -0, -0), 'berry': (-0, -0, 80), 'lime': (-0, 80, -0), 'blacky': (-40, -40, -40)}
    #colors = {'cherry': (40, -0, -0), 'berry': (-0, -0, 40), 'lime': (-0, 40, -0), 'blacky': (-40, -40, -40)}
    sprites = {'cherry': pygame.image.load(resource_path('data/sprites/cherry.png')),
               'berry': pygame.image.load(resource_path('data/sprites/berry.png')),
               'lime': pygame.image.load(resource_path('data/sprites/lime.png')),
               'blacky': pygame.image.load(resource_path('data/sprites/blacky.png'))}

    def __init__(self, x, y, name):
        self.x = x
        self.y = y
        self.color = Edible.colors[name]
        self.name = name
        self.sprite = Edible.sprites[name]

        for k, v in Edible.sprites.items():
            n = "%s_shadow" % k
            if n not in Edible.sprites.keys():
                s = make_shadow(v, 100)
                Edible.sprites[n] = s

        self.shadow = Edible.sprites["%s_shadow" % self.name]

    def get_rect(self):
        # just a center point actually
        return pygame.Rect(self.x + 12, self.y + 12, 1, 1)  # 24: sprite width

    def draw(self, screen):
        s_o = 2  # shadow offset
        screen.blit(self.shadow, (self.x + s_o, self.y + s_o))
        screen.blit(self.sprite, (self.x, self.y))



class Player(object):
    orig_color = (0, 0, 0)

    def __init__(self, x, y, diffuculty, app):
        self.app = app
        self.sprite = pygame.image.load(resource_path("data/sprites/player.png")).convert_alpha()
        self.sprite2 = pygame.image.load(resource_path("data/sprites/player2.png")).convert_alpha()
        self.x = x
        self.y = y
        self.diffuculty = diffuculty
        self.x_vel = 0
        self.y_vel = 0
        self.angle = 0
        self._i = False
        self.safe = False
        self.reset_color()
        self.sh1 = fill_with_color(self.sprite, (10, 10, 10), 200)
        self.sh2 = fill_with_color(self.sprite2, (10, 10, 10), 200)

    def reset_color(self):
        self.color = Player.orig_color
        #self.col_sprite = fill_with_color(self.sprite, self.color, 0)
        self._recolor()

    def process(self, safehouse):
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

        # safe?
        if safehouse.r.contains(self.get_rect()):
            self.safe = True
        else:
            self.safe = False

    def is_safe(self):
        return self.safe

    def camouflage(self, bg_col):
        # how close are the colors
        d_r = abs(self.color[0] - bg_col[0])
        d_g = abs(self.color[1] - bg_col[1])
        d_b = abs(self.color[2] - bg_col[2])
        a = [d_r, d_g, d_b]
        s = sum(a)

        pogreshnost = 10 * self.diffuculty
        s = s - pogreshnost
        cam = max(0, min(100, 100 - s))
        #print a, s, cam
        return cam

    def is_invisible(self, c):
        return self.camouflage(c) == 100  # 100% of camouflage

    def _accel(self, x_acc, y_acc):
        self.x_vel += x_acc
        self.y_vel += y_acc
        self.angle = math.degrees(math.atan2(self.x_vel, self.y_vel) - math.pi / 2)
        self._i = not self._i
        #self.app.audman.sfx("walk")

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.sprite.get_width(), self.sprite.get_height())

    def can_eat(self, rect):
        return self.get_rect().contains(rect)

    def _recolor(self):
        fill_color = self.color if any(self.color) > 0 else (50, 50, 50)
        self.col_sprite1 = fill_with_color(self.sprite, fill_color, 0)
        self.col_sprite2 = fill_with_color(self.sprite2, fill_color, 0)

    def eat(self, edible):
        def n(colval):
            return max(Player.orig_color[0], min(255, colval))
        r, g, b = edible.color
        sr, sg, sb = self.color
        self.color = (n(sr + r), n(sg + g), n(sb + b))
        self._recolor()

    def draw(self, app):
        col_sprite = self.col_sprite1 if self._i else self.col_sprite2
        sh = self.sh1 if self._i else self.sh2
        col_rot_sprite = pygame.transform.rotate(col_sprite, self.angle)
        rot_sh = pygame.transform.rotate(sh, self.angle)

        app.screen.blit(rot_sh, (self.x + 4, self.y + 4))
        app.screen.blit(col_rot_sprite, (self.x, self.y))
