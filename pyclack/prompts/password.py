from pyclack.utils import *
from pyclack.prompt import Prompt

class Password(Prompt):
    def __init__(self, question, placeholder="", mask_char='•', validators=None):
        super().__init__()
        self.question = question
        self.response = ""
        self.placeholder = placeholder
        self.mask_char = mask_char
        self.validators = validators

    def display(self):
        print(CURSOR_DOWN + CLEAR + CURSOR_UP + CLEAR, end='\r')
        masked_value = self.mask_char * len(self.response)
        display_text = masked_value if masked_value else f"{self.theme.secondary_color}{self.placeholder}{Colors.reset}"
        print(f"{self.theme.bar_color}{SymbolSet.bar}{Colors.reset}  {display_text}", end='\r')
        print(CURSOR_DOWN, end='\r')
        print(f"{self.theme.bar_color}{SymbolSet.bar_end} ", end='\r')
        print(CURSOR_UP, end='\r')

    def prompt(self, is_last=False):
        self.display_question(self.question, [self.theme.default_color, SymbolSet.step_active, self.theme.bar_color])
        self.display()
        while True:
            key = readchar.readkey()
            if key == readchar.key.BACKSPACE:
                self.response = self.response[:-1]
            elif key == readchar.key.ENTER:
                self.prompt_reponse_raw(self.response)
                is_valid, error_message = self.validate(self.validators, self.response)
                if not is_valid:
                    self.display_question(self.question, [self.theme.error_color, SymbolSet.step_error, self.theme.error_color], update={"code": 1, "message": error_message})
                    continue
                self.display_question(self.question, [self.theme.default_color, SymbolSet.step_active, self.theme.bar_color], update={"code": 2, "message": ""})
                print(f"{CURSOR_DOWN}{self.theme.bar_color}{SymbolSet.bar}")
                if is_last:
                    self.display_outro()
                return self.response
            elif len(key) == 1:
                if not self.response:  # Clear placeholder on first key press
                    self.response = key
                else:
                    self.response += key
            self.display()
