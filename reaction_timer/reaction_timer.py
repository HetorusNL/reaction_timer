import logging
import random
import time

from .pygame_audio import PygameAudio
from .pygame_visual import PygameVisual


LOG = logging.getLogger(__name__)
LOG.setLevel(logging.DEBUG)


class ReactionTimer(object):
    def __init__(self):
        logging.info("initializing ReactionTimer")
        self.running = True
        self.rt_time = 0
        self.next_trigger = 0
        self.trigger_time = 0  # make sure that trigger_time is smaller
        self.strike_time = 1  # make sure that strike_time is larger
        self.triggered = False

        # first initialize PygameAudio and then PygameVisual!
        self.pygame_audio = PygameAudio()
        self.pygame_visual = PygameVisual(self.pygame_audio, midi_device_id=3)

    def run(self):
        logging.info("starting ReactionTimer run loop")
        self.rt_time = time.time()
        while self.running:
            self._update_loop()

    def _update_loop(self):
        # process timing stuff
        current_time = time.time()
        time_delta = current_time - self.rt_time
        self.rt_time = current_time

        # process the event loop
        result = self.pygame_visual.process_event_loop()
        if result.get("shutdown"):
            logging.info("shutting down...")
            self.running = False
        if result.get("strike"):
            if self.triggered:
                self._strike()

        # make sure that the initialization of pygame_visual
        if not self.pygame_visual.initialize_finished():
            if not self.pygame_visual.run_initialize():
                return

        # make sure that the countdown of pygame_visual is finished
        if not self.pygame_visual.countdown_finished():
            if not self.pygame_visual.run_countdown(time_delta):
                return

        # make sure we have a trigger
        if self.next_trigger <= 0:
            # generate a new trigger in the interval [0.5, 5)
            self.next_trigger = random.random() * 4.5 + 0.5
            LOG.debug(f"generated next_trigger: {self.next_trigger}")

        # decrement the trigger and _trigger when <= 0
        self.next_trigger -= time_delta
        if self.next_trigger <= 0:
            self._trigger()

    def _trigger(self):
        logging.debug(f"triggered!")

        if self.triggered:
            logging.info("previous trigger missed!")
            return

        # store triggered and the trigger time
        self.trigger_time = time.time()
        self.triggered = True

        # set the left/right trigger in pygame_visual (pick one from set)
        which_trigger = ("left", "right")[random.randint(0, 1)]
        self.pygame_visual.set_trigger(which_trigger)

        # filling the screen with white
        self.pygame_visual.display_trigger((255, 255, 255))

        # add audible click (tick)
        self.pygame_audio.play_tick()

    def _strike(self):
        self.triggered = False
        self.strike_time = time.time()
        logging.info(f"strike after {self.strike_time-self.trigger_time}!")

        # add audible click (tock)
        self.pygame_audio.play_tock()

        # reset the screen to black
        self.pygame_visual.set_screen_color((0, 0, 0))
