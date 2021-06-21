from app import App


class HelloWorld(App):
    def setup(self):
        self.pockey.text.enabled = True

        self.pockey.text[0] = "Hello World!"

        self.frame_count = 0
        self.button_state = [False for _ in range(16)]

    def handle_button(self, number, edge):
        if edge == self.pockey.PRESSED:
            self.pockey.text[1] = f"Button pressed: {number}"
        else:
            self.pockey.text[2] = f"Button released: {number}"

        if isinstance(number, int):
            self.button_state[number] = (edge == self.pockey.PRESSED)

        self.pockey.request_display_update = True

    def mainloop(self):
        if self.frame_count % 5 == 0:
            if self.frame_count % 120 < 60:
                self.pockey.text[0] = f"Hello World! {self.frame_count}"
            else:
                self.pockey.text[0] = f"Pockey Test App {self.frame_count}"

            self.pockey.request_display_update = True

        self.pockey.trellis.clear()

        for button in range(16):
            if self.button_state[button]:
                self.light_up_cross(button)

        self.frame_count += 1

    def light_up_cross(self, number):
        row = number // 4
        for column in range(4):
            self.pockey.trellis[row, column] = (255, 0, 255)

        column = number % 4
        for row in range(4):
            self.pockey.trellis[row, column] = (255, 255, 0)

        self.pockey.trellis[number // 4, number % 4] = (255, 255, 255)


app = HelloWorld