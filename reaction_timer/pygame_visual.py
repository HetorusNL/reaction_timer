import logging
import math
import pygame
from pygame.font import Font

LOG = logging.getLogger()
LOG.setLevel(logging.DEBUG)


class PygameVisual(object):
    def __init__(self):
        LOG.debug("initializing PygameVisual")
        pygame.init()
        self.width = 1280
        self.height = 720
        self.pg_screen = pygame.display.set_mode((1280, 720), pygame.RESIZABLE)
        self.last_color = (0, 0, 0)
        self._countdown_finished = False
        self.countdown_time = 3

    def countdown_finished(self):
        return self._countdown_finished

    def run_countdown(self, time_delta):
        self.countdown_time -= time_delta
        value = math.ceil(self.countdown_time)
        if value <= 0:
            LOG.info("countdown completed")
            # reset countdown_time for future countdowns
            self.countdown_time = 3
            self._countdown_finished = True
            self._draw_text("START", 0.25)
            return True

        self._draw_text(value, self.countdown_time % 1)
        return False

    def process_event_loop(self):
        result = {}
        for event in pygame.event.get():
            if (
                event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
            ) or event.type == pygame.QUIT:
                result["shutdown"] = True
            elif event.type == pygame.MOUSEBUTTONDOWN:
                result["strike"] = True
            elif event.type == pygame.VIDEORESIZE:
                self.pg_screen = pygame.display.set_mode(
                    (event.w, event.h), pygame.RESIZABLE
                )
                self.width = event.w
                self.height = event.h
                # make sure to make the screen the same color as it was
                self.set_screen_color(self.last_color)

        return result

    def set_screen_color(self, color):
        self.last_color = color
        self.pg_screen.fill(color)
        pygame.display.update()

    def _draw_text(self, text, size):
        font = Font(None, int(400 * size + 100))
        text = font.render(str(text), True, (255, 255, 255))
        text_rect = text.get_rect()
        text_rect.center = (self.width / 2, self.height / 2)
        self.pg_screen.fill((0, 0, 0))
        self.pg_screen.blit(text, text_rect)
        pygame.display.update()
