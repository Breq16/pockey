from adafruit_neotrellis.neotrellis import NeoTrellis


class Trellis:
    def __init__(self, i2c, button_callback):
        self.trellis = NeoTrellis(i2c)
        self.trellis.pixels.auto_write = False

        def handle_trellis_button(event):
            button_callback(
                number=event.number,
                edge=(event.edge == NeoTrellis.EDGE_RISING)
            )

        for i in range(16):
            self.trellis.activate_key(i, NeoTrellis.EDGE_RISING)
            self.trellis.activate_key(i, NeoTrellis.EDGE_FALLING)
            self.trellis.callbacks[i] = handle_trellis_button

        self.virtual = [(0, 0, 0) for _ in range(16)]
        self.actual = [(0, 0, 0) for _ in range(16)]
        self.sync()

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
