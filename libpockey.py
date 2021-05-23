import os

import board
import displayio
import terminalio
import digitalio

from adafruit_display_text import bitmap_label
import adafruit_displayio_sh1107
from adafruit_neotrellis.neotrellis import NeoTrellis

displayio.release_displays()

class Button:
    def __init__(self, pin):
        self.io = digitalio.DigitalInOut(pin)
        self.io.direction = digitalio.Direction.INPUT
        self.io.pull = digitalio.Pull.UP

        self.previous_state = False

    def get_event(self):
        new_state = not self.io.value

        if (new_state and not self.previous_state):
            event = Pockey.PRESSED
        elif (self.previous_state and not new_state):
            event = Pockey.RELEASED
        else:
            event = None

        self.previous_state = new_state
        return event


class CachedTrellis:
    def __init__(self, i2c, button_callback):
        self.trellis = NeoTrellis(i2c)
        self.trellis.pixels.auto_write = False

        def handle_trellis_button(event):
            button_callback(
                number=event.number,
                edge=(Pockey.PRESSED if event.edge == NeoTrellis.EDGE_RISING
                      else Pockey.RELEASED)
            )

        for i in range(16):
            self.trellis.activate_key(i, NeoTrellis.EDGE_RISING)
            self.trellis.activate_key(i, NeoTrellis.EDGE_FALLING)
            self.trellis.callbacks[i] = handle_trellis_button

        self.virtual = [(0, 0, 0) for _ in range(16)]
        self.actual = [(0, 0, 0) for _ in range(16)]

    def sync(self):
        self.trellis.sync()

        virtual = self.virtual
        actual = self.actual

        dirty = False

        for pixel in range(16):
            if virtual[pixel] != actual[pixel]:
                self.trellis.pixels[pixel] = virtual[pixel]
                actual[pixel] = virtual[pixel]
                dirty = True

        if dirty:
            self.trellis.pixels.show()

    def _handle_index(self, index):
        if isinstance(index, int):
            return index
        elif len(index) == 2:
            # row and column access
            return index[0]*4 + index[1]

    def __getitem__(self, index):
        return self.virtual[self._handle_index(index)]

    def __setitem__(self, index, value):
        self.virtual[self._handle_index(index)] = value

    def clear(self):
        self.virtual = [(0, 0, 0) for _ in range(16)]


class TextCanvas:
    def __init__(self, parent):
        self.parent = parent
        self.group = displayio.Group()
        self.labels = [
            bitmap_label.Label(
                terminalio.FONT, color=0xFFFFFF, x=8, y=8 + 20*i
            ) for i in range(3)
        ]
        for label in self.labels:
            self.group.append(label)

        self.reset()
        self.enabled = False
        self.parent.append(self.group)

        self.virtual = ["", "", ""]
        self.actual = ["", "", ""]

    def reset(self):
        self.virtual = ["", "", ""]

    def sync(self):
        if self.enabled:
            for i in range(3):
                if self.virtual[i] != self.actual[i]:
                    self.put_text(i, self.virtual[i])
                    self.actual[i] = self.virtual[i]

    def put_text(self, i, text):
        self.labels[i]._reset_text(text=text)

    def __getitem__(self, index):
        return self.virtual[index]

    def __setitem__(self, index, value):
        self.virtual[index] = str(value)

    def _set_enabled(self, value):
        self.group.hidden = value
        if value:
            self.sync()

    def _get_enabled(self):
        return self.group.hidden

    enabled = property(_get_enabled, _set_enabled)

class Pockey:
    PRESSED = 1
    RELEASED = 0

    def __init__(self):
        self.i2c = board.I2C()
        self.init_trellis()
        self.init_display()

        self.apps = {}
        self.current_app_name = None
        self.current_app = None

        self.load_apps()

    def load_apps(self):
        apps = os.listdir("apps")

        for filename in apps:
            if filename.endswith(".py"):
                filename = filename[:-3]

            apps_module = __import__(f"apps.{filename}")
            app_module = getattr(apps_module, filename)
            app_class = getattr(app_module, "app")
            self.apps[filename] = app_class(self)

    def init_trellis(self):
        self.trellis = CachedTrellis(
            self.i2c, lambda number, edge: self.handle_button(number, edge))

    def init_display(self):
        self.display_bus = displayio.I2CDisplay(self.i2c, device_address=0x3C)
        self.display = adafruit_displayio_sh1107.SH1107(
            self.display_bus, width=128, height=64, auto_refresh=False)

        self.display_buttons = []

        pins = {"A": board.D9, "B": board.D6, "C": board.D5}
        self.display_buttons = {letter: Button(pin) for letter, pin in pins.items()}

        self.canvas = displayio.Group()
        self.text = TextCanvas(self.canvas)

        self.display.show(self.canvas)

    def scan_display_buttons(self):
        for letter, button in self.display_buttons.items():
            event = button.get_event()
            if event is not None:
                self.handle_button(number=letter, edge=event)

    def handle_button(self, number, edge):
        if self.current_app:
            self.current_app.handle_button(number, edge)

    def load_app(self, app_name):
        self.current_app_name = app_name

    def run_app(self):
        app_name = self.current_app_name
        app = self.apps[self.current_app_name]
        self.current_app = app

        app.setup()
        while self.current_app_name == app_name:
            app.mainloop()

            self.trellis.sync()
            self.text.sync()
            if not self.display.refresh(minimum_frames_per_second=0):
                print("FRAME DROP")
            self.scan_display_buttons()

        app.teardown()
        self.reset_context()

    def run(self):
        while True:
            self.run_app()

    def reset_context(self):
        self.text.enabled = False
        self.text.reset()
        self.trellis.clear()
        self.trellis.sync()
