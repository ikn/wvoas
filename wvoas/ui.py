import pygame as pg
from ext import evthandler as eh

import level
import conf

ir = lambda x: int(round(x))

def split (size, intervals):
    """Split a region into integer-sized intervals.

split(size, intervals) -> size_list

size: the size of the region to split.
intervals: the number of intervals to use.

size_list: a list of sizes for each interval in turn.

"""
    intervals = max(intervals, 0)
    if intervals == 0:
        return []
    if intervals == 1:
        return [size]
    avg = float(size) / intervals
    base = int(avg)
    diff = avg - base
    sizes = []
    current_diff = 0
    for i in xrange(intervals):
        # add up excess bits
        current_diff += diff
        # when we have 1, add it on
        if current_diff >= 1:
            sizes.append(base + 1)
            current_diff -= 1
        else:
            sizes.append(base)
    # adjust first interval (probably only by 1, if any)
    sizes[0] += size - sum(sizes)
    return sizes

def draw_rect (surface, colour, rect, width = 1):
    """Draw a rect border to a surface.

draw_rect(surface, colour, rect, width = 1)

surface: the surface to draw to.
colour: a standard (r, g, b) tuple.
rect: rect to draw; anything like (left, top, width, height).
width: (vertical, horizontal) rect border widths, or one int for
       vertical = horizontal, in pixels.

The border is drawn inside the given rect, unlike pygame.draw.rect, which draws
the lines with their centres on the rect's borders.

"""
    try:
        width[0]
    except TypeError:
        width = (width, width)
    l, t, w, h = rect
    x0 = l + width[0] / 2 + width[0] % 2 - 1
    x1 = l + w - width[0] / 2 - 1
    y0 = t + width[1] / 2 + width[1] % 2 - 1
    y1 = t + h - width[1] / 2 - 1
    points = (
        ((l, y0), (l + w - 1, y0)),
        ((x1, t), (x1, t + h - 1)),
        ((l + w - 1, y1), (l, y1)),
        ((x0, t + h - 1), (x0, t))
    )
    draw_line = pg.draw.line
    for i in xrange(len(points)):
        p, q = points[i]
        draw_line(surface, colour, p, q, width[not i % 2])


class LevelSelect:
    def __init__ (self, game, event_handler):
        self.game = game
        self.event_handler = event_handler
        self.frame = conf.FRAME
        # input
        event_handler.add_event_handlers({pg.MOUSEMOTION: self.set_current})
        # generate level thumbnails
        ids = conf.EXISTS
        n = len(ids)
        cols = min(i for i in xrange(n + 1) if i * i >= n)
        rows = n / cols + bool(n % cols)
        self.levels = levels = []
        w, h = conf.RES
        ws = split(w, cols)
        hs = split(ir(h * float(rows) / cols), rows)
        x = w_i = h_i = 0
        y = (h - sum(hs)) / 2
        draw_sfc = pg.Surface(conf.RES)
        for i in ids:
            rect = pg.Rect((x, y, ws[w_i], hs[h_i])).inflate(-2, -2)
            # generate image
            sfc = pg.Surface(rect[2:])
            l = level.Level(game, None, i)
            l.draw(draw_sfc)
            sfc = pg.transform.smoothscale(draw_sfc, rect[2:])
            # dim or brighten surface
            c = (0, 0, 0, 100) if i in list(range(7)) + [12, 13, 19, 16] else (255, 255, 255, 30)
            mod_sfc = pg.Surface(rect[2:]).convert_alpha()
            mod_sfc.fill(c)
            sfc.blit(mod_sfc, (0, 0))
            levels.append((i, rect, sfc.convert()))
            # get next rect
            x += ws[w_i]
            w_i += 1
            if w_i == cols:
                x = w_i = 0
                y += hs[h_i]
                h_i += 1
        self.current = None
        self.set_current(force = True)

    def set_current (self, evt = None, force = False):
        if evt is None:
            pos = pg.mouse.get_pos()
        else:
            pos = evt.pos
        current = 0 if force else None
        for i, r, s in self.levels:
            if r.inflate(2, 2).collidepoint(pos):
                current = i
        if current not in (None, self.current):
            self.current = current
            self.dirty = True

    def update (self):
        pass

    def draw (self, screen):
        if self.dirty:
            current = self.current
            screen.fill((20, 10, 5))
            for i, rect, sfc in self.levels:
                screen.blit(sfc, rect)
                if i == current:
                    draw_rect(screen, (190, 190, 80), rect.inflate(2, 2), 2)
            self.dirty = False
            return True
        else:
            return False


class Paused:
    def __init__ (self, game, event_handler):
        self.game = game
        self.event_handler = event_handler
        self.frame = conf.FRAME
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
        if self.dirty:
            # draw
            t = conf.PAUSE_FADE_TIME - self.fade_counter
            alpha = conf.PAUSE_FADE_RATE * float(t) / conf.PAUSE_FADE_TIME
            alpha = min(255, ir(alpha))
            self.fade_sfc.fill((0, 0, 0, alpha))
            screen.blit(self.sfc, (0, 0))
            screen.blit(self.fade_sfc, (0, 0))
            screen.blit(self.text, (0, 0))
            # update counter
            self.fade_counter -= 1
            if self.fade_counter <= 0:
                self.dirty = False
                del self.fade_sfc
            return True
        else:
            return False