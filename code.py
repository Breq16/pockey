import time

import board
import displayio
import terminalio

from adafruit_display_text import label
import adafruit_displayio_sh1107
from adafruit_neotrellis.neotrellis import NeoTrellis

displayio.release_displays()

i2c_bus = board.I2C()

trellis = NeoTrellis(i2c_bus)

display_bus = displayio.I2CDisplay(i2c_bus, device_address=0x3C)
display = adafruit_displayio_sh1107.SH1107(display_bus, width=128, height=64)
splash = displayio.Group()
display.show(splash)

# some color definitions
OFF = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 150, 0)
GREEN = (0, 255, 0)
CYAN = (0, 255, 255)
BLUE = (0, 0, 255)
PURPLE = (180, 0, 255)

def draw_text(text, x, y):
    splash.append(label.Label(terminalio.FONT, text=text, color=0xFFFFFF, x=x, y=y))

def make_callback(i):
    def blink(event):
        # turn the LED on when a rising edge is detected
        if event.edge == NeoTrellis.EDGE_RISING:
            trellis.pixels[event.number] = CYAN

            if len(splash):
                splash.pop()
            draw_text(f"Button {i} pressed", 8, 8)
        # turn the LED off when a rising edge is detected
        elif event.edge == NeoTrellis.EDGE_FALLING:
            trellis.pixels[event.number] = OFF

    return blink


for i in range(16):
    # activate rising edge events on all keys
    trellis.activate_key(i, NeoTrellis.EDGE_RISING)
    # activate falling edge events on all keys
    trellis.activate_key(i, NeoTrellis.EDGE_FALLING)
    # set all keys to trigger the blink callback
    trellis.callbacks[i] = make_callback(i)

    # cycle the LEDs on startup
    trellis.pixels[i] = PURPLE
    time.sleep(0.05)

for i in range(16):
    trellis.pixels[i] = OFF
    time.sleep(0.05)

while True:
    # call the sync function call any triggered callbacks
    trellis.sync()
    # the trellis can only be read every 17 millisecons or so
    time.sleep(0.02)
