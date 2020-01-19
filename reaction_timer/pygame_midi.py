import logging
import pygame.midi

LOG = logging.getLogger(__name__)
LOG.setLevel(logging.INFO)


class PygameMidi(object):
    def __init__(self, midi_device_id=None):
        LOG.info("initializing PygameMidi")
        pygame.midi.init()

        self.device_id = pygame.midi.get_default_input_id()
        self.has_midi = self.device_id != -1
        LOG.info(f"default midi input id: {self.device_id}")
        LOG.debug(f"midi device count: {pygame.midi.get_count()}")
        if midi_device_id:
            LOG.info(f"midi device id overridden to {midi_device_id}")
            self.device_id = midi_device_id

        if self.has_midi:
            LOG.debug(f"opened midi device")
            try:
                self.midi_device = pygame.midi.Input(self.device_id)
            except pygame.midi.MidiException as exception:
                LOG.error(f"failed to open midi device: {exception}")
                self.has_midi = False
        else:
            LOG.info(f"no midi device available!")

    def get_event_from_event_loop(self):
        if self.has_midi:
            while self.midi_device.poll():
                # get event data from event
                event = self.midi_device.read(1)[0][0]
                LOG.debug(event)
                LOG.debug(f"midi message: {list(hex(i) for i in event)}")
                # filter out Note ON messages:
                if event[0] >= 0x90 and event[0] <= 0x9F:
                    LOG.info(f"Note ON event with key: {hex(event[1])}")
                    yield event[1]
        return None
