from math import cos, sin, pi, ceil
from random import randint, random, expovariate, shuffle

import pygame as pg
from pygame import Rect
from ext import evthandler as eh

import conf

def random0 ():
    return 2 * random() - 1

# load move sound
snd = pg.mixer.Sound(conf.SOUND_DIR + 'move.ogg')
move_channel = c = pg.mixer.find_channel()
assert c is not None
c.set_volume(0)
c.play(snd, -1)
c.pause()
c.set_volume(conf.SOUND_VOLUME * conf.SOUND_VOLUMES.get('move', 1) * .01)

def tile (screen, img, rect, ox = 0, oy = 0, full = None):
    # get offset
    if full is not None:
        ox += rect[0] - full[0]
        oy += rect[1] - full[1]
    # draw
    i_w, i_h = img.get_size()
    ox %= i_w
    oy %= i_h
    x0, y0, w0, h0 = rect
    x1, y1 = x0 + w0, y0 + h0
    x = x0
    while x < x1:
        this_ox = ox if x == x0 else 0
        w = min(i_w - this_ox, x1 - x)
        y = y0
        while y < y1:
            this_oy = oy if y == y0 else 0
            h = min(i_h - this_oy, y1 - y)
            screen.blit(img, (x, y), (this_ox, this_oy, w, h))
            y += h
        x += w


class Player:
    def __init__ (self, level, pos):
        self.level = level
        w, h = level.game.img('player.png').get_size()
        self.img_size = (w / (conf.PLAYER_MAX_SKEW + 1), h / 2)
        self.rect = list(pos) + list(conf.PLAYER_SIZE)
        self.update_img_rect()
        self.post_draw_update()
        self.vel = [0, 0]
        self.on_ground = 0
        self.jumping = 0
        self.jumped = False
        self.moving = False
        self.moved = False
        move_channel.pause()
        self.img = level.game.img('player.png')
        self.skew_v = 0
        self.skew = 0

    def move (self, dirn):
        if not self.moving:
            move_channel.unpause()
            self.moving = True
        dirn = 1 if dirn else -1
        self.moved = dirn
        speed = conf.PLAYER_SPEED if self.on_ground else conf.PLAYER_AIR_SPEED
        self.vel[0] += dirn * speed

    def jump (self, press):
        if press:
            if self.on_ground and not self.jumping:
                dv = conf.INITIAL_JUMP
                self.snd(dv = dv)
                self.vel[1] -= dv
                self.jumping = conf.JUMP_TIME
                self.on_ground = 0
                pos = Rect(self.level.to_screen(self.rect)).midbottom
                self.level.add_ptcls('jump', pos)
        elif self.jumping:
            self.jumped = True

    def snd (self, axis = None, v = None, dv = None):
        if dv is None:
            dv = v - self.vel[axis]
        vol = abs(dv)
        if vol >= conf.HIT_VOL_THRESHOLD:
            self.level.game.play_snd('hit', vol)

    def update (self):
        skew_v = self.skew_v
        vx, vy = self.vel
        if self.moving:
            if self.moved:
                # if actually moving (not against a wall),
                if self.on_ground and abs(vx) > 1 and (vx > 0) == (self.moved > 0):
                    # skew
                    skew_v -= self.moved
                    # particles
                    pos = Rect(self.level.to_screen(self.rect)).midbottom
                    self.level.add_ptcls('move', pos)
            else:
                self.moving = False
                move_channel.pause()
        self.moved = False
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
        # move
        self.vel = [vx, vy]
        self.rect[0] += vx
        self.rect[1] += vy
        self.update_img_rect()
        # set if on ground
        if self.on_ground:
            self.on_ground -= 1
        if self.jumping:
            self.jumping -= 1
        # elasticity
        skew_v *= conf.PLAYER_ELAST
        skew_v -= conf.PLAYER_STIFFNESS * self.skew
        self.skew += skew_v
        self.skew_v = skew_v

    def update_img_rect (self):
        ox, oy = conf.PLAYER_OFFSET
        p = (int(round(self.rect[0])) + ox, int(round(self.rect[1])) + oy)
        self.rect_img = Rect(p, self.img_size)

    def update_vel (self):
        o, r, v = self.old_rect, self.rect, self.vel
        d = conf.LAUNCH_SPEED
        v[0] += d * (r[0] - o[0] - v[0])
        v[1] += d * (r[1] - o[1] - v[1])

    def post_draw_update (self):
        self.old_rect = list(self.rect)
        self.old_rect_img = self.rect_img.copy()

    def draw (self, screen):
        #print self.skew_v, self.skew
        skew = int(round(self.skew))
        skew = (1 if skew > 0 else -1) * min(abs(skew), conf.PLAYER_MAX_SKEW)
        x, y, w, h = self.rect_img
        screen.blit(self.img, (x, y), (w * abs(skew), h if skew > 0 else 0, w, h))
        self.post_draw_update()

