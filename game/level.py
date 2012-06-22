import pygame as pg

from ext import evthandler as eh
from ext.colhandler import HalfLine, Rect, StaticObject, Object, CollisionHandler

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

    def touching_cb (self, o1, o2, dirn, i1, i2):
        assert o1 is self.obj
        if dirn == 3:
            self.on_ground = True

    def move (self, dirn):
        speed = conf.PLAYER_SPEED if self.on_ground else conf.PLAYER_AIR_SPEED
        self.obj.vel[0] += (1 if dirn else -1) * speed

    def jump (self, press):
        v = self.obj.vel
        if self.jumping and not press:
            v[1] -= conf.CONTINUE_JUMP
        elif press and self.on_ground:
            v[1] -= conf.INITIAL_JUMP
            self.jumping = conf.JUMP_TIME

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
        # update things
        self.obj.vel = [vx, vy]
        self.on_ground = False
        if self.jumping:
            self.jumping -= 1

    def draw (self, screen):
        screen.fill((255, 0, 0), self.rect.pgrect)


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
        ])
        self.init()

    def init (self):
        data = conf.LEVELS[self.ID]
        # player
        self.player = Player(data['player_pos'])
        # rects
        w, h = conf.RES
        bdy = [HalfLine(*args) for args in ((2, 0, 0, h), (3, 0, 0, w),
                                            (0, w, 0, h), (1, h, 0, w))]
        self.rects = [Rect(*args) for args in data['rects']]
        self.objs = [StaticObject(s, conf.OBJ_ELAST) for s in self.rects + bdy]
        # colhandler
        self.col_handler = CollisionHandler([self.player.obj] + self.objs,
            before_cb = self.filter_col, touching_cb = self.player.touching_cb)

    def move (self, key, mode, mods, i):
        self.player.move(i)

    def jump (self, key, mode, mods):
        self.player.jump(mode == 0)

    def filter_col (self, o1, o2, dirn, i1, i2, data):
        pass

    def update (self):
        self.player.update()
        self.col_handler.update()

    def draw (self, screen):
        screen.fill((255, 255, 255))
        for r in self.rects:
            screen.fill((50, 50, 50), r.pgrect)
        self.player.draw(screen)
        return True