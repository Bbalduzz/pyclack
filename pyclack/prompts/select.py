from pyclack.utils import *
from pyclack.prompt import Prompt

class Select(Prompt):
    def __init__(self, question, options, initial_value=None, cursor_at=None, max_items=None):
        super().__init__()
        self.question = question
        self.options = options
        self.cursor = next((i for i, option in enumerate(options) if option['value'] == cursor_at), 0) if cursor_at is not None else 0
        self.max_items = max_items if max_items and max_items < len(options) else len(options)

        if initial_value is not None:
            for i, option in enumerate(self.options):
                if option['value'] == initial_value:
                    self.cursor = i
                    break

        self.selected_value = self.options[self.cursor]['value']

    def clear_options(self):
        # Calculate the number of lines to clear
        lines_to_clear = self.max_items
        if self.get_display_range()[0] > 0:
            lines_to_clear += 1  # For the upper ellipsis
        if self.get_display_range()[1] < len(self.options):
            lines_to_clear += 1  # For the lower ellipsis

        print(CLEAR_LINE * lines_to_clear, end='\r')
        print(CURSOR_UP, end='')

    def get_display_range(self):
        start = max(0, min(self.cursor - self.max_items // 2, len(self.options) - self.max_items))
        end = min(len(self.options), start + self.max_items)
        return start, end

    def update_display(self):
        start, end = self.get_display_range()
        lines_to_clear = self.max_items
        if start > 0: lines_to_clear += 1
        if end < len(self.options): lines_to_clear += 1
        print(CLEAR_LINE * lines_to_clear, end='\r')
        self.display()

    def display(self):
        start, end = self.get_display_range()
        if start > 0:
            print(f"{self.theme.bar_color}{SymbolSet.bar}   ...")
        for idx in range(start, end):
            option = self.options[idx]
            cursor = f"{SymbolSet.cursor} " if idx == self.cursor else "  "
            selected_color = self.theme.text_color if idx == self.cursor else self.theme.secondary_color
            hint = f" {self.theme.secondary_color}({option['hint']})" if idx == self.cursor and option.get('hint') else ""
            print(f"{self.theme.bar_color}{SymbolSet.bar}{Colors.reset}   {self.theme.cursor_color}{cursor}{selected_color}{option['label']}{hint}{Colors.reset}")
        if end < len(self.options):
            print(f"{self.theme.bar_color}{SymbolSet.bar}   ...")
        print(f"{self.theme.bar_color}{SymbolSet.bar_end} ", end='\r')


    def prompt(self, isLast=False):
        self.display_question(self.question, [self.theme.default_color, SymbolSet.step_active, self.theme.bar_color])
        if self.max_items < len(self.options):
            print(f"{self.theme.bar_color}{SymbolSet.bar}")
        self.display()
        while True:
            k = readchar.readkey()
            if k in [readchar.key.UP, 'k', readchar.key.LEFT, 'h']:  # 'k' and 'h' for vim-like controls
                self.cursor = (self.cursor - 1) % len(self.options)
            elif k in [readchar.key.DOWN, 'j', readchar.key.RIGHT, 'l']:  # 'j' and 'l' for vim-like controls
                self.cursor = (self.cursor + 1) % len(self.options)
            elif k == readchar.key.ENTER:
                self.clear_options()
                self.selected_value = self.options[self.cursor]['value']
                self.response = self.selected_value
                print(f"   {', '.join([opt['label'] for opt in self.options if opt['value'] in self.response])}")
                print(CURSOR_UP * 2, end='')
                self.display_question(self.question, [self.theme.default_color, SymbolSet.step_submit, self.theme.bar_color])
                print(f"{CURSOR_DOWN}{self.theme.bar_color}{SymbolSet.bar}")
                if isLast:
                    self.display_outro()
                return self.response
            elif k in [readchar.key.CTRL_C, readchar.key.ESC]:
                sys.exit(0)

            self.update_display()
