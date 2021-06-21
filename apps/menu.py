import os

import terminalio
import displayio
import adafruit_imageload
from adafruit_display_text import label

from pockey.app import App


class Menu(App):
    BUTTON_SCROLL_LEFT = 0
    BUTTON_SCROLL_RIGHT = 3
    BUTTON_CONFIRM = 2

    def setup(self):
        bitmap, palette = adafruit_imageload.load(
            "bmp/menu.bmp",
            bitmap=displayio.Bitmap,
            palette=displayio.Palette
        )

        self.tile_grid = displayio.TileGrid(
            bitmap,
            pixel_shader=palette
        )

        self.pockey.canvas.append(self.tile_grid)

        self.apps = os.listdir("apps")

        for i, filename in enumerate(self.apps):
            if filename.endswith(".py"):
                self.apps[i] = filename[:-3]

        self.apps.remove("menu")

        self.app_index = 0

        self.pockey.trellis[self.BUTTON_SCROLL_LEFT] = (255, 255, 255)
        self.pockey.trellis[self.BUTTON_SCROLL_RIGHT] = (255, 255, 255)
        self.pockey.trellis[self.BUTTON_CONFIRM] = (0, 255, 0)

        self.text_area = label.Label(
            terminalio.FONT,
            text=self.apps[self.app_index],
            color=0xFFFFFF,
            x=16, y=24
        )
        self.pockey.canvas.append(self.text_area)

    def handle_button(self, number, edge):
        if edge != self.pockey.RELEASED:
            return

        if number == self.BUTTON_SCROLL_LEFT:
            self.app_index -= 1
            if self.app_index < 0:
                self.app_index = len(self.apps) - 1

        if number == self.BUTTON_SCROLL_RIGHT:
            self.app_index += 1
            if self.app_index >= len(self.apps):
                self.app_index = 0

        if number == self.BUTTON_CONFIRM:
            self.pockey.load_app(self.apps[self.app_index])

        self.text_area.text = self.apps[self.app_index]

        self.pockey.request_display_update = True


app = Menu
