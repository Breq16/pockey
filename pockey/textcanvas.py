import displayio
import terminalio

from adafruit_display_text import bitmap_label

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
