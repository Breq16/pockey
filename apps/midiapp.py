import usb_midi
import adafruit_midi
from adafruit_midi.control_change import ControlChange
from adafruit_midi.note_off import NoteOff
from adafruit_midi.note_on import NoteOn
from adafruit_midi.pitch_bend import PitchBend
import adafruit_imageload
from adafruit_display_text import bitmap_label as label
import displayio
import terminalio
import math

from pockey.app import App


truncate = lambda s, x: s[:x] if len(s) > x else s

def increment(value, mapping, offset):
    keys = list(mapping)

    index = keys.index(value)
    index += offset

    while index >= len(keys):
        index -= len(keys)

    while index < 0:
        index += len(keys)

    return keys[index]


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

    KEYS_ORDER = ["C", "G", "D", "A", "E", "B", "F#", "Db", "Ab", "Eb", "Bb", "F"]

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

    BTN_MODES = [
        "octave",
        "pitch bend",
    ]

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
        self.button_mode = "octave"

        self.bend_target = 8192
        self.bend = 8192

        self.button_state = [False for _ in range(16)]

        bitmap, palette = adafruit_imageload.load(
            "bmp/midi-menu.bmp",
            bitmap=displayio.Bitmap,
            palette=displayio.Palette
        )

        self.tile_grid = displayio.TileGrid(
            bitmap,
            pixel_shader=palette
        )

        self.menu_group = displayio.Group()
        self.menu_group.append(self.tile_grid)

        self.key_label = label.Label(
            font=terminalio.FONT, color=0xFFFFFF, x=42, y=36
        )
        self.menu_group.append(self.key_label)

        self.scale_label = label.Label(
            font=terminalio.FONT, color=0xFFFFFF, x=70, y=36
        )
        self.menu_group.append(self.scale_label)

        self.button_label = label.Label(
            font=terminalio.FONT, color=0xFFFFFF, x=104, y=36
        )
        self.menu_group.append(self.button_label)

        self.pockey.canvas.append(self.menu_group)

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
            self.pockey.trellis.clear()

            self.pockey.trellis[0, 0] = (255, 0, 0)

            for row in range(2):
                self.pockey.trellis[row, 1] = (0, 255, 255)
                self.pockey.trellis[row, 2] = (0, 255, 0)
                self.pockey.trellis[row, 3] = (0, 0, 255)

            self.menu_group.hidden = False

            self.key_label.text = self.key
            self.scale_label.text = truncate(self.scale, 4)
            self.button_label.text = truncate(self.button_mode, 3)

        else:
            self.menu_group.hidden = True
            self.pockey.text[1] = f"Octave {self.octave}"

            self.draw_pixels()

            for i, button in enumerate(self.button_state):
                if button:
                    self.pockey.trellis[i] = (0, 255, 0)

            if self.bend != self.bend_target:
                increment = int(math.copysign(800, self.bend_target - self.bend))
                if increment > self.bend_target - self.bend:
                    increment = self.bend_target - self.bend

                self.bend += increment

            message = PitchBend(self.bend)
            self.midi.send(message)

    def handle_button(self, number, edge):
        if isinstance(number, str):  # Display Buttons
            if number == "C":  # Toggle Menu
                if edge != self.pockey.RELEASED:
                    return

                self.menu_open = not self.menu_open

            if self.button_mode == "octave":
                if edge != self.pockey.RELEASED:
                    return

                if number == "A":  # Octave Up
                    self.octave += 1
                    if self.octave > 8:
                        self.octave = 8
                elif number == "B":  # Octave Down
                    self.octave -= 1
                    if self.octave < -1:
                        self.octave = -1

                self.pockey.request_display_update = True

            if self.button_mode == "pitch bend":
                if number == "A":
                    if edge == self.pockey.PRESSED:
                        self.bend_target += 8191
                    else:
                        self.bend_target -= 8191

                if number == "B":
                    if edge == self.pockey.PRESSED:
                        self.bend_target -= 8191
                    else:
                        self.bend_target += 8191


        elif self.menu_open:  # Menu
            if edge != self.pockey.RELEASED:
                return

            self.pockey.request_display_update = True

            if number == 0:
                self.pockey.load_app(self.pockey.HOME_APP)

            if number == 1:
                self.key = increment(self.key, self.KEYS_ORDER, 1)
            if number == 5:
                self.key = increment(self.key, self.KEYS_ORDER, -1)

            if number == 2:
                self.scale = increment(self.scale, self.SCALES, 1)
            if number == 6:
                self.scale = increment(self.scale, self.SCALES, -1)

            if number == 3:
                self.button_mode = increment(
                    self.button_mode, self.BTN_MODES, 1)
            if number == 7:
                self.button_mode = increment(
                    self.button_mode, self.BTN_MODES, -1)

        else:  # Normal Operation
            self.button_state[number] = (edge == self.pockey.PRESSED)

            message_type = NoteOn if edge == self.pockey.PRESSED else NoteOff
            note_number = self.SCALES[self.scale]["offsets"][number]
            note_number += (self.octave + 2) * 12
            message = message_type(note_number, 127)
            self.midi.send(message)

app = MidiApp