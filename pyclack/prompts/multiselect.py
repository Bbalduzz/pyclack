from pyclack.utils import *
from pyclack.prompt import Prompt

class MultiSelect(Prompt):
    def __init__(self, question, options, initial_values=None, cursor_at=None, max_items=None, validators=None):
        super().__init__()
        self.question = question
        self.options = options
        self.validators = validators
        self.selected_values = set(initial_values) if initial_values else set()
        self.cursor = next((i for i, option in enumerate(options) if option['value'] == cursor_at), 0) if cursor_at is not None else 0
        self.max_items = max_items if max_items and max_items < len(options) else len(options)

    def clear_options(self):
        # Calculate the number of lines to clear
        lines_to_clear = self.max_items
        if self.get_display_range()[0] > 0:
            lines_to_clear += 1  # For the upper ellipsis
        if self.get_display_range()[1] < len(self.options):
            lines_to_clear += 1  # For the lower ellipsis

        print(CLEAR_LINE * lines_to_clear, end='\r')

    def get_display_range(self):
        start = max(0, min(self.cursor - self.max_items // 2, len(self.options) - self.max_items))
        end = min(len(self.options), start + self.max_items)
        return start, end

    def update_display(self):
        self.clear_options()
        self.display()

    def display(self, is_last=False):
        start, end = self.get_display_range()
        if start > 0:
            print(f"{self.theme.bar_color}{SymbolSet.bar}   ...")
        for idx in range(start, end):
            option = self.options[idx]
            selected = option['value'] in self.selected_values
            selected_color = self.theme.text_color if idx == self.cursor or selected else self.theme.secondary_color
            hint = f" {self.theme.secondary_color}({option['hint']})" if idx == self.cursor and option.get('hint') else ""
            checkmark = f"{self.theme.cursor_color}{SymbolSet.password_mask} " if idx == self.cursor else (f"{SymbolSet.checkbox_selected} " if selected else f"{self.theme.secondary_color}{SymbolSet.checkbox_active}{Colors.reset} ")
            print(f"{self.theme.bar_color}{SymbolSet.bar}{Colors.reset}   {Colors.white}{checkmark}{selected_color}{option['label']}{hint}")
        if end < len(self.options):
            print(f"{self.theme.bar_color}{SymbolSet.bar}   ...")
        print(f"{self.theme.bar_color}{SymbolSet.bar_end} ", end='\r')

    def toggle_current(self):
        current_value = self.options[self.cursor]['value']
        if current_value in self.selected_values:
            self.selected_values.remove(current_value)
        else:
            self.selected_values.add(current_value)

    def toggle_all(self):
        if len(self.selected_values) == len(self.options):
            self.selected_values.clear()
        else:
            self.selected_values = {option['value'] for option in self.options}

    def prompt(self, isLast=False):
        self.display_question(self.question, [self.theme.default_color, SymbolSet.step_active, self.theme.bar_color])
        if self.max_items < len(self.options):
            print(f"{self.theme.bar_color}{SymbolSet.bar}")
        self.display()
        while True:
            key = readchar.readkey()
            if key == readchar.key.UP and self.cursor > 0:
                self.cursor -= 1
            elif key == readchar.key.DOWN and self.cursor < len(self.options) - 1:
                self.cursor += 1
            elif key == readchar.key.SPACE:
                self.toggle_current()
            elif key.lower() == 'a':
                self.toggle_all()
            elif key == readchar.key.ENTER:
                self.clear_options()
                self.response = list(self.selected_values)
                print(f"   {', '.join([opt['label'] for opt in self.options if opt['value'] in self.response])}")
                print(CURSOR_UP * 2, end='')
                self.display_question(self.question, [self.theme.default_color, SymbolSet.step_submit, self.theme.bar_color])
                print(f"{CURSOR_DOWN}{self.theme.bar_color}{SymbolSet.bar}")
                if isLast:
                    self.display_outro()
                return self.response
            self.update_display()
