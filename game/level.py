from math import cos, sin, pi
from random import randint, random, expovariate

import pygame as pg
from ext import evthandler as eh

import conf

# load move sound
snd = pg.mixer.Sound(conf.SOUND_DIR + 'move.ogg')
move_channel = c = pg.mixer.find_channel()
assert c is not None
c.set_volume(0)
c.play(snd, -1)
c.pause()
c.set_volume(conf.SOUND_VOLUME * conf.SOUND_VOLUMES.get('move', 1) * .01)

def tile (screen, img, rect, jitter = None):
    if jitter is None:
        ox = oy = 0
    else:
        if len(jitter) == 3:
            jx, jy, t0 = jitter
            t = t0
            ox, oy = randint(0, jx), randint(0, jy)
            jitter += [ox, oy, t]
        else:
            jx, jy, t0, ox, oy, t = jitter
            if t == 0:
                ox, oy = randint(0, jx), randint(0, jy)
                jitter[3] = ox
                jitter[4] = oy
                jitter[5] = t0
        jitter[5] -= 1
    i_w, i_h = img.get_size()
    i_w -= ox
    i_h -= oy
    x, y0, w, h0 = rect
    x1, y1 = x + w, y0 + h0
    while x < x1:
        w = min(w, x1 - x)
        y = y0
        h = h0
        while y < y1:
            h = min(h, y1 - y)
            screen.blit(img, (x, y), (ox, oy, w, h))
            y += i_h
        x += i_w


class Player:
    def __init__ (self, game, pos):
        self.game = game
        self.rect = list(pos) + list(conf.PLAYER_SIZE)
        self.vel = [0, 0]
        self.on_ground = 0
        self.jumping = 0
        self.jumped = False
        self.moving = False
        self.moved = False
        move_channel.pause()

    def move (self, dirn):
        if not self.moving:
            move_channel.unpause()
            self.moving = True
        self.moved = True
        speed = conf.PLAYER_SPEED if self.on_ground else conf.PLAYER_AIR_SPEED
        self.vel[0] += (1 if dirn else -1) * speed

    def jump (self, press):
        if press:
            if self.on_ground and not self.jumping:
                dv = conf.INITIAL_JUMP
                self.snd(dv = dv)
                self.vel[1] -= dv
                self.jumping = conf.JUMP_TIME
                self.on_ground = 0
        elif self.jumping:
            self.jumped = True

    def snd (self, axis = None, v = None, dv = None):
        if dv is None:
            dv = v - self.vel[axis]
        vol = abs(dv)
        if vol >= conf.HIT_VOL_THRESHOLD:
            self.game.play_snd('hit', vol)

    def update (self):
        if self.moving and not self.moved:
            self.moving = False
            move_channel.pause()
        self.moved = False
        vx, vy = self.vel
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
        self.vel = [vx, vy]
        self.rect[0] += vx
        self.rect[1] += vy
        if self.on_ground:
            self.on_ground -= 1
        if self.jumping:
            self.jumping -= 1


