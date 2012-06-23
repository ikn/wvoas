import pygame as pg

from ext import evthandler as eh
from ext.colhandler import Rect, StaticObject, Object, CollisionHandler

import conf


class Player:
    def __init__ (self, pos):
        x, y = pos
        w, h = conf.PLAYER_SIZE
        self.rect = Rect(x, y, x + w, y + h)
        self.obj = Object(conf.PLAYER_MASS, self.rect,
                          elast = conf.PLAYER_ELAST)
        self.on_ground = False
        self.jumping = 0
        self.jumped = False

    def touching_cb (self, o1, o2, dirn, i1, i2):
        assert o1 is self.obj
        if dirn == 3:
            self.on_ground = True

    def move (self, dirn):
        speed = conf.PLAYER_SPEED if self.on_ground else conf.PLAYER_AIR_SPEED
        self.obj.vel[0] += (1 if dirn else -1) * speed

    def jump (self, press):
        v = self.obj.vel
        if press:
            if self.on_ground and not self.jumping:
                v[1] -= conf.INITIAL_JUMP
                self.jumping = conf.JUMP_TIME
        elif self.jumping:
            self.jumped = True

    def update (self):
        vx, vy = self.obj.vel
        # gravity
        vy += conf.GRAV
        # friction
        if self.on_ground:
            vx *= 1 - conf.FRICT
        # air resistance
        dx = 1 if vx > 0 else -1
        vx -= dx * conf.AIR_RES * vx ** 2
        vx = dx * max(dx * vx, 0)
        dy = 1 if vy > 0 else -1
        vy -= dy * conf.AIR_RES * vy ** 2
        vy = dy * max(dy * vy, 0)
        # jump
        if self.jumped:
            vy -= conf.CONTINUE_JUMP
        self.jumped = False
        # update things
        self.obj.vel = [vx, vy]
        self.on_ground = False
        if self.jumping:
            self.jumping -= 1


class Level:
    def __init__ (self, game, event_handler, ID = 0):
        self.game = game
        self.event_handler = event_handler
        self.ID = ID
        self.frame = conf.FRAME
        # input
        event_handler.add_key_handlers([
            (ks, [(self.move, (i,))], eh.MODE_HELD)
            for i, ks in enumerate(conf.KEYS_MOVE)
        ] + [
            (conf.KEYS_JUMP, self.jump, eh.MODE_ONDOWN_REPEAT, 1, 1),
            ((pg.K_ESCAPE,), lambda *args: setattr(self, 'show', not self.show), eh.MODE_ONDOWN)
        ])
        self.show = False
        self.rect = pg.Rect(0, 0, *conf.RES).inflate(-10, -10)
        self.init()

    def init (self):
        data = conf.LEVELS[self.ID]
        # player
        self.player = Player(data['player_pos'])
        # goal
        x, y = data['goal']
        w, h = conf.GOAL_SIZE
        self.goal = Rect(x, y, x + w, y + h)
        # window
        x, y = self.player.rect.centre
        w, h = conf.HALF_WINDOW_SIZE
        self.window = pg.Rect(x - w, y - h, 2 * w, 2 * h)
        # objs
        w, h = conf.RES
        self.rects = [Rect(*args) for args in data['rects']]
        self.objs = [StaticObject(s, conf.OBJ_ELAST) for s in self.rects + [self.goal]]
        # colhandler
        self.col_handler = CollisionHandler([self.player.obj] + self.objs,
            self.filter_col, self.col_cb, self.player.touching_cb)
        pg.mouse.set_pos(self.rect.center)

    def move (self, key, mode, mods, i):
        self.player.move(i)

    def jump (self, key, mode, mods):
        self.player.jump(mode == 0)

    def filter_col (self, o1, o2, dirn, i1, i2, data):
        c = self.window.clip
        for s in (o1.shape, o2.shape):
            if s is self.goal:
                self.win()
                return True
            if isinstance(s, Rect):
                r = s.pgrect
            else: # HalfLine
                size = [0, 0]
                size[s.axis] = s.length
                r = list(s.a) + size
            w, h = c(self.to_screen(r)).size
            if w == 0 and h == 0:
                return True

    def col_cb (self, o1, o2, dirn, i1, i2, I):
        pass

    def update (self):
        x0, y0 = self.rect.center
        x, y = pg.mouse.get_pos()
        self.window = self.window.move(x - x0, y - y0)
        pg.mouse.set_pos(x0, y0)
        self.player.update()
        self.col_handler.update()
        # check if OoB
        bl = self.rect.left
        br, bb = self.rect.bottomright
        l, t, r, b = self.to_screen(self.player.rect.rect)
        if r < bl or l > br or t > bb:
            self.die()

    def win (self):
        self.ID += 1
        if self.ID == len(conf.LEVELS):
            self.game.quit()
        else:
            self.init()

    def die (self):
        self.init()

    def to_screen (self, rect):
        return [int(round(x)) for x in rect]

    def draw (self, screen):
        screen.fill((0, 0, 0))
        screen.fill((255, 255, 255), self.window)
        rects = []
        for r in self.rects:
            col = self.to_screen(r.pgrect)
            if self.show:
                col = pg.Rect(col)
            else:
                col = self.window.clip(col)
            if col:
                screen.fill((50, 50, 50), col)
                if self.show:
                    col = self.window.clip(col)
                    if not col:
                        continue
                rects.append(col)
        # goal
        screen.fill((255, 255, 0), self.to_screen(self.goal.pgrect))
        # player
        p = self.to_screen(self.player.rect.pgrect)
        screen.fill((255, 0, 0), p)
        for r in rects:
            if r.colliderect(p):
                self.die()
        return True