import os
import sys

import board
import displayio
import supervisor

import adafruit_displayio_sh1107

from pockey.app import App
from pockey.button import Button
from pockey.textcanvas import TextCanvas
from pockey.trellis import Trellis


displayio.release_displays()
supervisor.disable_autoreload()


class Pockey:
    PRESSED = 1
    RELEASED = 0

    HOME_BUTTON = "C"
    HOME_APP = "menu"

    def __init__(self):
        self.i2c = board.I2C()
        self.init_trellis()
        self.init_display()

        self.current_app_name = None
        self.current_app = None

    def init_trellis(self):
        self.trellis = Trellis(
            self.i2c, lambda number, edge: self.handle_button(number, edge))

    def init_display(self):
        self.display_bus = displayio.I2CDisplay(self.i2c, device_address=0x3C)
        self.display = adafruit_displayio_sh1107.SH1107(
            self.display_bus, width=128, height=64, auto_refresh=False)

        self.palette = displayio.Palette(2)
        self.palette[0] = 0x000000
        self.palette[1] = 0xFFFFFF

        self.display_buttons = []

        pins = {"A": board.D9, "B": board.D6, "C": board.D5}
        self.display_buttons = {letter: Button(pin) for letter, pin in pins.items()}
        self.reset_display()

    def reset_display(self):
        self.canvas = displayio.Group()
        self.text = TextCanvas(self.canvas)

        self.display.show(self.canvas)

    def scan_display_buttons(self):
        for letter, button in self.display_buttons.items():
            event = button.get_event()
            if event is not None:
                self.handle_button(number=letter, edge=event)

    def handle_button(self, number, edge):
        if not self.current_app:
            return

        if number == self.HOME_BUTTON and not self.current_app.OVERRIDE_HOME:
            self.load_app(self.HOME_APP)
        else:
            self.current_app.handle_button(number, edge)

    def load_app(self, app_name):
        self.current_app_name = app_name

    def run_app(self):
        app_name = self.current_app_name


        if f"apps.{app_name}" in sys.modules:
            del sys.modules[f"apps.{app_name}"]
        apps_module = __import__(f"apps.{app_name}")
        app_module = getattr(apps_module, app_name)
        app_class = getattr(app_module, "app")

        filename = app_module.__file__
        modify_date = os.stat(filename)[9]

        app: App = app_class(self)
        self.current_app = app

        app.setup()

        self.request_display_update = True

        while True:
            self.trellis.sync()

            app.mainloop()

            self.text.sync()

            if self.request_display_update:
                self.display.refresh(minimum_frames_per_second=0)
                self.request_display_update = False

            self.scan_display_buttons()

            if self.current_app_name != app_name:
                break

            if os.stat(filename)[9] > modify_date:
                break

        app.teardown()
        self.reset_context()

    def run(self):
        self.load_app(self.HOME_APP)
        while True:
            self.run_app()

    def reset_context(self):
        self.trellis.clear()
        self.trellis.sync()
        self.reset_display()
