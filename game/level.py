import pygame as pg

from ext import evthandler as eh

import conf


class Player:
    def __init__ (self, pos):
        self.rect = list(pos) + list(conf.PLAYER_SIZE)
        self.vel = [0, 0]
        self.on_ground = 0
        self.jumping = 0
        self.jumped = False

    def move (self, dirn):
        speed = conf.PLAYER_SPEED if self.on_ground else conf.PLAYER_AIR_SPEED
        self.vel[0] += (1 if dirn else -1) * speed

    def jump (self, press):
        if press:
            if self.on_ground and not self.jumping:
                self.vel[1] -= conf.INITIAL_JUMP
                self.jumping = conf.JUMP_TIME
                self.on_ground = 0
        elif self.jumping:
            self.jumped = True

    def update (self):
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
        event_handler.add_key_handlers([
            (ks, [(self.move, (i,))], eh.MODE_HELD)
            for i, ks in enumerate(conf.KEYS_MOVE)
        ] + [
            (conf.KEYS_JUMP, self.jump, eh.MODE_ONDOWN_REPEAT, 1, 1)
        ])
        self.show = False
        self.rect = pg.Rect(0, 0, *conf.RES).inflate(-4, -4)
        self.ID = None
        self.init(ID, cp)

    def init (self, ID = None, cp = None):
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
        self.player = Player(p)
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
        pg.mouse.set_pos(self.rect.center)

    def move (self, key, mode, mods, i):
        self.player.move(i)

    def jump (self, key, mode, mods):
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
        w = list(self.window)
        get_clip = self.get_clip
        for r in self.all_rects:
            r = self.get_clip(r, w)
            if r:
                rects.append(r)

    def handle_collisions (self):
        get_clip = self.get_clip
        p = self.player.rect
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
                v[axis] = 0
                if axis == 1:
                    self.vert_dirn = dirn
        # die if still colliding
        if any(get_clip(r, p, conf.ERR) for r in self.rects + self.arects):
            self.die()

    def update (self):
        # move player
        self.player.update()
        # move window
        x0, y0 = self.rect.center
        x, y = pg.mouse.get_pos()
        dx, dy = x - x0, y - y0
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
                self.handle_collisions()
        if not done:
            self.handle_collisions()
        if self.vert_dirn == 1:
            self.player.on_ground = conf.ON_GROUND_TIME
        # centre mouse
        pg.mouse.set_pos(x0, y0)
        # check if OoB
        bl = self.rect.left
        br, bb = self.rect.bottomright
        l, t, w, h = self.player.rect
        r, b = l + w, t + h
        if r < bl or l > br or t > bb:
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
            if get_clip(p, c):
                self.current_cp += 1

    def win (self):
        if self.ID == len(conf.LEVELS) - 1:
            self.game.quit()
        else:
            self.init(self.ID + 1)

    def die (self):
        self.init()

    def to_screen (self, rect):
        return [int(round(x)) for x in rect]

    def draw (self, screen):
        screen.fill((0, 0, 0))
        screen.fill((255, 255, 255), self.window)
        for c, rects in (((50, 50, 50), self.rects),
                         ((0, 0, 100), self.arects)):
            for r in rects:
                screen.fill(c, self.to_screen(r))
        # goal
        screen.fill((255, 255, 0), self.to_screen(self.goal))
        # checkpoints
        for i, r in enumerate(self.checkpoints):
            c = (0, 150, 0) if i == self.current_cp else (100, 100, 255)
            r = self.window.clip(self.to_screen(r))
            if r:
                screen.fill(c, r)
        # player
        p = self.to_screen(self.player.rect)
        screen.fill((255, 0, 0), p)
        return True