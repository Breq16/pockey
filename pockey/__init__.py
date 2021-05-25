import os

import board
import displayio

import adafruit_displayio_sh1107

from pockey.button import Button
from pockey.textcanvas import TextCanvas
from pockey.trellis import Trellis


displayio.release_displays()


class Pockey:
    PRESSED = 1
    RELEASED = 0

    HOME_BUTTON = "C"
    HOME_APP = "menu"

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
        self.trellis = Trellis(
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
        if number == self.HOME_BUTTON:
            self.load_app(self.HOME_APP)
        elif self.current_app:
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
        self.load_app(self.HOME_APP)
        while True:
            self.run_app()

    def reset_context(self):
        self.text.enabled = False
        self.text.reset()
        self.trellis.clear()
        self.trellis.sync()
