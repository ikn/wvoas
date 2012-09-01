from sys import argv
import os
from time import time
from random import choice
from bisect import bisect
from optparse import OptionParser

d = os.path.dirname(argv[0])
if d: # else current dir
    os.chdir(d)

import pygame as pg
from pygame.time import wait
if os.name == 'nt':
    # for Windows freeze support
    import pygame._view

pg.mixer.pre_init(buffer = 1024)
pg.init()

from game.ui import LevelSelect
from game.level import Level
from game.conf import conf
from game.util import ir, convert_sfc
from game.ext.sched import Scheduler
from game.ext import evthandler as eh
if conf.USE_FONTS:
    from game.ext.fonthandler import Fonts


def get_backend_id (backend):
    """Return the computed identifier of the given backend (or backend type).

See Game.create_backend for details.

"""
    if hasattr(backend, 'id'):
        return backend.id
    else:
        if not isinstance(backend, type):
            backend = type(backend)
        return backend.__name__.lower()


class Game (object):
    """Handles backends.

Takes the same arguments as the create_backend method and passes them to it.

    METHODS

create_backend
start_backend
get_backends
quit_backend
img
render_text
play_snd
find_music
play_music
run
quit
restart
set_overlay
fade
cancel_fade
colour_fade
linear_fade
refresh_display
toggle_fullscreen
minimise

    ATTRIBUTES

scheduler: sched.Scheduler instance for scheduling events.
backend: the current running backend.
backends: a list of previous (nested) backends, most 'recent' last.  Each is
          actually a dict with keys the same as the attributes of Game when the
          backend is active.  (For example, the 'backend' key gives the backend
          object itself.)
overlay: the current overlay (see Game.set_overlay).
fading: whether a fade is in progress (see Game.fade)
files: loaded image cache (before resize).
imgs: image cache.
text: cache for rendered text.
fonts: a fonthandler.Fonts instance, or None if conf.USE_FONTS is False.
music: filenames for known music.

"""
    # attributes to store with backends, and their initial values
    _backend_attrs = {
        'backend': None,
        'overlay': False,
        'fading': False,
        '_fade_data': None
    }

    def __init__ (self, *args, **kwargs):
        self.scheduler = Scheduler()
        self.scheduler.add_timeout(self._update, frames = 1, repeat_frames = 1)
        # initialise caches
        self.files = {}
        self.imgs = {}
        self.text = {}
        # load display settings
        self.refresh_display()
        self.fonts = Fonts(conf.FONT_DIR) if conf.USE_FONTS else None
        # load move sound
        snd = pg.mixer.Sound(conf.SOUND_DIR + 'move.ogg')
        self.move_channel = c = pg.mixer.find_channel()
        assert c is not None
        c.set_volume(0)
        c.play(snd, -1)
        c.pause()
        c.set_volume(conf.VOL_MUL * conf.SOUND_VOLUME * conf.SOUND_VOLUMES.get('move', 1))
        snd = pg.mixer.Sound(conf.SOUND_DIR + 'star.ogg')
        self.star_channel = c = pg.mixer.find_channel()
        assert c is not None
        c.set_volume(0)
        c.play(snd, -1)
        c.pause()
        # start first backend
        self.backends = []
        self._last_overlay = False
        self.start_backend(*args, **kwargs)
        # start playing music
        pg.mixer.music.set_endevent(conf.EVENT_ENDMUSIC)
        self.find_music()
        self.play_music()

    def _init_backend (self):
        """Set some default attributes for a new backend."""
        for attr, val in self._backend_attrs.iteritems():
            setattr(self, attr, val)

    def _store_backend (self):
        """Store the current backend in the backends list."""
        if hasattr(self, 'backend') and self.backend is not None:
            data = dict((attr, getattr(self, attr)) \
                        for attr, val in self._backend_attrs.iteritems())
            self.backends.append(data)

    def _restore_backend (self, data):
        """Restore a backend from the given data."""
        self.__dict__.update(data)
        self._select_backend(self.backend)

    def _select_backend (self, backend, overlay = False):
        """Set the given backend as the current backend."""
        self._update_again = True
        self.backend = backend
        backend.dirty = True
        i = get_backend_id(backend)
        # set some per-backend things
        self.scheduler.timer.fps = conf.FPS[i]
        if conf.USE_FONTS:
            fonts = self.fonts
            for k, v in conf.REQUIRED_FONTS[i].iteritems():
                fonts[k] = v
        pg.mouse.set_visible(conf.MOUSE_VISIBLE[i])
        pg.mixer.music.set_volume(conf.VOL_MUL * conf.MUSIC_VOLUME[i])

    def create_backend (self, cls, *args, **kwargs):
        """Create a backend.

create_backend(cls, *args, **kwargs) -> backend

cls: the backend class to instantiate.
args, kwargs: positional- and keyword arguments to pass to the constructor.

backend: the created backend.

Backends handle pretty much everything, including drawing, and must have update
and draw methods, as follows:

update(): handle input and make any necessary calculations.
draw(screen) -> drawn: draw anything necessary to screen; drawn is True if the
                       whole display needs to be updated, something falsy if
                       nothing needs to be updated, else a list of rects to
                       update the display in.  This should not change the state
                       of the backend, because it is not guaranteed to be
                       called every frame.

A pause method may optionally be defined, which takes no arguments and is
called when the window loses focus to pause the game.

A backend is also given a dirty attribute, which indicates whether its draw
method should redraw everything (it should set it to False when it does so).
It may define an id attribute, which is a unique identifier used for some
settings in conf; if none is set, type(backend).__name__.lower() will be used
(for this to make sense, the backend must be a new-style class).

A backend is constructed via:

    cls(game, event_handler, *args, **kwargs)

game is this Game instance; event_handler is the EventHandler instance the
backend should use for input, and is stored in its event_handler attribute.

"""
        # create event handler for this backend
        v = conf.VOL_CHANGE_AMOUNT
        r = (eh.MODE_ONDOWN_REPEAT, conf.VOL_REPEAT_DELAY,
             conf.VOL_REPEAT_RATE)
        h = eh.MODE_HELD
        event_handler = eh.EventHandler({
            pg.ACTIVEEVENT: self._active_cb,
            pg.VIDEORESIZE: self._resize_cb,
            conf.EVENT_ENDMUSIC: self.play_music
        }, [
            (conf.KEYS_FULLSCREEN, self.toggle_fullscreen, eh.MODE_ONDOWN),
            (conf.KEYS_MINIMISE, self.minimise, eh.MODE_ONDOWN),
            (conf.KEYS_VOL_UP, [(self._ch_vol, (v,))]) + r,
            (conf.KEYS_VOL_DOWN, [(self._ch_vol, (-v,))]) + r
        ], False, self.quit)
        # instantiate class
        backend = cls(self, event_handler, *args)
        backend.event_handler = event_handler
        return backend

    def _ch_vol (self, key, mode, mods, amount):
        i = get_backend_id(self.backend)
        v = max(0, min(1, conf.VOL_MUL + amount))
        conf.VOL_MUL = v
        pg.mixer.music.set_volume(v * conf.MUSIC_VOLUME[i])

    def start_backend (self, *args, **kwargs):
        """Start a new backend.

Takes the same arguments as create_backend; see that method for details.

Returns the started backend.

"""
        self._store_backend()
        return self.switch_backend(*args, **kwargs)

    def switch_backend (self, *args, **kwargs):
        """Close the current backend and start a new one.

Takes the same arguments as create_backend and returns the created backend.

"""
        self._init_backend()
        backend = self.create_backend(*args, **kwargs)
        self._select_backend(backend)
        return backend

    def get_backends (self, ident, current = True):
        """Get a list of running backends, filtered by ID.

get_backends(ident, current = True) -> backends

ident: the backend identifier to look for (see create_backend for details).
current: include the current backend in the search.

backends: the backend list, in order of time started, most recent last.

"""
        backends = []
        current = [{'backend': self.backend}] if current else []
        for data in self.backends + current:
            backend = data['backend']
            if get_backend_id(backend) == ident:
                backends.append(backend)

    def quit_backend (self, depth = 1):
        """Quit the currently running backend.

quit_backend(depth = 1)

depth: quit this many (nested) backends.

If the running backend is the last (root) one, exit the game.

"""
        if depth < 1:
            return
        if self.backends:
            self._restore_backend(self.backends.pop())
        else:
            self.quit()
        self.quit_backend(depth - 1)

    def img (self, filename, size = None, cache = True):
        """Load or scale an image, or retrieve it from cache.

img(filename[, size], cache = True) -> surface

data: a filename to load.
size: scale the image.  Can be an (x, y) size, a rect (in which case its
      dimension is used), or a number to scale by.  If (x, y), either x or y
      can be None to scale to the other with aspect ratio preserved.
cache: whether to store this image in the cache if not already stored.

"""
        # get standardised cache key
        if size is not None:
            if isinstance(size, (int, float)):
                size = float(size)
            else:
                if len(size) == 4:
                    # rect
                    size = size[2:]
                size = tuple(size)
        key = (filename, size)
        if key in self.imgs:
            return self.imgs[key]
        # else new: load/render
        filename = conf.IMG_DIR + filename
        # also cache loaded images to reduce file I/O
        if filename in self.files:
            img = self.files[filename]
        else:
            img = convert_sfc(pg.image.load(filename))
            if cache:
                self.files[filename] = img
        # scale
        if size is not None and size != 1:
            current_size = img.get_size()
            if not isinstance(size, tuple):
                size = (ir(size * current_size[0]), ir(size * current_size[1]))
            # handle None
            for i in (0, 1):
                if size[i] is None:
                    size = list(size)
                    scale = float(size[not i]) / current_size[not i]
                    size[i] = ir(current_size[i] * scale)
            img = pg.transform.smoothscale(img, size)
            # speed up blitting (if not resized, this is already done)
            img = convert_sfc(img)
            if cache:
                # add to cache (if not resized, this is in the file cache)
                self.imgs[key] = img
        return img

    def render_text (self, *args, **kwargs):
        """Render text and cache the result.

Takes the same arguments as fonthandler.Fonts, plus a keyword-only 'cache'
argument.  If passed, the text is cached under this hashable value, and can be
retrieved from cache by calling this function with the same value for this
argument.

Returns the same value as fonthandler.Fonts

"""
        if self.fonts is None:
            raise ValueError('conf.USE_FONTS is False: text rendering isn\'t'
                             'supported')
        cache = 'cache' in kwargs
        if cache:
            key = kwargs['cache']
            if key in self.text:
                return self.text[key]
        # else new: render
        img, lines = self.fonts.render(*args, **kwargs)
        img = convert_sfc(img)
        result = (img, lines)
        if cache:
            self.text[key] = result
        return result

    def play_snd (self, base_ID, volume = 1):
        """Play a sound.

play_snd(base_ID, volume = 1)

base_ID: the ID of the sound to play (we look for base_ID + i for a number i,
         as many sounds as conf.SOUNDS[base_ID]).
volume: float to scale volume by.

"""
        try:
            n = conf.SOUNDS[base_ID]
        except KeyError:
            return
        IDs = [base_ID + str(i) for i in xrange(n)]
        ID = choice(IDs)
        # load sound
        snd = conf.SOUND_DIR + ID + '.ogg'
        snd = pg.mixer.Sound(snd)
        if snd.get_length() < 10 ** -3:
            # no way this is valid
            return
        snd.set_volume(conf.VOL_MUL * conf.SOUND_VOLUME * conf.SOUND_VOLUMES.get(base_ID, 1) * volume)
        snd.play()

    def find_music (self):
        """Store a list of music files."""
        d = conf.MUSIC_DIR
        try:
            files = os.listdir(d)
        except OSError:
            # no directory
            self.music = []
        else:
            self.music = [d + f for f in files if os.path.isfile(d + f)]

    def play_music (self, event = None):
        """Play next piece of music."""
        if self.music:
            f = choice(self.music)
            pg.mixer.music.load(f)
            pg.mixer.music.play()
        else:
            # stop currently playing music if there's no music to play
            pg.mixer.music.stop()

    def _update (self):
        """Update backends and draw."""
        self._update_again = True
        while self._update_again:
            self._update_again = False
            self.backend.event_handler.update()
            # if a new backend was created during the above call, we'll end up
            # updating twice before drawing
            if not self._update_again:
                self._update_again = False
                self.backend.update()
        backend = self.backend
        # fade
        if self.fading:
            frame = self.scheduler.timer.frame
            data = self._fade_data['core']
            fn, duration, persist, t = data
            if duration is None:
                # cancel if returned overlay is None
                o = fn(t)
                cancel = o is None
            else:
                # cancel if time limit passed
                cancel = t + .5 * frame > duration
                if not cancel:
                    o = fn(t)
            if cancel:
                self.cancel_fade(persist)
            else:
                self.set_overlay(o)
                data[3] += frame
        # check overlay
        o0 = self._last_overlay
        o = self.overlay
        o_same = o == o0
        draw = True
        if isinstance(o, pg.Surface):
            o_colour = False
            if o.get_alpha() is None and o.get_colorkey() is None:
                # opaque: don't draw
                draw = False
        elif o is not False:
            if len(o) == 4 and o[3] == 0:
                o = False
            else:
                o_colour = True
                if len(o) == 3 or o[3] == 255:
                    # opaque: don't draw
                    draw = False
        s = self._overlay_sfc
        # draw backend
        screen = self.screen
        if draw:
            dirty = backend.dirty
            draw = backend.draw(screen)
            # if (overlay changed or drew something but perhaps not
            # everything), and we have an overlay (we know this will be
            # transparent), then draw everything (if dirty already drew
            # everything)
            if (draw or o != o0) and not dirty:
                backend.dirty = True
                new_draw = backend.draw(screen)
                # merge draw and new_draw
                if True in (draw, new_draw):
                    draw = True
                else:
                    # know draw != False and now draw != True so is rect list
                    draw = list(draw) + (list(new_draw) if new_draw else [])
        # update overlay surface if changed
        if o not in (o0, False):
            if o_colour:
                s.fill(o)
            else:
                s = o
        # draw overlay if changed or backend drew
        if o is not False and (o != o0 or draw):
            screen.blit(s, (0, 0))
            draw = True
            if o != o0:
                backend.dirty = True
        self._last_overlay = self.overlay
        # update display
        if draw is True:
            pg.display.flip()
        elif draw:
            pg.display.update(draw)
        return True

    def run (self, n = None):
        """Main loop."""
        self.scheduler.run(n)

    def quit (self, event = None):
        """Quit the game."""
        self.scheduler.timer.stop()

    def restart (self, *args):
        """Restart the game."""
        global restarting
        restarting = True
        self.quit()

    def set_overlay (self, overlay, convert = True):
        """Set up an overlay for the current backend.

This draws over the screen every frame after the backend draws.  It takes a
single argument, which is a Pygame-style colour tuple, with or without alpha,
or a pygame.Surface, or False for no overlay.

The overlay is for the current backend only: if another backend is started and
then stopped, the overlay will be restored for the original backend.

The backend's draw method will not be called at all if the overlay to be drawn
this frame is opaque.

"""
        if isinstance(overlay, pg.Surface):
            # surface
            if convert:
                overlay = convert_sfc(overlay)
        elif overlay is not False:
            # colour
            overlay = tuple(overlay)
            # turn RGBA into RGB if no alpha
            if len(overlay) == 4 and overlay[3] == 255:
                overlay = overlay[:3]
        self.overlay = overlay

    def fade (self, fn, time = None, persist = False):
        """Fade an overlay on the current backend.

fade(fn[, time], persist = False)

fn: a function that takes the time since the fade started and returns the
    overlay to use, as taken by Game.set_overlay.
time: fade duration in seconds; this is rounded to the nearest frame.  If None
      or not given, fade_fn may return None to end the fade.
persist: whether to continue to show the current overlay when the fade ends
         (else it is set to False).

Calling this cancels any current fade, and calling Game.set_overlay during the
fade will not have any effect.

"""
        self.fading = True
        self._fade_data = {'core': [fn, time, persist, 0]}

    def cancel_fade (self, persist = True):
        """Cancel any running fade on the current backend.

Takes the persist argument taken by Game.fade.

"""
        self.fading = False
        self._fade_data = None
        if not persist:
            self.set_overlay(False)

    def _colour_fade_fn (self, t):
        """Fade function for Game.colour_fade."""
        f, os, ts = self._fade_data['colour']
        t = f(t)
        # get waypoints we're between
        i = bisect(ts, t)
        if i == 0:
            # before start
            return os[0]
        elif i == len(ts):
            # past end
            return os[-1]
        o0, o1 = os[i - 1:i + 1]
        t0, t1 = ts[i - 1:i + 1]
        # get ratio of the way between waypoints
        if t1 == t0:
            r = 1
        else:
            r = float(t - t0) / (t1 - t0)
        assert 0 <= r <= 1
        o = []
        for x0, x1 in zip(o0, o1):
            # if one is no overlay, use the other's colours
            if x0 is None:
                if x1 is None:
                    # both are no overlay: colour doesn't matter
                    o.append(0)
                o.append(x1)
            elif x1 is None:
                o.append(x0)
            else:
                o.append(x0 + r * (x1 - x0))
        return o

    def colour_fade (self, fn, time, *ws, **kwargs):
        """Start a fade between colours on the current backend.

colour_fade(fn, time, *waypoints, persist = False)

fn: a function that takes the time since the fade started and returns the
    'time' to use in bisecting the waypoints to determine the overlay to use.
time: as taken by Game.fade.  This is the time as passed to fn, not as returned
      by it.
waypoints: two or more points to fade to, each (overlay, time).  overlay is as
           taken by Game.set_overlay, but cannot be a surface, and time is the time in seconds at which that overlay should be reached.  Times must
           be in order and all >= 0.

           For the first waypoint, time is ignored and set to 0, and the
           waypoint may just be the overlay.  For any waypoint except the first
           or the last, time may be None, or the waypoint may just be the
           overlay.  Any group of such waypoints are spaced evenly in time
           between the previous and following waypoints.
persist: keyword-only, as taken by Game.fade.

See Game.fade for more details.

"""
        os, ts = zip(*((w, None) if w is False or len(w) > 2 else w \
                     for w in ws))
        os = list(os)
        ts = list(ts)
        ts[0] = 0
        # get groups with time = None
        groups = []
        group = None
        for i, (o, t) in enumerate(zip(os, ts)):
            # sort into groups
            if t is None:
                if group is None:
                    group = [i]
                    groups.append(group)
            else:
                if group is not None:
                    group.append(i)
                group = None
            # turn into RGBA
            if o is False:
                o = (None, None, None, 0)
            else:
                o = tuple(o)
                if len(o) == 3:
                    o += (255,)
                else:
                    o = o[:4]
            os[i] = o
        # assign times to waypoints in groups
        for a, b in groups:
            assert a != b
            t0 = ts[a - 1]
            dt = float(ts[b] - t0) / (b - (a - 1))
            for i in xrange(a, b):
                ts[i] = t0 + dt * (i - (a - 1))
        # start fade
        persist = kwargs.get('persist', False)
        self.fade(self._colour_fade_fn, time, persist)
        self._fade_data['colour'] = (fn, os, ts)

    def linear_fade (self, *ws, **kwargs):
        """Start a linear fade on the current backend.

Takes the same arguments as Game.colour_fade, without fn and time.

"""
        self.colour_fade(lambda x: x, ws[-1][1], *ws, **kwargs)

    def refresh_display (self, *args):
        """Update the display mode from conf, and notify the backend."""
        # get resolution and flags
        flags = conf.FLAGS
        if conf.FULLSCREEN:
            flags |= pg.FULLSCREEN
            r = conf.RES_F
        else:
            w = max(conf.MIN_RES_W[0], conf.RES_W[0])
            h = max(conf.MIN_RES_W[1], conf.RES_W[1])
            r = (w, h)
        if conf.RESIZABLE:
            flags |= pg.RESIZABLE
        ratio = conf.ASPECT_RATIO
        if ratio is not None:
            # lock aspect ratio
            r = list(r)
            r[0] = min(r[0], r[1] * ratio)
            r[1] = min(r[1], r[0] / ratio)
        conf.RES = r
        self.screen = pg.display.set_mode(conf.RES, flags)
        self._overlay_sfc = pg.Surface(conf.RES).convert_alpha()
        try:
            self.backend.dirty = True
        except AttributeError:
            pass
        # clear image cache (very unlikely we'll need the same sizes)
        self.imgs = {}

    def toggle_fullscreen (self, *args):
        """Toggle fullscreen mode."""
        if conf.RESIZABLE:
            conf.FULLSCREEN = not conf.FULLSCREEN
            self.refresh_display()

    def minimise (self, *args):
        """Minimise the display."""
        pg.display.iconify()

    def _active_cb (self, event):
        """Callback to handle window focus loss."""
        if event.state == 2 and not event.gain:
            try:
                self.backend.pause()
            except (AttributeError, TypeError):
                pass

    def _resize_cb (self, event):
        """Callback to handle a window resize."""
        conf.RES_W = (event.w, event.h)
        self.refresh_display()


