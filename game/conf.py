from platform import system
import os
from os.path import sep, expanduser, join as join_path
from collections import defaultdict

import pygame as pg

import settings
from util import dd


class Conf (object):

    IDENT = 'wvoas'
    USE_SAVEDATA = True
    USE_FONTS = False

    # save data
    SAVE = ('CURRENT_LEVEL', 'COMPLETED_LEVELS', 'COMPLETED')
    # need to take care to get unicode path
    if system() == 'Windows':
        try:
            import ctypes
            n = ctypes.windll.kernel32.GetEnvironmentVariableW(u'APPDATA', None, 0)
            if n == 0:
                raise ValueError()
        except Exception:
            # fallback (doesn't get unicode string)
            CONF_DIR = os.environ[u'APPDATA']
        else:
            buf = ctypes.create_unicode_buffer(u'\0' * n)
            ctypes.windll.kernel32.GetEnvironmentVariableW(u'APPDATA', buf, n)
            CONF_DIR = buf.value
        CONF_DIR = join_path(CONF_DIR, IDENT)
    else:
        CONF_DIR = join_path(os.path.expanduser(u'~'), '.config', IDENT)
    CONF = join_path(CONF_DIR, 'conf')

    # paths
    DATA_DIR = ''
    IMG_DIR = DATA_DIR + 'img' + sep
    SOUND_DIR = DATA_DIR + 'sound' + sep
    MUSIC_DIR = DATA_DIR + 'music' + sep

    # display
    WINDOW_ICON = IMG_DIR + 'icon.png'
    WINDOW_TITLE = 'World View of a Slime'
    MOUSE_VISIBLE = dd(True, {'level': False})
    FLAGS = 0
    FULLSCREEN = False
    RESIZABLE = False # also determines whether fullscreen togglable
    RES_W = (960, 540)
    RES_F = pg.display.list_modes()[0]
    RES = RES_W
    MIN_RES_W = (320, 180)
    ASPECT_RATIO = None

    # timing
    FPS = dd(60) # keys are backend IDs

    # debug
    PROFILE_TIME = 5
    PROFILE_STATS_FILE = '.profile_stats'
    PROFILE_NUM_STATS = 20
    PROFILE_STATS_SORT = 'cumulative'

    # input
    KEYS_NEXT = (pg.K_RETURN, pg.K_SPACE, pg.K_KP_ENTER)
    KEYS_BACK = (pg.K_ESCAPE, pg.K_BACKSPACE)
    KEYS_MINIMISE = (pg.K_F10,)
    KEYS_FULLSCREEN = (pg.K_F11, (pg.K_RETURN, pg.KMOD_ALT, True),
                    (pg.K_KP_ENTER, pg.KMOD_ALT, True))
    KEYS_LEFT = (pg.K_LEFT, pg.K_a, pg.K_q)
    KEYS_RIGHT = (pg.K_RIGHT, pg.K_d, pg.K_e)
    KEYS_UP = (pg.K_UP, pg.K_w, pg.K_z, pg.K_COMMA)
    KEYS_DOWN = (pg.K_DOWN, pg.K_s, pg.K_o)
    KEYS_MOVE = (KEYS_LEFT, KEYS_UP, KEYS_RIGHT, KEYS_DOWN)
    KEYS_JUMP = (pg.K_SPACE,) + KEYS_UP
    KEYS_RESET = (pg.K_r, pg.K_p)

    # audio
    MUSIC_VOLUME = dd(.7, paused = .2)
    SOUND_VOLUME = .5
    EVENT_ENDMUSIC = pg.USEREVENT
    SOUNDS = {'hit': 10, 'die': 4}
    SOUND_VOLUMES = {'hit': 1. / 13, 'die': 2, 'move': .5}
    HIT_VOL_THRESHOLD = 2 # before scaling

    # gameplay (sizes must be ints)
    PLAYER_SIZE = (15, 30)
    PLAYER_SPEED = 1
    PLAYER_AIR_SPEED = .2
    LAUNCH_SPEED = .6
    INITIAL_JUMP = 5
    CONTINUE_JUMP = .7
    FAIL_JUMP = 2
    JUMP_TIME = 10
    ON_GROUND_TIME = 2
    DIE_TIME = 120
    # can skip when counted down this low from DIE_TIME
    DIE_SKIP_THRESHOLD = 100
    WIN_SKIP_THRESHOLD = 100
    GRAV = .5
    FRICT = .15
    AIR_RES = .0025
    GOAL_SIZE = (5, 60)
    CHECKPOINT_SIZE = (10, 10)
    HALF_WINDOW_SIZE = (125, 75)
    WINDOW_SIZE = [x * 2 for x in HALF_WINDOW_SIZE]
    ERR = 10 ** -10
    WINDOW_MOVE_AMOUNT = 3

    # levels (all positions must be ints)
    LEVELS = [{
        'bgs': ('bg', ('bg0', (154, 75))),
        'player_pos': (100, 25),
        'goal': (100, 440),
        'rects': [(0, 300, 960, 100), (0, 500, 960, 40)],
        'arects': [(0, 55, 850, 5), (110, 185, 960, 5)]
    }, {
        'player_pos': (100, 420),
        'goal': (900, 390),
        'rects': [(0, 460, 325, 80), (325, 450, 635, 90), (200, 0, 50, 450),
                  (400, 0, 300, 450)],
        'arects': [(0, 450, 325, 10)]
    }, {
        'player_pos': (100, 420),
        'goal': (900, 390),
        'rects': [(0, 450, 960, 90)],
        'arects': [(200, 0, 50, 450), (400, 400, 50, 140), (600, 0, 50, 450)]
    }, {
        'player_pos': (200, 120),
        'goal': (850, 440),
        'rects': [(0, 150, 400, 10), (560, 500, 400, 10)]
    }, {
        'player_pos': (200, 120),
        'goal': (850, 440),
        'rects': [(0, 150, 400, 10), (560, 500, 400, 10)],
        'arects': [(400, 0, 10, 160)]
    }, {
        'player_pos': (472, 70),
        'goal': (478, 440),
        'rects': [(220, 100, 100, 10), (640, 100, 100, 10),
                  (200, 140, 140, 10), (470, 200, 20, 10)],
        'arects': [(0, 60, 960, 10), (0, 100, 220, 10), (320, 100, 320, 10),
                   (740, 100, 220, 10), (0, 140, 200, 10), (760, 140, 200, 10),
                   (340, 140, 10, 60), (610, 140, 10, 60), (340, 200, 130, 10),
                   (490, 200, 130, 10)]
    }, {
        'player_pos': (100, 320),
        'goal': (860, 290),
        'rects': [(0, 350, 960, 45)],
        'arects': [(250, 250, 460, 100)]
    }, {
        'player_pos': (100, 240),
        'goal': (50, 50),
        'checkpoints': [(785, 210)],
        'rects': [(100, 0, 570, 150), (0, 270, 250, 10), (330, 520, 150, 20),
                  (570, 150, 100, 130), (570, 400, 100, 140),
                  (740, 230, 100, 220)]
    }, {
        'player_pos': (150, 420),
        'goal': (900, 120),
        'checkpoints': [(520, 330), (270, 160)],
        'rects': [(0, 450, 960, 10), (0, 400, 960, 10), (500, 350, 460, 10),
                  (300, 290, 200, 10), (150, 210, 150, 40),
                  (150, 180, 100, 40), (550, 180, 960, 10), (500, 0, 10, 140)],
        'arects': [(500, 290, 460, 10), (250, 180, 50, 10)]
    }, {
        'player_pos': (50, 240),
        'goal': (850, 240),
        'rects': [(10, 270, 140, 50), (310, 270, 140, 50), (750, 70, 30, 400)],
        'vrects': [(160, 270, 140, 50), (460, 70, 490, 400)]
    }, {
        'player_pos': (230, 180),
        'goal': (720, 95),
        'checkpoints': [(475, 420)],
        'rects': [(0, 210, 475, 50), (0, 320, 475, 50), (485, 265, 475, 50)],
        'vrects': [(0, 265, 475, 50), (0, 375, 960, 130), (485, 155, 475, 50)],
        'arects': [(475, 0, 10, 370)]
    },
        'disable jump',
    {
        'player_pos': (100, 310),
        'goal': (860, 280),
        'rects': [(0, 340, 200, 60), (760, 340, 200, 60)],
        'vrects': [(380, 340, 200, 60)],
        'arects': [(200, 240, 180, 160), (580, 240, 180, 160)]
    }, {
        'player_pos': (200, 340),
        'goal': (760, 310),
        'rects': [(0, 370, 455, 170), (505, 370, 455, 170)],
        'arects': [(455, 0, 50, 540)]
    }, {
        'player_pos': (100, 120),
        'goal': (860, 390),
        'rects': [(0, 150, 300, 10), (660, 450, 300, 10)],
        'arects': [(0, 110, 300, 10)]
    }, {
        'player_pos': (180, 120),
        'goal': (750, 450),
        'checkpoints': [(595, 320)],
        'rects': [(0, 150, 200, 10)],
        'vrects': [(550, 0, 100, 340)],
        'arects': [(550, 340, 100, 200)]
    }, {
        'player_pos': (100, 220),
        'goal': (50, 80),
        'checkpoints': [(615, 80)],
        'rects': [(0, 250, 250, 10), (570, 100, 100, 180),
                  (570, 400, 100, 100)],
        'vrects': [(100, 100, 200, 50)],
        'arects': [(570, 500, 300, 40)]
    }, {
        'player_pos': (322, 265),
        'goal': (428, 135),
        'rects': [(380, 195, 95, 75), (475, 195, 105, 55), (583, 245, 97, 55),
                  (480, 295, 100, 50)],
        'vrects': [(480, 245, 97, 50), (580, 295, 100, 50)],
        'arects': [(280, 295, 200, 50)]
    }, {
        'player_pos': (53, 480),
        'goal': (898, 450),
        'checkpoints': [(470, 490)],
        'rects': [(0, 510, 960, 30), (185, 50, 15, 260), (685, 50, 15, 160)],
        'vrects': [(185, 310, 15, 200), (0, 110, 15, 200),
                   (685, 210, 15, 300)],
        'arects': [(0, 0, 450, 10), (200, 50, 50, 460), (450, 0, 50, 460),
                   (700, 50, 50, 460)]
    },
        'disable move',
    {
        'player_pos': (370, 170),
        'goal': (580, 390),
        'rects': [(0, 200, 960, 150), (0, 450, 960, 60)],
        'arects': [(0, 510, 960, 30)]
    }, {
        'player_pos': (370, 170),
        'goal': (580, 390),
        'rects': [(0, 200, 960, 150), (0, 450, 960, 90)]
    }, {
        'player_pos': (100, 420),
        'goal': (900, 390),
        'rects': [(0, 450, 960, 60)],
        'arects': [(0, 510, 960, 30), (200, 0, 50, 450), (400, 400, 50, 140),
                   (600, 0, 50, 450)]
    }, {
        'player_pos': (50, 310),
        'goal': (860, 280),
        'checkpoints': [(600, 220)],
        'rects': [(0, 340, 300, 60), (300, 240, 460, 10), (760, 340, 200, 60)],
        'arects': [(300, 250, 460, 150)]
    },
        'disable exists',
    {
        'player_pos': (473, 255),
        'goal': (500, -100),
        'vrects': [(0, 0, 960, 540)]
    }]
    # compile some properties
    CAN_JUMP = [True]
    CAN_MOVE = [True]
    EXISTS = [True]
    _properties = {'jump': CAN_JUMP, 'move': CAN_MOVE, 'exists': EXISTS}
    i = 0
    while i < len(LEVELS):
        s = LEVELS[i]
        if isinstance(s, basestring):
            # property modifier: alter property list's first item
            if s.startswith('disable'):
                s = s[8:]
                v = False
            else: # enable
                s = s[7:]
                v = True
            for p, l in _properties.iteritems():
                if s == p:
                    l[0] = v
            # remove from LEVELS
            LEVELS.pop(i)
        else:
            # level
            for p, l in _properties.iteritems():
                if l[0]:
                    l.append(i)
            i += 1
    for l in _properties.itervalues():
        l.pop(0)
    del _properties
    CURRENT_LEVEL = 0
    COMPLETED_LEVELS = []
    COMPLETED = False

    # graphics
    # level select
    LS_BG_COLOUR = (120, 120, 120)
    LS_HL_COLOUR = (150, 150, 0)
    LS_HL_WIDTH = 2
    LS_FADE_IN = ((0, 0, 0), (False, 1.5))
    LS_FADE_OUT = (False, ((0, 0, 0), 1.5))
    LS_LEVEL_START_TIME = 2
    LS_WON_OVERLAY = (0, 0, 0, 150)
    # images
    DEFAULT_BGS = ('bg',)
    BGS = DEFAULT_BGS + sum((l.get('bgs', ()) for l in LEVELS), ())
    BGS = tuple(set([bg if isinstance(bg, str) else bg[0] for bg in BGS]))
    NUM_CLOUDS = 4
    CLOUDS = tuple('cloud{0}'.format(i) for i in xrange(NUM_CLOUDS))
    CLOUD_SPEED = .5
    CLOUD_VERT_SPEED_RATIO = .1
    CLOUD_MOD_SPEED_RATIO = .2
    CLOUD_JITTER = .01
    PLAYER_OFFSET = (-7, -2)
    PLAYER_SQUASH_ELAST = .7
    PLAYER_SQUASH_STIFFNESS = .2
    PLAYER_MIN_SQUASH = .4
    PLAYER_MAX_SQUASH = 1.5
    PLAYER_SKEW_ELAST = .85
    PLAYER_SKEW_STIFFNESS = .1
    PLAYER_MAX_SKEW = 4
    GOAL_OFFSET = (-17, -2)
    VOID_JITTER_X = 10
    VOID_JITTER_Y = 10
    VOID_JITTER_T = 5
    # fades
    FADE_TIME = 120
    FADE_RATE = 300 # rate * time_ratio = 255 * alpha
    PAUSE_FADE_TIME = 60
    PAUSE_FADE_RATE = 200 # rate * time_ratio = 255 * alpha
    # particles
    PARTICLES = {
        'die': {
            'colours': (((36, 130, 36), 1500), ((25, 91, 25), 1000),
                        ((47, 169, 47), 500)),
            'speed': 10,
            'life': 180,
            'size': 5,
            'damping': .98,
            'jitter': .035
        }, 'move': {
            'colours': (((10, 10, 10), .2), ((30, 30, 30), .1),
                        ((36, 130, 36), .05), ((25, 91, 25), .02),
                        ((47, 169, 47), .02)),
            'speed': 2,
            'life': 60,
            'size': 4,
            'damping': 1,
            'jitter': 0
        }, 'jump': {
            'colours': (((10, 10, 10), 20), ((30, 30, 30), 10),
                        ((36, 130, 36), 5), ((25, 91, 25), 2),
                        ((47, 169, 47), 2)),
            'speed': 5,
            'life': 90,
            'size': 4,
            'damping': .98,
            'jitter': 0
        }
    }


def translate_dd (d):
    if isinstance(d, defaultdict):
        return defaultdict(d.default_factory, d)
    else:
        # should be (default, dict)
        return dd(*d)
conf = dict((k, v) for k, v in Conf.__dict__.iteritems()
            if not k.startswith('__'))
types = {
    defaultdict: translate_dd
}
if Conf.USE_SAVEDATA:
    conf = settings.SettingsManager(conf, Conf.CONF, Conf.SAVE, types)
else:
    conf = settings.DummySettingsManager(conf, types)