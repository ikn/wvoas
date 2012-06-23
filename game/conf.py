from os import sep

import pygame as pg

# paths
DATA_DIR = ''
IMG_DIR = DATA_DIR + 'img' + sep
SOUND_DIR = DATA_DIR + 'sound' + sep
MUSIC_DIR = DATA_DIR + 'music' + sep
FONT_DIR = DATA_DIR + 'font' + sep

# display
WINDOW_ICON = None #IMG_DIR + 'icon.png'
WINDOW_TITLE = ''
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

# input
KEYS_NEXT = (pg.K_RETURN, pg.K_SPACE, pg.K_KP_ENTER)
KEYS_BACK = (pg.K_ESCAPE, pg.K_BACKSPACE)
KEYS_MINIMISE = (pg.K_F10,)
KEYS_FULLSCREEN = (pg.K_F11, (pg.K_RETURN, pg.KMOD_ALT, True),
                   (pg.K_KP_ENTER, pg.KMOD_ALT, True))
KEYS_LEFT = (pg.K_LEFT, pg.K_a)
KEYS_RIGHT = (pg.K_RIGHT, pg.K_d, pg.K_e)
KEYS_MOVE = (KEYS_LEFT, KEYS_RIGHT)
KEYS_JUMP = (pg.K_UP, pg.K_SPACE, pg.K_w, pg.K_COMMA)

# audio
MUSIC_VOLUME = 50
SOUND_VOLUME = 50
EVENT_ENDMUSIC = pg.USEREVENT
SOUNDS = {}
SOUND_VOLUMES = {}

# gameplay
PLAYER_SIZE = (15, 30)
PLAYER_SPEED = 1
PLAYER_AIR_SPEED = .2
INITIAL_JUMP = 5
CONTINUE_JUMP = .7
JUMP_TIME = 10
ON_GROUND_TIME = 2
GRAV = .5
FRICT = .15
AIR_RES = .0025
GOAL_SIZE = (10, 60)
CHECKPOINT_SIZE = (10, 10)
HALF_WINDOW_SIZE = (125, 75)
ERR = 10 ** -10

# levels
LEVELS = [{
    'player_pos': (100, 420),
    'goal': (900, 390),
    'rects': [(0, 450, 960, 90), (200, 0, 50, 450), (400, 0, 300, 450)]
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
    'player_pos': (150, 420),
    'goal': (900, 100),
    'checkpoints': [(520, 330), (270, 160)],
    'rects': [(0, 450, 960, 10), (0, 400, 960, 10), (500, 350, 460, 10),
              (300, 290, 200, 10), (150, 210, 150, 40), (150, 180, 100, 40),
              (550, 160, 960, 10), (450, 0, 10, 120)],
    'arects': [(500, 290, 460, 10), (250, 180, 50, 10)]
}, {
    'player_pos': (100, 320),
    'goal': (860, 290),
    'rects': [(0, 350, 960, 45)],
    'arects': [(250, 250, 460, 100)]
}, {
    'player_pos': (100, 220),
    'goal': (50, 80),
    'checkpoints': [(785, 210)],
    'rects': [(100, 0, 570, 150), (0, 250, 250, 10), (570, 150, 100, 130),
              (330, 520, 150, 20), (570, 400, 100, 140), (740, 230, 100, 220)]
}]