if __name__ == '__main__':
    if conf.WINDOW_ICON is not None:
        pg.display.set_icon(pg.image.load(conf.WINDOW_ICON))
    if conf.WINDOW_TITLE is not None:
        pg.display.set_caption(conf.WINDOW_TITLE)
    # options
    op = OptionParser(prog = 'run')
    op.add_option('-l', '--level', action = 'store', dest = 'level',
                  type = 'int')
    op.add_option('-c', '--checkpoint', action = 'store', dest = 'cp',
                  type = 'int')
    op.add_option('-i', '--level-select', action = 'store_true', dest = 'ls')
    op.add_option('-p', '--profile', action = 'store_true', dest = 'profile')
    op.add_option('-t', '--profile-time', action = 'store', dest = 'time',
                  type = 'int')
    op.add_option('-f', '--profile-file', action = 'store', dest = 'fn',
                  type = 'string')
    op.add_option('-n', '--num-stats', action = 'store', dest = 'num_stats',
                  type = 'int')
    op.add_option('-s', '--sort-stats', action = 'store', dest = 'sort_stats',
                  type = 'string')
    op.set_defaults(cp = -1, ls = False, time = conf.PROFILE_TIME,
                    fn = conf.PROFILE_STATS_FILE,
                    num_stats = conf.PROFILE_NUM_STATS,
                    sort_stats = conf.PROFILE_STATS_SORT)
    options = op.parse_args()[0]
    level = options.level
    if level is not None:
        cls = Level
        level_args = (level, options.cp)
    elif options.ls:
        cls = LevelSelect
        level_args = ()
    else:
        if conf.COMPLETED:
            cls = LevelSelect
            level_args = ()
        else:
            cls = Level
            level_args = (conf.CURRENT_LEVEL,)
    if options.profile:
        # profile
        from cProfile import run as profile
        from pstats import Stats
        t = options.time * conf.FPS[get_backend_id(cls)]
        fn = options.fn
        profile('Game({0}, *level_args).run(t)'.format(cls.__name__), fn, locals())
        Stats(fn).strip_dirs().sort_stats(options.sort_stats).print_stats(options.num_stats)
        os.unlink(fn)
    else:
        # run normally
        restarting = True
        while restarting:
            restarting = False
            Game(cls, *level_args).run()

pg.quit()
