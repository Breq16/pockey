from pockey.app import App


class Menu(App):
    BUTTON_SCROLL_LEFT = 0
    BUTTON_SCROLL_RIGHT = 3
    BUTTON_CONFIRM = 2

    def setup(self):
        self.pockey.text.enabled = True

        self.pockey.text[0] = "Main Menu"

        self.apps = list(self.pockey.apps.keys())

        self.app_index = 0

        self.pockey.trellis[self.BUTTON_SCROLL_LEFT] = (255, 255, 255)
        self.pockey.trellis[self.BUTTON_SCROLL_RIGHT] = (255, 255, 255)
        self.pockey.trellis[self.BUTTON_CONFIRM] = (0, 255, 0)

        self.pockey.text[1] = self.apps[self.app_index]

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

        self.pockey.text[1] = self.apps[self.app_index]


app = Menu
