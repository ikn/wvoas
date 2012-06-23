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
HALF_WINDOW_SIZE = (125, 75)

ascend_rects = []
ascend_arects = []
for i, (x1, x2) in enumerate(((20, 30), (40, 50))):
    y0 = 450 - i * 60
    ascend_rects.append((0, y0, x1, 10))
    ascend_arects.append((x1, y0, x2 - x1, 10))
    ascend_rects.append((x2, y0, 960 - x2, 10))

# levels
LEVELS = [{
    'player_pos': (100, 420),
    'goal': (900, 390),
    'rects': [(0, 450, 960, 90), (200, 0, 50, 450), (400, 0, 300, 450)]
}, {
    'player_pos': (100, 420),
    'goal': (900, 390),
    'rects': [(0, 450, 960, 90)],
    'arects': [(200, 0, 50, 450), (400, 0, 300, 450)]
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
    'goal': (800, 190),
    'rects': ascend_rects,
    'arects': ascend_arects
}, {
    'player_pos': (100, 420),
    'goal': (25, 225),
    'rects': [(0, 450, 900, 535), (0, 535, 960, 540), (0, 285, 85, 315),
              (350, 315, 380, 450), (85, 60, 380, 315), (380, 375, 960, 450),
              (530, 300, 960, 375), (615, 230, 960, 300), (380, 60, 500, 240),
              (500, 230, 615, 240), (650, 0, 960, 230), (575, 165, 650, 170),
              (500, 100, 575, 105), (400, 0, 500, 60)]
}, {
    'player_pos': (100, 320),
    'goal': (860, 290),
    'rects': [(0, 350, 960, 360), (250, 250, 710, 345)]
}, {
    'player_pos': (430, 320),
    'goal': (530, 290),
    'rects': [(425, 350, 450, 360), (475, 0, 485, 540)]
}]