class Level:
    def __init__ (self, game, event_handler, ID = 0, cp = -1):
        self.game = game
        self.event_handler = event_handler
        self.frame = conf.FRAME
        # input
        event_handler.add_event_handlers({
            pg.KEYDOWN: self.skip,
            pg.MOUSEBUTTONDOWN: self.skip
        })
        event_handler.add_key_handlers([
            (ks, [(self.move, (i,))], eh.MODE_HELD)
            for i, ks in enumerate(conf.KEYS_MOVE)
        ] + [
            (conf.KEYS_JUMP, self.jump, eh.MODE_ONDOWN_REPEAT, 1, 1),
            (conf.KEYS_RESET, lambda *args: self.init(), eh.MODE_ONDOWN),
            (conf.KEYS_PAUSE, self.toggle_paused, eh.MODE_ONDOWN)
        ])
        self.paused = False
        self.was_paused = False
        self.unpaused = False
        self.centre = (conf.RES[0] / 2, conf.RES[1] / 2)
        self.ID = None
        self.init(ID, cp)
        self.load_graphics()

    def init (self, ID = None, cp = None):
        self.first = True
        if ID is None:
            ID = self.ID
        if ID != self.ID:
            self.ID = ID
            self.current_cp = cp if cp is not None else -1
        elif cp is not None:
            self.current_cp = cp
        data = conf.LEVELS[ID]
        # checkpoints
        s = conf.CHECKPOINT_SIZE
        self.checkpoints = [p + s for p in data.get('checkpoints', [])]
        # player
        if self.current_cp >= 0:
            p = list(self.checkpoints[self.current_cp][:2])
            s_p, s_c = conf.PLAYER_SIZE, conf.CHECKPOINT_SIZE
            for i in (0, 1):
                p[i] += float(s_c[i] - s_p[i]) / 2
        else:
            p = data['player_pos']
        self.player = Player(self.game, p)
        self.dying = False
        self.winning = False
        # goal
        self.goal = data['goal'] + conf.GOAL_SIZE
        # window
        x, y = pg.Rect(self.to_screen(self.player.rect)).center
        w, h = conf.HALF_WINDOW_SIZE
        self.window = pg.Rect(x - w, y - h, 2 * w, 2 * h)
        # objs
        w, h = conf.RES
        self.all_rects = data['rects']
        self.update_rects()
        self.arects = data.get('arects', [])
        # centre mouse to avoid initial window movement
        pg.mouse.set_pos(self.centre)

    def toggle_paused (self, *args):
        if self.paused:
            self.paused = False
            self.was_paused = False
            self.unpaused = True
        elif not self.dying:
            self.paused = True
            self.player.moving = False
            move_channel.pause()

    def skip (self, evt):
        if self.dying and self.dying_counter < conf.DIE_SKIP_THRESHOLD:
            self.dying = False
            self.init()

    def move (self, key, mode, mods, i):
        if not self.paused:
            self.player.move(i)

    def jump (self, key, mode, mods):
        if not self.paused:
            self.player.jump(mode == 0)

    def get_clip (self, r1, r2, err = 0):
        x01, y01, w, h = r1
        x11, y11 = x01 + w, y01 + h
        x02, y02, w, h = r2
        x12, y12 = x02 + w, y02 + h
        x0, y0 = max(x01, x02), max(y01, y02)
        x1, y1 = min(x11, x12), min(y11, y12)
        w, h = x1 - x0, y1 - y0
        if w > err and h > err:
            return (x0, y0, w, h)

    def update_rects (self):
        self.rects = rects = []
        self.draw_rects = draw = []
        w = list(self.window)
        get_clip = self.get_clip
        for r in self.all_rects:
            c = self.get_clip(r, w)
            if c:
                draw.append(r)
                rects.append(c)

    def handle_collisions (self):
        get_clip = self.get_clip
        p = self.player.rect
        p0 = list(p)
        v = self.player.vel
        for r in self.rects + self.arects:
            if get_clip(r, p):
                r_x0, r_y0, w, h = r
                r_x1, r_y1 = r_x0 + w, r_y0 + h
                p_x0, p_y0, w, h = p
                p_x1, p_y1 = p_x0 + w, p_y0 + h
                x, dirn = min((p_x1 - r_x0, 0), (p_y1 - r_y0, 1),
                              (r_x1 - p_x0, 2), (r_y1 - p_y0, 3))
                axis = dirn % 2
                p[axis] += (1 if dirn >= 2 else -1) * x
                self.player.snd(axis, 0)
                v[axis] = 0
                if axis == 1:
                    self.vert_dirn = dirn
        # screen left/right
        if p[0] < 0:
            p[0] = 0
            self.player.snd(0, 0)
            v[0] = 0
        elif p[0] + p[2] > conf.RES[0]:
            p[0] = conf.RES[0] - p[2]
            self.player.snd(0, 0)
            v[0] = 0
        # die if still colliding
        axes = set()
        e = conf.ERR
        colliding = [r for r in self.rects + self.arects if get_clip(r, p, e)]
        if colliding:
            for r in colliding:
                r_x0, r_y0, w, h = r
                r_x1, r_y1 = r_x0 + w, r_y0 + h
                p_x0, p_y0, w, h = p
                p_x1, p_y1 = p_x0 + w, p_y0 + h
                x, dirn = min((p_x1 - r_x0, 0), (p_y1 - r_y0, 1),
                              (r_x1 - p_x0, 2), (r_y1 - p_y0, 3))
                axes.add(dirn % 2)
            if len(axes) == 2:
                dirn = .5
            else:
                dirn = .95 if axes.pop() == 0 else .1
            self.die(dirn)

    def update (self):
        if self.paused and not self.first:
            return
        if self.winning:
            self.win_counter -= 1
            if self.win_counter == 0:
                self.init(self.ID + 1)
        if not self.dying:
            # move player
            self.player.update()
        # move window
        x0, y0 = self.centre
        if self.unpaused:
            dx = dy = 0
            self.unpaused = False
        else:
            x, y = pg.mouse.get_pos()
            dx, dy = x - x0, y - y0
        pg.mouse.set_pos(x0, y0)
        done = False
        self.vert_dirn = 3
        for axis, d in ((0, dx), (1, dy)):
            dirn = 1 if d > 0 else -1
            while d * dirn > 0:
                done = True
                d -= dirn
                rel = [0, 0]
                rel[axis] += dirn
                self.window = self.window.move(rel)
                self.update_rects()
                if not self.dying:
                    self.handle_collisions()
        if self.dying:
            # update particles
            k = conf.PARTICLE_DAMPING
            j = conf.PARTICLE_JITTER
            for c, p, v, size in self.death_particles:
                p[0] += v[0]
                p[1] += v[1]
                v[0] *= k
                v[1] *= k
                v[0] += j * (random() - .5)
                v[1] += j * (random() - .5)
            # counter
            self.dying_counter -= 1
            if self.dying_counter == 0:
                self.init()
            return
        if not done:
            self.handle_collisions()
        if self.vert_dirn == 1:
            self.player.on_ground = conf.ON_GROUND_TIME
        # die if OoB
        if self.player.rect[1] > conf.RES[1]:
            self.die()
        # check if at goal
        get_clip = self.get_clip
        w = self.window
        p = self.player.rect
        c = get_clip(p, self.goal)
        if c and get_clip(w, c):
            self.win()
        # check if at checkpoints
        for c in self.checkpoints[self.current_cp + 1:]:
            if get_clip(p, c) and get_clip(w, c):
                self.current_cp += 1

    def win (self):
        if self.winning:
            return
        move_channel.pause()
        if self.ID == len(conf.LEVELS) - 1:
            self.game.quit()
        else:
            self.winning = True
            self.win_counter = conf.WIN_TIME
            self.win_sfc = pg.Surface(conf.RES).convert_alpha()
            # particles
            self.win_ptcls = []
            self.add_ptcls(conf.WIN_PARTICLE_COLOURS, self.win_ptcls, list(pg.Rect(self.to_screen(self.player.rect)).center))

    def add_ptcls (self, src, dest, pos, dirn = .5):
        max_speed = conf.PARTICLE_SPEED
        max_size = int(round(conf.PARTICLE_SIZE))
        r = random
        dirn *= pi / 2
        for c, amount in src:
            while amount > 0:
                size = randint(1, max_size)
                amount -= size
                angle = random() * 2 * pi
                speed = max_speed * expovariate(5)
                v = [speed * cos(dirn) * cos(angle), speed * sin(dirn) * sin(angle)]
                dest.append((c, list(pos), v, size))

    def die (self, dirn = .5):
        self.dying = True
        self.dying_counter = conf.DIE_TIME
        # particles
        self.death_particles = []
        pos = list(pg.Rect(self.to_screen(self.player.rect)).center)
        self.add_ptcls(conf.DEATH_PARTICLE_COLOURS, self.death_particles, pos, dirn)
        # sound
        move_channel.pause()
        self.game.play_snd('die')

    def load_graphics (self):
        self.imgs = imgs = {}
        for img in ('bg', 'void', 'window', 'rect', 'arect', 'player',
                    'checkpoint-current', 'checkpoint', 'goal'):
            imgs[img] = self.game.img(img + '.png')
        img = imgs['player']
        imgs['player'] = [img, pg.transform.flip(img, True, False)]
        self.void_jitter = [5, 5, 5]
        self.window_sfc = pg.Surface(conf.WINDOW_SIZE).convert_alpha()

    def to_screen (self, rect):
        return [int(round(x)) for x in rect]

    def draw (self, screen):
        if self.paused:
            if self.was_paused and not self.first:
                return
            else:
                self.was_paused = True
        self.first = False
        imgs = self.imgs
        to_screen = self.to_screen
        # background
        tile(screen, imgs['void'], (0, 0) + screen.get_size(), self.void_jitter)
        # window
        w = self.window
        w_sfc = self.window_sfc
        w_sfc.blit(imgs['bg'], (0, 0), w)
        # contains rects
        offset = (-w[0], -w[1])
        img = imgs['rect']
        for r in self.rects:
            tile(w_sfc, img, pg.Rect(to_screen(r)).move(offset))
        # window border
        w_sfc.blit(imgs['window'], (0, 0), None, pg.BLEND_RGBA_MULT)
        # copy window area to screen
        screen.blit(w_sfc, w)
        # arects
        img = imgs['arect']
        for r in self.arects:
            tile(screen, img, to_screen(r))
        # goal
        r = pg.Rect(to_screen(self.goal)).move(conf.GOAL_OFFSET)
        screen.blit(imgs['goal'], r)
        # checkpoints
        for i, r in enumerate(self.checkpoints):
            c = w.clip(to_screen(r))
            img = imgs['checkpoint' + ('-current' if i == self.current_cp else '')]
            if c:
                screen.blit(img, c, c.move(-r[0], -r[1]))
        # player
        if self.dying:
            # particles
            for c, p, v, size in self.death_particles:
                screen.fill(c, p + [size, size])
        else:
            p = to_screen(self.player.rect)
            screen.blit(imgs['player'][0], pg.Rect(p).move(conf.PLAYER_OFFSET))
        # fadeout
        if self.winning:
            alpha = 300 * float(conf.WIN_TIME - self.win_counter) / conf.WIN_TIME
            alpha = min(255, int(round(alpha)))
            self.win_sfc.fill((0, 0, 0, alpha))
            screen.blit(self.win_sfc, (0, 0))
        return True