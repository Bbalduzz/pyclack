from pyclack.utils import *
from pyclack.prompt import Prompt

class Confirm(Prompt):
    def __init__(self, question, active='Yes', inactive='No', initial_value=True):
        super().__init__()
        self.active = active
        self.inactive = inactive
        self.value = initial_value
        self.question = question

    def update_display(self):
        print(CLEAR_LINE , end='\r')
        self.display()

    def display(self):
        def format_radio_button(is_active, label):
            symbol = SymbolSet.radio_active if is_active else SymbolSet.radio_inactive
            label_color = self.theme.text_color if is_active else self.theme.secondary_color
            return f"{self.theme.cursor_color}{symbol}{Colors.reset}  {label_color}{label}{Colors.reset}"

        active_part = format_radio_button(self.value, self.active)
        inactive_part = format_radio_button(not self.value, self.inactive)
        print(f"{self.theme.bar_color}{SymbolSet.bar}{Colors.reset}  {active_part} / {inactive_part}\n", end='\r')
        print(f"{self.theme.bar_color}{SymbolSet.bar_end} ", end='\r')

    def prompt(self, isLast=False):
        self.display_question(self.question, [self.theme.default_color, SymbolSet.step_active, self.theme.bar_color])
        self.display()
        while True:
            key = readchar.readkey()
            if key == readchar.key.UP or key == readchar.key.DOWN:
                self.value = not self.value
            elif key == readchar.key.ENTER:
                print(CLEAR_LINE, end='\r')
                self.response = self.value
                selected_value = self.active if self.value else self.inactive
                print(f"   {self.active if self.response else self.inactive}")
                print(CURSOR_UP * 2, end='\r') # 2 is max number of lines that the Confirm prompt can take up
                self.display_question(self.question, [self.theme.default_color, SymbolSet.step_submit, self.theme.bar_color])
                if isLast:
                    self.display_outro()
                print(f"{CURSOR_DOWN}{self.theme.bar_color}{SymbolSet.bar}")
                return self.response
            self.update_display()
