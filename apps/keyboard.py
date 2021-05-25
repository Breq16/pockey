import usb_hid
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS
from adafruit_hid.keycode import Keycode


from pockey.app import App


class KeyboardApp(App):
    def __init__(self, pockey):
        super().__init__(pockey)

        self.keyboard = Keyboard(usb_hid.devices)
        self.layout = KeyboardLayoutUS(self.keyboard)

        self.mapping = {
            0: "Hello World!",
            1: "https://google.com/\n",
            'A': "Hello hello!"
        }

    def setup(self):
        self.pockey.text.enabled = True

        self.pockey.text[0] = "Keyboard Demo"

        self.pockey.trellis[0] = (255, 255, 255)
        self.pockey.trellis[1] = (255, 255, 255)

    def handle_button(self, number, edge):
        if edge == self.pockey.PRESSED:
            if number in self.mapping:
                self.layout.write(self.mapping[number])

    def mainloop(self):
        pass

    def teardown(self):
        self.keyboard.release_all()


app = KeyboardApp