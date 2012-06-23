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
PLAYER_MASS = 50
PLAYER_SIZE = (15, 30)
PLAYER_ELAST = 0
PLAYER_SPEED = 1
PLAYER_AIR_SPEED = .2
INITIAL_JUMP = 5
CONTINUE_JUMP = .7
JUMP_TIME = 10
OBJ_ELAST = 0
GRAV = .5
FRICT = .15
AIR_RES = .0025
GOAL_SIZE = (10, 60)
HALF_WINDOW_SIZE = (125, 75)

# levels
LEVELS = [{
    'player_pos': (100, 420),
    'goal': (900, 390),
    'rects': [(0, 450, 350, 550), (150, 385, 350, 450), (250, 320, 350, 385),
              (450, 320, 550, 540), (800, 450, 960, 540)]
}, {
    'player_pos': (100, 420),
    'goal': (900, 390),
    'rects': [(0, 450, 960, 540), (200, 250, 230, 450), (470, 250, 680, 450)]
}, {
    'player_pos': (150, 120),
    'goal': (850, 440),
    'rects': [(0, 150, 500, 160), (500, 0, 960, 440), (500, 500, 960, 540)]
}, {
    'player_pos': (150, 420),
    'goal': (800, 190),
    'rects': [(0, 450, 600, 500), (0, 400, 600, 410), (0, 350, 600, 360),
              (0, 310, 600, 320), (0, 250, 600, 290), (760, 450, 960, 500),
              (760, 400, 960, 410), (760, 350, 960, 360), (760, 310, 960, 320),
              (760, 250, 960, 290)]
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