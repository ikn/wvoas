import pygame as pg
from ext import evthandler as eh

import conf
import level


class Title (level.Level):
    def __init__ (self, game, event_handler, *level_args):
        Level.__init__(self, game, event_handler, conf.TITLE_LEVEL)
        self.level_args = level_args

    def skip (self, evt):
        f = self.game.start_backend
        self.start_fading(lambda: f(level.PlayableLevel, *self.level_args))

class Paused:
    def __init__ (self, game, event_handler):
        self.game = game
        self.event_handler = event_handler
        self.frame = conf.FRAME
        self.fading = True
        self.fade_counter = conf.PAUSE_FADE_TIME
        self.fade_sfc = pg.Surface(conf.RES).convert_alpha()
        self.sfc = pg.display.get_surface().copy()
        self.text = game.img('paused.png')
        event_handler.add_key_handlers([
            (conf.KEYS_BACK, self.finish, eh.MODE_ONDOWN)
        ])
        pg.mixer.music.set_volume(conf.PAUSED_MUSIC_VOLUME * .01)

    def finish (self, *args):
        pg.mixer.music.set_volume(conf.MUSIC_VOLUME * .01)
        self.game.quit_backend()

    def update (self):
        pass

    def draw (self, screen):
        if self.fading:
            # draw
            t = conf.PAUSE_FADE_TIME - self.fade_counter
            alpha = conf.PAUSE_FADE_RATE * float(t) / conf.PAUSE_FADE_TIME
            alpha = min(255, int(round(alpha)))
            self.fade_sfc.fill((0, 0, 0, alpha))
            screen.blit(self.sfc, (0, 0))
            screen.blit(self.fade_sfc, (0, 0))
            screen.blit(self.text, (0, 0))
            # update counter
            self.fade_counter -= 1
            if self.fade_counter == 0:
                self.fading = False
                del self.fade_sfc
            return True
        else:
            return False