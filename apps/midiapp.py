import usb_midi
import adafruit_midi
from adafruit_midi.control_change import ControlChange
from adafruit_midi.note_off import NoteOff
from adafruit_midi.note_on import NoteOn
from adafruit_midi.pitch_bend import PitchBend

from pockey.app import App


class MidiApp(App):
    OVERRIDE_HOME = True

    COLOR_MAP = {
        0: (0, 0, 0),
        1: (255, 255, 0),
        2: (255, 0, 255)
    }

    SCALES = {
        "chromatic": {
            "offsets": [
                12, 13, 14, 15,
                8, 9, 10, 11,
                4, 5, 6, 7,
                0, 1, 2, 3
            ],
            "colors": [
                1, 0, 2, 0,
                0, 2, 0, 2,
                2, 2, 0, 2,
                1, 0, 2, 0
            ]
        },
        "major": {
            "offsets": [
                19, 21, 23, 24,
                12, 14, 16, 17,
                7, 9, 11, 12,
                0, 2, 4, 5
            ],
            "colors": [
                2, 0, 0, 1,
                1, 0, 2, 0,
                2, 0, 0, 1,
                1, 0, 2, 0
            ]
        },
        "minor": {
            "offsets": [
                19, 20, 22, 24,
                12, 14, 15, 17,
                7, 8, 10, 12,
                0, 2, 3, 5
            ],
            "colors": [
                2, 0, 0, 1,
                1, 0, 2, 0,
                2, 0, 0, 1,
                1, 0, 2, 0
            ]
        }
    }

    KEYS = {
        "C": 0,
        "G": -5,
        "D": 2,
        "A": -3,
        "E": 4,
        "B": -1,
        "F#": 6,
        "Db": 1,
        "Ab": -4,
        "Eb": 3,
        "Bb": -2,
        "F": 5
    }

    def __init__(self, pockey):
        super().__init__(pockey)

        self.midi = adafruit_midi.MIDI(
            midi_in=usb_midi.ports[0],
            in_channel=0,
            midi_out=usb_midi.ports[1],
            out_channel=0
        )

        self.menu_open = False
        self.scale = "major"
        self.key = "G"

        self.button_state = [False for _ in range(16)]

    def draw_pixels(self):
        for i, color in enumerate(self.SCALES[self.scale]["colors"]):
            self.pockey.trellis[i] = self.COLOR_MAP[color]

    def setup(self):
        self.pockey.text.enabled = True

        self.pockey.text[0] = "MIDI Test"
        self.octave = 1
        self.pockey.text[1] = f"Octave {self.octave}"

        self.draw_pixels()

    def mainloop(self):
        if self.menu_open:
            # Handle menu
            pass

        else:
            self.pockey.text[1] = f"Octave {self.octave}"

            self.draw_pixels()

            for i, button in enumerate(self.button_state):
                if button:
                    self.pockey.trellis[i] = (0, 255, 0)

    def handle_button(self, number, edge):
        if isinstance(number, str):  # Display Buttons
            if edge != self.pockey.RELEASED:
                return

            if number == "C":  # Toggle Menu
                self.menu_open = not self.menu_open

            elif number == "A":  # Octave Up
                self.octave += 1
                if self.octave > 8:
                    self.octave = 8
            elif number == "B":  # Octave Down
                self.octave -= 1
                if self.octave < -1:
                    self.octave = -1

        elif self.menu_open:  # Menu
            pass

        else:  # Normal Operation
            self.button_state[number] = (edge == self.pockey.PRESSED)

            message_type = NoteOn if edge == self.pockey.PRESSED else NoteOff
            note_number = self.SCALES[self.scale]["offsets"][number]
            note_number += (self.octave + 2) * 12
            message = message_type(note_number, 127)
            self.midi.send(message)

app = MidiApp