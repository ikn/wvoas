from random import expovariate

import pygame as pg
from pygame import Rect

from conf import conf
from util import ir


class Player (object):
    def __init__ (self, level, pos):
        self.level = level
        w, h = level.game.img('player.png').get_size()
        self.img_size = (w / (conf.PLAYER_MAX_SKEW + 1), h / 2)
        self.rect = list(pos) + list(conf.PLAYER_SIZE)
        self.old_rect = list(self.rect)
        ox, oy = conf.PLAYER_OFFSET
        p = (ir(self.rect[0]) + ox, ir(self.rect[1]) + oy)
        self.old_rect_img = self.rect_img = Rect(p, self.img_size)
        self.vel = [0, 0]
        self.on_ground = 0
        self.can_jump = level.ID in conf.CAN_JUMP
        self.jumping = 0
        self.jumped = False
        self.can_move = level.ID in conf.CAN_MOVE
        self.moving = False
        self.moved = False
        if level.move_channel is not None:
            level.move_channel.pause()
        self.img = level.game.img('player.png')
        self.f_imgs = [level.game.img('player-features.png'),
                       level.game.img('player-features-blinking.png')]
        self.f_imgs = [(img, pg.transform.flip(img, True, False))
                       for img in self.f_imgs]
        self.sfc = pg.Surface(self.img_size).convert_alpha()
        self.dirn = True
        self.last_dirn = None
        self.skew_v = 0
        self.skew = 0
        self.last_skew = None
        self.squash_v = [0, 0, 0, 0]
        self.squash = [0, 0, 0, 0]
        self.last_scale = None
        self.blinking = -1
        self.last_blinking = None
        self.to_move = 0

    def impact (self, axis, v = None, dv = None):
        if dv is None:
            dv = v - self.vel[axis]
        # velocity
        self.vel[axis] += dv
        # squash
        self.squash_v[axis + (2 if dv > 0 else 0)] += abs(dv)
        # sound
        vol = abs(dv)
        if vol >= conf.HIT_VOL_THRESHOLD:
            self.level.game.play_snd('hit', vol)

    def move (self, dirn):
        self.dirn = dirn
        dirn = 1 if dirn else -1
        if self.can_move:
            vx = self.vel[0]
            if abs(vx) > 1 and (vx > 0) == (dirn > 0) and self.on_ground:
                # actually moving along the ground (not against a wall)
                if not self.moving:
                    if self.level.move_channel is not None:
                        self.level.move_channel.unpause()
                    self.moving = True
                self.moved = dirn
            self.to_move += dirn
        elif self.on_ground:
            self.skew_v += dirn

    def jump (self, press):
        if press:
            if self.on_ground and not self.jumping:
                if self.can_jump:
                    self.impact(1, dv = -conf.INITIAL_JUMP)
                    self.jumping = conf.JUMP_TIME
                    self.on_ground = 0
                    pos = Rect(self.level.to_screen(self.rect)).midbottom
                    self.level.add_ptcls('jump', pos)
                else:
                    self.squash_v[1] -= conf.INITIAL_JUMP
                    self.level.game.play_snd('hit', conf.INITIAL_JUMP)
        elif self.jumping:
            self.jumped = True

    def update (self):
        skew_v = self.skew_v
        if self.moving:
            # skew
            skew_v -= self.moved
            # particles
            pos = Rect(self.level.to_screen(self.rect)).midbottom
            self.level.add_ptcls('move', pos)
            if not self.moved:
                self.moving = False
                if self.level.move_channel is not None:
                    self.level.move_channel.pause()
        self.moved = False
        # apply movement
        v = self.to_move
        if v:
            self.vel[0] += (v / abs(v)) * (conf.PLAYER_SPEED if self.on_ground else conf.PLAYER_AIR_SPEED)
            self.to_move = 0
        # gravity
        vx, vy = self.vel
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
        # move
        self.vel = [vx, vy]
        self.rect[0] += vx
        self.rect[1] += vy
        # set if on ground
        if self.on_ground:
            self.on_ground -= 1
        if self.jumping:
            self.jumping -= 1
        # skew
        skew_v *= conf.PLAYER_SKEW_ELAST
        skew_v -= conf.PLAYER_SKEW_STIFFNESS * self.skew
        self.skew += skew_v
        self.skew_v = skew_v
        # squash
        squash_v = self.squash_v
        squash = self.squash
        e = conf.PLAYER_SQUASH_ELAST
        k = conf.PLAYER_SQUASH_STIFFNESS
        for i in xrange(4):
            squash_v[i] *= e
            squash_v[i] -= k * squash[i]
            squash[i] += squash_v[i]
        # blink (< 0 means blinking, > 0 not)
        b = self.blinking
        if b in (1, -1):
            b = -b * (2 + int(expovariate(.3 if b == 1 else .002)))
        else:
            b -= 1 if b > 0 else -1
        self.blinking = b

    def pre_draw (self):
        ox, oy = conf.PLAYER_OFFSET
        x, y = (ir(self.rect[0]) + ox, ir(self.rect[1]) + oy)
        w0, h0 = self.img_size
        # copy images to use to sfc
        sfc = self.sfc
        dirn = self.dirn
        skew = ir(self.skew)
        skew = (1 if skew > 0 else -1) * min(abs(skew), conf.PLAYER_MAX_SKEW)
        blinking = self.blinking
        if skew != self.last_skew or dirn != self.last_dirn \
           or (blinking < 0) != self.last_blinking:
            sfc.fill((0, 0, 0, 0))
            x0, y0 = w0 * abs(skew), h0 if skew > 0 else 0
            sfc.blit(self.img, (0, 0), (x0, y0, w0, h0))
            f_img = self.f_imgs[blinking < 0][dirn]
            if dirn:
                # facing right
                x0 = w0 * (conf.PLAYER_MAX_SKEW - abs(skew))
                # use opposite skew
                y0 = 0 if skew > 0 else h0
            sfc.blit(f_img, (0, 0), (x0, y0, w0, h0))
            self.last_scale = None
            self.last_skew = skew
            self.last_dirn = dirn
            self.last_blinking = blinking < 0
        # scale
        x0, y0, x1, y1 = self.squash
        w = w0 - x0 - x1
        h = h0 - y0 - y1
        # constrain scale factor
        mn, mx = conf.PLAYER_MIN_SQUASH, conf.PLAYER_MAX_SQUASH
        wb = min(max(w, mn * w0), mx * w0)
        hb = min(max(h, mn * h0), mx * h0)
        # adjust blit location if constrained
        if wb != w:
            assert x0 + x1 != 0
            x0 -= (wb - w) * x0 / (x0 + x1)
        if hb != h:
            assert y0 + y1 != 0
            y0 -= (hb - h) * y0 / (y0 + y1)
        self.rect_img = pg.Rect(x + ir(x0), y + ir(y0), ir(wb), ir(hb))
        # star sound
        c = self.level.star_channel
        if c is not None:
            x0, y0 = self.rect_img.center
            vs = []
            for s in self.level.stars:
                if not s.got:
                    x1, y1 = s.rect.center
                    v = (abs(x1 - x0) + abs(y1 - y0)) ** 1.5
                    vs.append(1. / max(conf.STAR_SND_CUTOFF, v))
            if vs:
                v = conf.VOL_MUL * conf.SOUND_VOLUME * conf.SOUND_VOLUMES.get('star', 1) * max(0, *vs)
                c.set_volume(min(v, 1))
            else:
                c.pause()

    def update_vel (self):
        o, r, v = self.old_rect, self.rect, self.vel
        d = conf.LAUNCH_SPEED
        v[0] += d * (r[0] - o[0] - v[0])
        v[1] += d * (r[1] - o[1] - v[1])

    def draw (self, screen):
        x, y, w, h = self.rect_img
        if self.last_scale == (w, h):
            sfc = self.last_sfc
        else:
            self.last_scale = (w, h)
            self.last_sfc = sfc = pg.transform.smoothscale(self.sfc, (w, h))
        screen.blit(sfc, (x, y))
        self.old_rect = list(self.rect)
        self.old_rect_img = self.rect_img


class Star (object):
    def __init__ (self, level, pos, got):
        self.rect = Rect(pos, conf.STAR_SIZE)
        self.got = got
        self.bg = level.game.img('star-bg.png')
        self.fg = level.game.img('star-fg.png')
        self.sfc = pg.Surface(self.fg.get_size()).convert_alpha()
        self.glow = 0
        self.glow_dirn = 1

    def draw (self, screen, offset):
        r = self.rect.move(offset)
        screen.blit(self.bg, r)
        sfc = self.sfc
        g = self.glow
        # draw fg with opacity level from glow
        sfc.fill((255, 255, 255, ir(g * 255)))
        sfc.blit(self.fg, (0, 0), None, pg.BLEND_RGBA_MULT)
        screen.blit(sfc, r)
        # update glow
        d = self.glow_dirn
        g += d * conf.STAR_PULSE_SPEED
        gb = min(1, max(0, g))
        if g != gb:
            d *= -1
        self.glow = gb
        self.glow_dirn = d