class Paused:
    def __init__ (self, game, event_handler):
        self.game = game
        self.event_handler = event_handler
        self.frame = conf.FRAME
        self.fading = True
        self.fade_counter = conf.PAUSE_FADE_TIME
        self.fade_sfc = pg.Surface(conf.RES).convert_alpha()
        self.sfc = pg.display.get_surface().copy()
        self.text = game.img('paused.png')
        event_handler.add_key_handlers([
            (conf.KEYS_BACK + conf.KEYS_NEXT, self.unpause, eh.MODE_ONDOWN)
        ])
        pg.mixer.music.set_volume(conf.PAUSED_MUSIC_VOLUME * .01)
        pg.mouse.set_visible(True)

    def unpause (self, *args):
        pg.mixer.music.set_volume(conf.MUSIC_VOLUME * .01)
        pg.mouse.set_visible(conf.MOUSE_VISIBLE)
        self.game.quit_backend()

    def update (self):
        pass

    def draw (self, screen):
        if self.fading:
            # draw
            t = conf.PAUSE_FADE_TIME - self.fade_counter
            alpha = conf.PAUSE_FADE_RATE * float(t) / conf.PAUSE_FADE_TIME
            alpha = min(255, int(round(alpha)))
            self.fade_sfc.fill((0, 0, 0, alpha))
            screen.blit(self.sfc, (0, 0))
            screen.blit(self.fade_sfc, (0, 0))
            screen.blit(self.text, (0, 0))
            # update counter
            self.fade_counter -= 1
            if self.fade_counter == 0:
                self.fading = False
                del self.fade_sfc
            return True
        else:
            return False


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
            (conf.KEYS_BACK, self.pause, eh.MODE_ONDOWN),
            (conf.KEYS_RESET, self.reset, eh.MODE_ONDOWN),
            (conf.KEYS_JUMP, self.jump, eh.MODE_ONDOWN_REPEAT, 1, 1)
        ] + [
            (ks, [(self.move, (i,))], eh.MODE_HELD)
            for i, ks in enumerate(conf.KEYS_MOVE)
        ])
        self.centre = (conf.RES[0] / 2, conf.RES[1] / 2)
        self.clouds = []
        self.load_graphics()
        # load first level
        self.ID = None
        self.init(ID, cp)

    def init (self, ID = None, cp = None):
        self.first = True
        self.paused = False
        self.dying = False
        self.first_dying = False
        self.winning = False
        self.fading = False
        self.particles = []
        self.particle_rects = []
        self.void_jitter = [conf.VOID_JITTER_X, conf.VOID_JITTER_Y, conf.VOID_JITTER_T]
        # get level/current checkpoint
        if ID is None:
            # same level
            ID = self.ID
        if ID != self.ID:
            # new level
            self.ID = ID
            self.current_cp = cp if cp is not None else -1
            # clouds: randomise initial positions and velocities
            self.clouds = cs = []
            w, h = conf.RES
            imgs = self.imgs
            vx0 = conf.CLOUD_SPEED
            vy0 = vx0 * conf.CLOUD_VERT_SPEED_RATIO
            self.cloud_vel = [vx0 * random0(), vy0 * random0()]
            vx = conf.CLOUD_MOD_SPEED_RATIO
            vy = vx * conf.CLOUD_VERT_SPEED_RATIO
            for c in conf.CLOUDS:
                c_w, c_h = imgs[c].get_size()
                s = (c_w, c_h)
                c_w /= 2
                c_h /= 2
                pos = [randint(-c_w, w - c_w), randint(-c_h, h - c_h)]
                vel = [vx * random0(), vy * random0()]
                cs.append((pos, vel, s))
        elif cp is not None:
            self.current_cp = cp
        data = conf.LEVELS[ID]
        # background
        self.bgs = data.get('bgs', conf.DEFAULT_BGS)
        # player
        if self.current_cp >= 0:
            p = list(data['checkpoints'][self.current_cp][:2])
            s_p, s_c = conf.PLAYER_SIZE, conf.CHECKPOINT_SIZE
            for i in (0, 1):
                p[i] += float(s_c[i] - s_p[i]) / 2
        else:
            p = data['player_pos']
        self.player = Player(self, p)
        # window
        x, y = Rect(self.to_screen(self.player.rect)).center
        w, h = conf.HALF_WINDOW_SIZE
        self.window = Rect(x - w, y - h, 2 * w, 2 * h)
        self.old_window = self.window.copy()
        # centre mouse to avoid initial window movement
        pg.mouse.set_pos(self.centre)
        # checkpoints
        s = conf.CHECKPOINT_SIZE
        self.checkpoints = [Rect(p + s) for p in data.get('checkpoints', [])]
        # goal
        self.goal = Rect(data['goal'] + conf.GOAL_SIZE)
        self.goal_img = self.goal.move(conf.GOAL_OFFSET)
        self.goal_img.size = self.imgs['goal'].get_size()
        # rects
        self.all_rects = [Rect(r) for r in data['rects']]
        self.all_vrects = [Rect(r) for r in data.get('vrects', [])]
        self.arects = [Rect(r) for r in data.get('arects', [])]
        self.update_rects()

    def skip (self, evt):
        if self.dying and self.dying_counter < conf.DIE_SKIP_THRESHOLD and \
           not (evt.type == pg.KEYDOWN and evt.key in conf.KEYS_BACK) and \
           not self.winning:
            self.init()

    def pause (self, *args):
        move_channel.pause()
        self.game.start_backend(Paused)
        self.paused = True

    def reset (self, *args):
        if not self.winning:
            self.init()

    def jump (self, key, mode, mods):
        if self.ID in conf.CAN_JUMP:
            self.player.jump(mode == 0)

    def move (self, key, mode, mods, i):
        if self.ID in conf.CAN_MOVE:
            self.player.move(i)

    def update_window (self):
        w = self.window
        wp0 = w.topleft
        wp1 = w.bottomright
        s = conf.RES
        self.inverse_win = rs = []
        for px in (0, 1, 2):
            for py in (0, 1, 2):
                if px == py == 1:
                    continue
                r = [0, 0, 0, 0]
                for i, p in enumerate((px, py)):
                    if p == 0:
                        r[i + 2] = wp0[i]
                    if p == 1:
                        r[i] = wp0[i]
                        r[i + 2] = wp1[i] - wp0[i]
                    elif p == 2:
                        r[i] = wp1[i]
                        r[i + 2] = s[i] - wp1[i]
                if r[2] > 0 and r[3] > 0:
                    rs.append(Rect(r))

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
        self.update_window()
        # rects
        self.rects = rects = []
        self.draw_rects = draw = []
        w = self.window
        for r in self.all_rects:
            c = w.clip(r)
            if c:
                rects.append(c)
                draw.append(r)
        # vrects
        self.vrects = rects = []
        ws = self.inverse_win
        for r in self.all_vrects:
            for w in ws:
                c = w.clip(r)
                if c:
                    rects.append(c)

    def handle_collisions (self):
        get_clip = self.get_clip
        p = self.player.rect
        p0 = list(p)
        v = self.player.vel
        for r in self.rects + self.vrects + self.arects:
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
        colliding = [r for r in self.rects + self.vrects + self.arects \
                     if get_clip(r, p, e)]
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

    def die (self, dirn = .5):
        self.first_dying = True
        self.dying = True
        self.dying_counter = conf.DIE_TIME
        # particles
        pos = list(Rect(self.to_screen(self.player.rect)).center)
        self.add_ptcls('die', pos, dirn)
        # sound
        move_channel.pause()
        self.game.play_snd('die')

    def next_level (self):
        if self.ID == len(conf.LEVELS) - 1:
            self.game.quit_backend()
        else:
            self.init(self.ID + 1)

    def win (self):
        if self.winning:
            return
        move_channel.pause()
        self.winning = True
        self.start_fading(self.next_level)

    def update (self):
        # fade counter
        if self.fading:
            self.fade_counter -= 1
            if self.fade_counter == 0:
                self.fading = False
                del self.fade_sfc
                self.fade_cb()
        # move player
        if not self.dying:
            pl = self.player
            pl.update()
        # get amount to move window by
        w = self.window
        self.old_window = w.copy()
        x0, y0 = self.centre
        if self.paused:
            dx = dy = 0
            self.paused = False
        else:
            x, y = pg.mouse.get_pos()
            dx, dy = x - x0, y - y0
        pg.mouse.set_pos(x0, y0)
        wx0, wy0, ww, wh = self.total_window = w.union(w.move(dx, dy))
        # move window
        if self.dying:
            # just move window
            w.move_ip(dx, dy)
            self.update_rects()
        else:
            self.vert_dirn = 3
            if dx == dy == 0:
                # just handle collisions
                self.handle_collisions()
            else:
                # check if player and window intersect
                wx1, wy1 = wx0 + ww, wy0 + wh
                r = pl.rect
                o_r = pl.old_rect
                px0, py0 = min(r[0], o_r[0]), min(r[1], o_r[1])
                px1 = max(r[0] + r[2], o_r[0] + o_r[2])
                py1 = max(r[1] + r[3], o_r[1] + o_r[3])
                if px1 > wx0 and py1 > wy0 and px0 < wx1 and py0 < wy1:
                    # if so, move window a few pixels at a time
                    c = conf.WINDOW_MOVE_AMOUNT
                    for axis, d in ((0, dx), (1, dy)):
                        dirn = 1 if d > 0 else -1
                        while d * dirn > 0:
                            d -= dirn * c
                            rel = [0, 0]
                            rel[axis] += c * dirn + (0 if d * dirn > 0 else d)
                            w.move_ip(rel)
                            self.update_rects()
                            if not self.dying:
                                self.handle_collisions()
                else:
                    # else move it the whole way
                    w.move_ip(dx, dy)
                    self.update_rects()
                    self.handle_collisions()
            if self.vert_dirn == 1:
                pl.on_ground = conf.ON_GROUND_TIME
        # clouds
        if self.clouds:
            # jitter
            jx = conf.CLOUD_JITTER
            jy = jx * conf.CLOUD_VERT_SPEED_RATIO
            v0 = self.cloud_vel
            v0[0] += jx * random0()
            v0[1] += jy * random0()
            r = conf.RES
            for p, v, s in self.clouds:
                for i, (i_w, r_w) in enumerate(zip(s, r)):
                    # move
                    x = p[i]
                    x += v0[i] + v[i]
                    # wrap
                    if x + i_w < 0:
                        x = r_w
                    elif x > r_w:
                        x = -i_w
                    p[i] = x
        # particles
        ptcls = []
        rects = []
        for k, j, group in self.particles:
            g = []
            x0, y0 = conf.RES
            x1 = y1 = 0
            for c, p, v, size, t in group:
                x, y = p
                # update boundary
                if x < x0:
                    x0 = x
                if y < y0:
                    y0 = y
                if x + size > x1:
                    x1 = x + size
                if y + size > y1:
                    y1 = y + size
                t -= 1
                if t != 0:
                    # move
                    vx, vy = v
                    x += vx
                    y += vy
                    # update boundary
                    if x < x0:
                        x0 = x
                    if y < y0:
                        y0 = y
                    if x + size > x1:
                        x1 = x + size
                    if y + size > y1:
                        y1 = y + size
                    # damp/jitter
                    vx *= k
                    vy *= k
                    vx += j * random0()
                    vy += j * random0()
                    g.append((c, (x, y), (vx, vy), size, t))
            if g:
                ptcls.append((k, j, g))
            if x1 > x0 and y1 > y0:
                rects.append((int(x0), int(y0), ceil(x1 - x0), ceil(y1 - y0)))
        self.particles = ptcls
        self.particle_rects = rects
        # death counter
        if self.dying:
            self.dying_counter -= 1
            if self.dying_counter == 0:
                self.init()
            return
        # player velocity
        pl.update_vel()
        # die if OoB
        if pl.rect[1] > conf.RES[1]:
            self.die()
        # win if at goal
        p = pl.rect
        c = w.clip(self.goal)
        if c and self.get_clip(p, c):
            self.win()
        # check if at checkpoints
        for c in self.checkpoints[self.current_cp + 1:]:
            if w.clip(c) and self.get_clip(p, c):
                self.current_cp += 1

    def load_graphics (self):
        self.imgs = imgs = {}
        for img in ('void', 'window', 'rect', 'vrect', 'arect',
                    'checkpoint-current', 'checkpoint', 'goal') + \
                   conf.BGS + conf.CLOUDS:
            imgs[img] = self.game.img(img + '.png')
        self.window_sfc = pg.Surface(conf.WINDOW_SIZE).convert_alpha()

    def to_screen (self, rect):
        return [int(round(x)) for x in rect]

    def add_ptcls (self, key, pos, dirn = .5):
        particles = []
        data = conf.PARTICLES[key]
        max_speed = data['speed']
        max_size = data['size']
        k = data['damping']
        j = data['jitter']
        max_life = data['life']
        dirn *= pi / 2
        for c, amount in data['colours']:
            a, b = divmod(amount, 1)
            amount = int(a) + (1 if random() < b else 0)
            while amount > 0:
                size = randint(1, max_size)
                amount -= size
                angle = random() * 2 * pi
                speed = max_speed * expovariate(5)
                v = (speed * cos(dirn) * cos(angle), speed * sin(dirn) * sin(angle))
                life = int(random() * max_life)
                if life > 0:
                    particles.append((c, tuple(pos), v, size, life))
        self.particles.append((k, j, particles))

    def start_fading (self, cb):
        if not self.fading:
            self.fading = True
            self.fade_counter = conf.FADE_TIME
            self.fade_sfc = pg.Surface(conf.RES).convert_alpha()
            self.fade_cb = cb

    def update_jitter (self, jitter):
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

    def draw (self, screen):
        # HACK: don't draw on last frame
        if self.winning and not self.fading and self.ID == len(conf.LEVELS) - 1:
            return False
        self.first = False
        imgs = self.imgs
        w = self.window
        pl = self.player
        # background
        jitter = self.void_jitter
        self.update_jitter(jitter)
        ox, oy = jitter[3], jitter[4]
        img = imgs['void']
        draw_all = jitter[5] == conf.VOID_JITTER_T - 1 or self.fading
        if draw_all:
            tile(screen, img, (0, 0) + screen.get_size(), ox, oy)
        else:
            draw_rects = self.particle_rects + [self.total_window, self.goal_img]
            if self.first_dying or not self.dying:
                draw_rects.append(pl.rect_img.union(pl.old_rect_img))
            for r in draw_rects:
                tile(screen, img, r, ox, oy, (0, 0))
        # vrects
        img = imgs['vrect']
        for r in self.all_vrects:
            tile(screen, img, r)
        # window
        offset = (-w[0], -w[1])
        w_sfc = self.window_sfc
        # window background: static images
        for img in self.bgs:
            if isinstance(img, str):
                pos = (0, 0)
            else:
                img, pos = img
            w_sfc.blit(imgs[img], Rect(pos + (0, 0)).move(offset))
        # clouds
        for c, (p, v, s) in zip(conf.CLOUDS, self.clouds):
            w_sfc.blit(imgs[c], Rect(self.to_screen(p + [0, 0])).move(offset))
        # rects in window
        img = imgs['rect']
        for r, r_full in zip(self.rects, self.draw_rects):
            tile(w_sfc, img, r.move(offset), full = r_full.move(offset))
        # checkpoints
        for i, r in enumerate(self.checkpoints):
            img = imgs['checkpoint' + ('-current' if i == self.current_cp else '')]
            w_sfc.blit(img, r.move(offset))
        # window border
        w_sfc.blit(imgs['window'], (0, 0), None, pg.BLEND_RGBA_MULT)
        # copy window area to screen
        screen.blit(w_sfc, w)
        # arects
        img = imgs['arect']
        for r in self.arects:
            tile(screen, img, r)
        # goal
        screen.blit(imgs['goal'], self.goal_img)
        # player
        if not self.dying:
            pl.draw(screen)
        # particles
        for k, j, g in self.particles:
            for c, p, v, size, t in g:
                screen.fill(c, p + (size, size))
        # fadeout
        if self.fading:
            t = conf.FADE_TIME - self.fade_counter
            alpha = conf.FADE_RATE * float(t) / conf.FADE_TIME
            alpha = min(255, int(round(alpha)))
            self.fade_sfc.fill((0, 0, 0, alpha))
            screen.blit(self.fade_sfc, (0, 0))
            draw_all = True
        if self.first_dying:
            self.first_dying = False
        if draw_all:
            return True
        else:
            return draw_rects + self.arects