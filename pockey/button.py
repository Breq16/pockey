import digitalio


class Button:
    def __init__(self, pin):
        self.io = digitalio.DigitalInOut(pin)
        self.io.direction = digitalio.Direction.INPUT
        self.io.pull = digitalio.Pull.UP

        self.previous_state = False

    def get_event(self):
        new_state = not self.io.value

        if (new_state and not self.previous_state):
            event = True
        elif (self.previous_state and not new_state):
            event = False
        else:
            event = None

        self.previous_state = new_state
        return event
