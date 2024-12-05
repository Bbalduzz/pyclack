from pyclack.utils import *
from pyclack.prompt import Prompt

class GroupMultiSelect(Prompt):
    def __init__(self, question, options, initial_values=None, cursor_at=None):
        super().__init__()
        self.question = question
        self.grouped_options = options
        self.options = self._flatten_options(options)
        self.selected_values = set(initial_values) if initial_values else set()
        self.cursor = 0
        if cursor_at is not None:
            self.cursor = next((i for i, option in enumerate(self.options) if option['value'] == cursor_at), 0)

    def _flatten_options(self, grouped_options):
        options = []
        for group, details in grouped_options.items():
            group_hint = details.get('hint', '')
            options.append({'value': group, 'label': group, 'is_group': True, **({'hint': group_hint} if group_hint else {})})
            items = details['items']
            options.extend([
                {'value': item['value'], 'label': item['label'], 'group': group, **({'hint': item['hint']} if 'hint' in item else {})}
                for item in items
            ])
        return options

    def clear_options(self, add=0):
        lines_to_clear = len(self.options) + add
        print(CLEAR_LINE * lines_to_clear, end='\r')

    def update_display(self):
        self.clear_options()
        self.display()

    def display(self):
        for idx, option in enumerate(self.options):
            selected = option['value'] in self.selected_values
            selected_color = self.theme.text_color if idx == self.cursor or selected else self.theme.secondary_color
            hint = f" {self.theme.secondary_color}({option['hint']})" if idx == self.cursor and option.get('hint') else ""
            checkmark = f"{self.theme.cursor_color}{SymbolSet.radio_inactive}{Colors.reset} " if idx == self.cursor else ( f"{SymbolSet.radio_active} " if selected else f"{self.theme.secondary_color}{SymbolSet.radio_inactive}{Colors.reset} ")
            group_prefix = "  " if option.get('is_group') else "    "
            print(f"{self.theme.bar_color}{SymbolSet.bar}{Colors.reset}{group_prefix} {checkmark}{selected_color}{option['label']}{hint}")
        print(f"{self.theme.bar_color}{SymbolSet.bar_end} ", end='\r')

    def toggle_current(self):
        current_option = self.options[self.cursor]
        if current_option.get('is_group'):
            group_values = [opt['value'] for opt in self.options if opt.get('group') == current_option['value']]
            if self.selected_values.intersection(group_values) == set(group_values):
                self.selected_values.difference_update(group_values)
            else:
                self.selected_values.update(group_values)
        else:
            current_value = current_option['value']
            if current_value in self.selected_values:
                self.selected_values.remove(current_value)
            else:
                self.selected_values.add(current_value)

    def prompt(self, isLast=False):
        self.display_question(self.question, [self.theme.default_color, SymbolSet.step_active, self.theme.bar_color])
        self.display()
        while True:
            k = readchar.readkey()
            if k == readchar.key.UP and self.cursor > 0:
                self.cursor -= 1
                self.update_display()
            elif k == readchar.key.DOWN and self.cursor < len(self.options) - 1:
                self.cursor += 1
                self.update_display()
            elif k == readchar.key.SPACE:
                self.toggle_current()
                self.update_display()
            elif k == readchar.key.ENTER:
                self.clear_options()
                self.response = list(self.selected_values)
                print(f"   {', '.join([opt['label'] for opt in self.options if opt['value'] in self.selected_values])}")
                print(CURSOR_UP * 2, end='')
                self.display_question(self.question, [self.theme.default_color, SymbolSet.step_submit, self.theme.bar_color])
                print(f"{CURSOR_DOWN}{self.theme.bar_color}{SymbolSet.bar}")
                if isLast:
                    self.display_outro()
                return self.response
            elif k == readchar.key.CTRL_C or k == readchar.key.ESC:
                sys.exit(0)
