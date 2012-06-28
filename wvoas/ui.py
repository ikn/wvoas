import pygame as pg
from ext import evthandler as eh

import conf
from level import Level, PlayableLevel


class Title (Level):
    def __init__ (self, game, event_handler, *level_args):
        Level.__init__(self, game, event_handler, conf.TITLE_LEVEL)
        self.level_args = level_args

    def skip (self, evt):
        self.start_fading(lambda: self.game.start_backend(PlayableLevel, *self.level_args))