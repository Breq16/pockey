import time

import usb_hid
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS
from adafruit_hid.keycode import Keycode
import displayio
import adafruit_imageload

from pockey.app import App


class EmojiKeys(App):
    def __init__(self, pockey):
        super().__init__(pockey)

        self.keyboard = Keyboard(usb_hid.devices)
        self.layout = KeyboardLayoutUS(self.keyboard)

        self.emoji = [
            "😁",
            "😂",
            "😤",
            "🥰",

            "🤔",
            "🤯",
            "🥳",
            "😱",

            "👍",
            "💯",
            "✨",
            "❤️"[0], # Don't type the color character
        ]

        self.colors = [
            (255, 255, 0),
            (127, 127, 255),
            (255, 255, 255),
            (255, 127, 127),

            (127, 127, 0),
            (255, 127, 0),
            (0, 255, 0),
            (64, 64, 255),

            (255, 255, 64),
            (127, 0, 0),
            (255, 255, 192),
            (255, 64, 64)
        ]

    def setup(self):
        bitmap, palette = adafruit_imageload.load(
            "bmp/emoji.bmp",
            bitmap=displayio.Bitmap,
            palette=displayio.Palette
        )

        self.tile_grid = displayio.TileGrid(
            bitmap,
            pixel_shader=palette
        )

        for i, color in enumerate(self.colors):
            self.pockey.trellis[i] = color

        self.pockey.canvas.append(self.tile_grid)

    def type_emoji(self, emoji):
        # Open the characters popover
        self.keyboard.press(Keycode.CONTROL, Keycode.COMMAND, Keycode.SPACE)
        self.keyboard.release_all()
        time.sleep(0.2)

        # Type the unicode hex code point
        self.layout.write("u+" + hex(ord(emoji))[2:])
        time.sleep(0.3)

        # Press ENTER to select the first emoji in the list
        self.keyboard.press(Keycode.ENTER)
        self.keyboard.release_all()
        time.sleep(0.1)

        # Press ENTER to insert the emoji
        self.keyboard.press(Keycode.ENTER)
        self.keyboard.release_all()
        time.sleep(0.1)

    def handle_button(self, number, edge):
        if edge == self.pockey.PRESSED:
            if isinstance(number, int) and number < len(self.emoji):
                self.type_emoji(self.emoji[number])

    def mainloop(self):
        pass

    def teardown(self):
        self.keyboard.release_all()


app = EmojiKeys