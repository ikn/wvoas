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
PLAYER_SPEED = .8
PLAYER_AIR_SPEED = .2
INITIAL_JUMP = 5
CONTINUE_JUMP = .7
JUMP_TIME = 10
OBJ_ELAST = 0
GRAV = .5
FRICT = .08
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
    'player_pos': (150, 220),
    'goal': (900, 440),
    'rects': [(0, 250, 300, 300), (0, 200, 300, 210), (0, 150, 300, 160),
              (0, 110, 300, 120), (0, 50, 300, 90), (300, 50, 560, 540),
              (560, 150, 800, 400), (580, 0, 800, 150), (320, 500, 960, 540)]
}]