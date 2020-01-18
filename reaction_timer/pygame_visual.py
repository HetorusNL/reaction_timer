import logging
import math
import pygame
from pygame.font import Font

LOG = logging.getLogger()
LOG.setLevel(logging.DEBUG)


class PygameVisual(object):
    def __init__(self, pygame_audio):
        LOG.debug("initializing PygameVisual")
        self.pygame_audio = pygame_audio
        pygame.init()
        self.width = 1280
        self.height = 720
        self.pg_screen = pygame.display.set_mode((1280, 720), pygame.RESIZABLE)
        self.last_color = None
        self.last_display_trigger = None
        self._initialize_finished = None
        self._initialize_states = None
        self._initialize_state = None
        self._midi_events = None
        self._key_events = None
        self._mouse_events = None
        self._trigger = None
        self._countdown_finished = None
        self.countdown_time = None
        self.prev_cntdwn_time = None
        self._which_trigger = None
        # initialize / cleanup by using _reset function
        self._reset()

    def initialize_finished(self):
        return self._initialize_finished

    def run_initialize(self):
        # state machine that runs through the initialization / mapping sequence
        current_state = self._initialize_states[self._initialize_state]
        self._draw_text(current_state["text"], 50)
        func = current_state["func"]
        # check for midi/keyboard/mouse events for left trigger
        processed = False
        processed = func(self._midi_events, "midi", processed)
        processed = func(self._key_events, "keyboard", processed)
        processed = func(self._mouse_events, "mouse", processed)
        return processed and self._initialize_finished

    def _get_left(self, buffer, trigger_type, processed):
        if len(buffer) > 0 and not processed:
            self._trigger["left"]["type"] = trigger_type
            self._trigger["left"]["trigger"] = buffer[0]
            self._initialize_state = "get_left_again"
            buffer.remove(buffer[0])
            return True
        return processed

    def _get_left_again(self, buffer, trigger_type, processed):
        if len(buffer) > 0 and not processed:
            if self._trigger["left"]["type"] == trigger_type:
                if self._trigger["left"]["trigger"] == buffer[0]:
                    self._initialize_state = "get_right"
                else:
                    self._initialize_state = "get_left"
            else:
                self._initialize_state = "get_left"
            buffer.remove(buffer[0])
            return True
        return processed

    def _get_right(self, buffer, trigger_type, processed):
        if len(buffer) > 0 and not processed:
            self._trigger["right"]["type"] = trigger_type
            self._trigger["right"]["trigger"] = buffer[0]
            self._initialize_state = "get_right_again"
            buffer.remove(buffer[0])
            return True
        return processed

    def _get_right_again(self, buffer, trigger_type, processed):
        if len(buffer) > 0 and not processed:
            if self._trigger["right"]["type"] == trigger_type:
                if self._trigger["right"]["trigger"] == buffer[0]:
                    self._initialize_state = "any_to_start"
                else:
                    self._initialize_state = "get_right"
            else:
                self._initialize_state = "get_right"
            buffer.remove(buffer[0])
            return True
        return processed

    def _any_to_start(self, buffer, trigger_type, processed):
        _ = trigger_type
        while len(buffer) > 0:
            buffer.remove(buffer[0])
            self._initialize_finished = True
            processed = True
        return processed

    def countdown_finished(self):
        return self._countdown_finished

    def run_countdown(self, time_delta):
        self.countdown_time -= time_delta
        # play audio if changing between countdown numbers and at start
        value = math.ceil(self.countdown_time)
        if value != self.prev_cntdwn_time:
            self.prev_cntdwn_time = value
            self.pygame_audio.play_sound()

        if value <= 0:
            LOG.info("countdown completed")
            # reset countdown_time for future countdowns
            self.countdown_time = 3
            self._countdown_finished = True
            self._draw_text("START", int(400 * 0.25 + 100))
            return True

        self._draw_text(value, int(400 * (self.countdown_time % 1) + 100))
        return False

    def process_event_loop(self):
        result = {}
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                result["shutdown"] = True
            elif event.type == pygame.QUIT:
                result["shutdown"] = True
            elif event.type == pygame.KEYDOWN:
                if self.initialize_finished():
                    trigger = self._trigger[self._which_trigger]
                    if trigger["type"] == "keyboard":
                        if trigger["trigger"] == event.key:
                            result["strike"] = True
                else:
                    self._key_events.append(event.key)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.initialize_finished():
                    if self._trigger[self._which_trigger]["type"] == "mouse":
                        result["strike"] = True
                else:
                    self._mouse_events.append(None)
            elif event.type == pygame.VIDEORESIZE:
                self.pg_screen = pygame.display.set_mode(
                    (event.w, event.h), pygame.RESIZABLE
                )
                self.width = event.w
                self.height = event.h
                # make sure to make the screen the same color as it was
                if self.last_display_trigger:
                    self.display_trigger(self.last_display_trigger)
                else:
                    self.set_screen_color(self.last_color)

        return result

    def set_trigger(self, which_trigger):
        self._which_trigger = which_trigger

    def display_trigger(self, color):
        self.set_screen_color((0, 0, 0))
        self.last_display_trigger = color
        if self._which_trigger == "left":
            left = int(self.width / 8)
        elif self._which_trigger == "right":
            left = int(self.width * 5 / 8)
        else:
            LOG.error("display_trigger called ith no valid _which_trigger!")
            return
        top = int(self.height / 4)
        width = int(self.width / 4)
        height = int(self.height / 2)
        LOG.debug(f"generated square at: ({left}, {top}), ({width}, {height})")
        LOG.debug(f"color: {color}")

        rect = pygame.Rect((left, top), (width, height))
        # rect = pygame.Rect((80, 18), (32, 36))
        self.pg_screen.fill(color, rect)
        pygame.display.update()

    def set_screen_color(self, color):
        self.last_color = color
        self.last_display_trigger = None
        self.pg_screen.fill(color)
        pygame.display.update()

    def _draw_text(self, text, size):
        font = Font(None, size)
        text = font.render(str(text), True, (255, 255, 255))
        text_rect = text.get_rect()
        text_rect.center = (self.width / 2, self.height / 2)
        self.pg_screen.fill((0, 0, 0))
        self.pg_screen.blit(text, text_rect)
        pygame.display.update()

    def _reset(self):
        self.last_color = (0, 0, 0)
        self._initialize_finished = False
        self._initialize_states = {
            "get_left": {
                "func": self._get_left,
                "text": "Hit left hand drum pad, key or mouse",
            },
            "get_left_again": {
                "func": self._get_left_again,
                "text": "Hit left hand drum pad, key or mouse again",
            },
            "get_right": {
                "func": self._get_right,
                "text": "Hit right hand drum pad, key or mouse",
            },
            "get_right_again": {
                "func": self._get_right_again,
                "text": "Hit right hand drum pad, key or mouse again",
            },
            "any_to_start": {
                "func": self._any_to_start,
                "text": "Success, hit ANY drum pad, key or mouse to begin",
            },
        }
        self._initialize_state = "get_left"
        self._midi_events = []
        self._key_events = []
        self._mouse_events = []
        self._trigger = {
            "left": {"type": None, "trigger": None},
            "right": {"type": None, "trigger": None},
        }
        self._countdown_finished = False
        self.countdown_time = 3
        self.prev_cntdwn_time = 4
        self._which_trigger = None
