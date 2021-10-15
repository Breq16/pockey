# Workaround for cyclic import
# https://stackoverflow.com/questions/39740632/
try:
    # TYPE_CHECKING is False at runtime
    from typing import TYPE_CHECKING
    if TYPE_CHECKING:
        from pockey import Pockey
except ImportError:
    # MicroPython / CircuitPython has no typing module
    pass


class App:
    TARGET_FPS = 5
    OVERRIDE_HOME = False

    def __init__(self, pockey: "Pockey"):
        self.pockey = pockey

    def setup(self):
        pass

    def mainloop(self):
        pass

    def teardown(self):
        pass

    def handle_button(self, number, edge):
        pass
