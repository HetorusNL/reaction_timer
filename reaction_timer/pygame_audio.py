import logging
import pygame
from pygame.mixer import Sound

LOG = logging.getLogger(__name__)
LOG.setLevel(logging.INFO)


class PygameAudio(object):
    def __init__(self):
        LOG.info("initializing PygameAudio")
        try:
            pygame.mixer.init(buffer=512)
            self.has_audio = True
            LOG.info("audio initialized successfully")
        except pygame.error:
            self.has_audio = False
            LOG.warning("failed to initialize audio!")

        if self.has_audio:
            self.tick = Sound("reaction_timer/resources/metronome-3.wav")
            self.tock = Sound("reaction_timer/resources/metronome-4.wav")

    def play_tick(self):
        # add audible click (tick)
        if self.has_audio:
            self.tick.play()

    def play_tock(self):
        # add audible click (tock)
        if self.has_audio:
            self.tock.play()
