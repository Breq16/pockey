import usb_midi
import adafruit_midi
from adafruit_midi.control_change import ControlChange
from adafruit_midi.note_off import NoteOff
from adafruit_midi.note_on import NoteOn
from adafruit_midi.pitch_bend import PitchBend

from pockey.app import App


class MidiApp(App):
    def __init__(self, pockey):
        super().__init__(pockey)

        self.midi = adafruit_midi.MIDI(
            midi_in=usb_midi.ports[0],
            in_channel=0,
            midi_out=usb_midi.ports[1],
            out_channel=0
        )

    def setup(self):
        self.pockey.text.enabled = True

        self.pockey.text[0] = "MIDI Test"
        self.octave = 1
        self.pockey.text[1] = f"Octave {self.octave}"

        self.notes = [
            "C{1}", "C#{1}", "D{1}", "D#{1}",
            "G#{0}", "A{0}", "A#{0}", "B{0}",
            "E{0}", "F{0}", "F#{0}", "G{0}",
            "C{0}", "C#{0}", "D{0}", "D#{0}",
        ]

        self.pixel_art = []
        for note in self.notes:
            if "#" in note:
                self.pixel_art.append((0, 0, 0))
            elif "C" in note:
                self.pixel_art.append((255, 255, 0))
            else:
                self.pixel_art.append((255, 0, 255))

        self.button_state = [False for _ in range(16)]

    def mainloop(self):
        self.pockey.text[1] = f"Octave {self.octave}"

        for i, pixel in enumerate(self.pixel_art):
            self.pockey.trellis[i] = pixel

        for i, button in enumerate(self.button_state):
            if button:
                self.pockey.trellis[i] = (0, 255, 0)

    def handle_button(self, number, edge):
        if isinstance(number, int):
            self.button_state[number] = (edge == self.pockey.PRESSED)

            message_type = NoteOn if edge == self.pockey.PRESSED else NoteOff
            note_number = self.notes[number].format(self.octave, self.octave + 1)
            message = message_type(note_number, 120)
            self.midi.send(message)
        else:
            if edge != self.pockey.RELEASED:
                return
            if number == "A":
                self.octave += 1
                if self.octave > 8:
                    self.octave = 8
            elif number == "B":
                self.octave -= 1
                if self.octave < -1:
                    self.octave = -1

app = MidiApp