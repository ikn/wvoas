from os import sep

import pygame as pg

# paths
DATA_DIR = ''
IMG_DIR = DATA_DIR + 'img' + sep
SOUND_DIR = DATA_DIR + 'sound' + sep
MUSIC_DIR = DATA_DIR + 'music' + sep

# display
WINDOW_ICON = IMG_DIR + 'icon.png'
WINDOW_TITLE = 'World View of a Slime'
MOUSE_VISIBLE = False
FLAGS = 0
FULLSCREEN = False
RESIZABLE = False # also determines whether fullscreen togglable
RES_W = (960, 540)
RES_F = pg.display.list_modes()[0]
MIN_RES_W = (320, 180)
ASPECT_RATIO = None

# timing
FPS = 60
FRAME = 1. / FPS

# debug
DEBUG_INITIAL_LEVEL = 0
DEBUG_INITIAL_CP = -1
PROFILE_STATS_FILE = '.profile_stats'
DEFAULT_PROFILE_TIME = 5

# input
KEYS_NEXT = (pg.K_RETURN, pg.K_SPACE, pg.K_KP_ENTER)
KEYS_BACK = (pg.K_ESCAPE, pg.K_BACKSPACE)
KEYS_MINIMISE = (pg.K_F10,)
KEYS_FULLSCREEN = (pg.K_F11, (pg.K_RETURN, pg.KMOD_ALT, True),
                   (pg.K_KP_ENTER, pg.KMOD_ALT, True))
KEYS_LEFT = (pg.K_LEFT, pg.K_a, pg.K_q)
KEYS_RIGHT = (pg.K_RIGHT, pg.K_d, pg.K_e)
KEYS_MOVE = (KEYS_LEFT, KEYS_RIGHT)
KEYS_JUMP = (pg.K_UP, pg.K_SPACE, pg.K_w, pg.K_z, pg.K_COMMA)
KEYS_RESET = (pg.K_r, pg.K_p)

# audio
MUSIC_VOLUME = 70
PAUSED_MUSIC_VOLUME = 20
SOUND_VOLUME = 50
EVENT_ENDMUSIC = pg.USEREVENT
SOUNDS = {'hit': 10, 'die': 4}
SOUND_VOLUMES = {'hit': 1. / 13, 'die': 2, 'move': .5}
HIT_VOL_THRESHOLD = 2 # before scaling

# gameplay (sizes must be ints)
PLAYER_SIZE = (15, 30)
PLAYER_SPEED = 1
PLAYER_AIR_SPEED = .2
LAUNCH_SPEED = .5
INITIAL_JUMP = 5
CONTINUE_JUMP = .7
FAIL_JUMP = 2
JUMP_TIME = 10
ON_GROUND_TIME = 2
DIE_TIME = 120
DIE_SKIP_THRESHOLD = 100 # can skip when counted down this low from DIE_TIME
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

# levels
CAN_JUMP = range(8)
CAN_MOVE = range(12)
# all positions must be ints
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
    'player_pos': (100, 320),
    'goal': (860, 290),
    'rects': [(0, 350, 960, 45)],
    'arects': [(250, 250, 460, 100)]
}, {
    'player_pos': (100, 240),
    'goal': (50, 50),
    'checkpoints': [(785, 210)],
    'rects': [(100, 0, 570, 150), (0, 270, 250, 10), (330, 520, 150, 20),
              (570, 150, 100, 130), (570, 400, 100, 140), (740, 230, 100, 220)]
}, {
    'player_pos': (150, 420),
    'goal': (900, 120),
    'checkpoints': [(520, 330), (270, 160)],
    'rects': [(0, 450, 960, 10), (0, 400, 960, 10), (500, 350, 460, 10),
              (300, 290, 200, 10), (150, 210, 150, 40), (150, 180, 100, 40),
              (550, 180, 960, 10), (500, 0, 10, 140)],
    'arects': [(500, 290, 460, 10), (250, 180, 50, 10)]
},
    # can't jump
{
    'player_pos': (100, 310),
    'goal': (860, 280),
    'rects': [(0, 340, 250, 60), (710, 340, 250, 60)],
    'arects': [(250, 240, 460, 160)]
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
    'player_pos': (100, 220),
    'goal': (50, 80),
    'checkpoints': [(615, 80)],
    'rects': [(100, 100, 200, 50), (0, 250, 200, 10), (570, 100, 100, 180),
              (570, 400, 100, 100)],
    'arects': [(570, 500, 300, 40)]
},
    # can't move
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
}]

# graphics
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
VOID_JITTER_T = 1
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
    }, 'fail_jump': {
        'colours': (((10, 10, 10), 2), ((30, 30, 30), 1),
                    ((36, 130, 36), .5), ((25, 91, 25), .2),
                    ((47, 169, 47), .2)),
        'speed': 3,
        'life': 90,
        'size': 4,
        'damping': .98,
        'jitter': 0
    }
}