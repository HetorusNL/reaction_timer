import logging
import pygame
from pygame.mixer import Sound

LOG = logging.getLogger()
LOG.setLevel(logging.DEBUG)


class PygameAudio(object):
    def __init__(self):
        LOG.debug("initializing PygameAudio")
        try:
            pygame.mixer.init(buffer=512)
            self.has_audio = True
            LOG.info("audio initialized successfully")
        except pygame.error:
            self.has_audio = False
            LOG.warning("failed to initialize audio!")

        if self.has_audio:
            self.metronome = Sound("reaction_timer/resources/metronome-1.wav")

    def play_sound(self):
        # add audible click (metronome)
        if self.has_audio:
            self.metronome.play()
