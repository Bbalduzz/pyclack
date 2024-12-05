from pyclack.utils import *
from pyclack.prompt import Prompt

class Text(Prompt):
    def __init__(self, question, placeholder="", validators=None):
        super().__init__()
        self.response = ""
        self.question = question
        self.placeholder = placeholder
        self.validators = validators

    def display(self):
        print(CURSOR_DOWN + CLEAR + CURSOR_UP + CLEAR, end='\r')
        display_text = self.response if self.response else f"{self.theme.secondary_color}{self.placeholder}{Colors.reset}"
        print(f"{self.theme.bar_color}{SymbolSet.bar}{Colors.reset}  {display_text}", end='\r')
        print(CURSOR_DOWN, end='\r')
        print(f"{self.theme.bar_color}{SymbolSet.bar_end} ", end='\r')
        print(CURSOR_UP, end='\r')

    def prompt(self, isLast=False):
        self.display_question(self.question, [self.theme.default_color, SymbolSet.step_active, self.theme.bar_color])
        self.display()
        while True:
            key = readchar.readkey()
            if key == readchar.key.BACKSPACE:
                self.response = self.response[:-1]
            elif key == readchar.key.ENTER:
                if not self.response:
                    self.response = self.placeholder
                self.prompt_reponse_raw(self.response)
                is_valid, error_message = self.validate(self.validators, self.response)
                if not is_valid:
                    self.display_question(self.question, [self.theme.error_color, SymbolSet.step_error, self.theme.error_color], update={"code": 1, "message": error_message})
                    continue
                self.display_question(self.question, [self.theme.default_color, SymbolSet.step_active, self.theme.bar_color], update={"code": 2, "message": ""})
                print(f"{CURSOR_DOWN}{self.theme.bar_color}{SymbolSet.bar}")
                if isLast:
                    self.display_outro()
                return self.response
            else:
                if not self.response:  # Clear placeholder on first key press
                    self.response = key
                else:
                    self.response += key
            self.display()

class DinamicText(Prompt):
    def __init__(self, question, placeholder="", validators=None):
        super().__init__()
        self.response = ""
        self.question = question
        self.placeholder = placeholder
        self.validators = validators

    def display(self):
        # Clears the display and then shows the current input status
        print(CURSOR_DOWN + CLEAR + CURSOR_UP + CLEAR, end='\r')
        display_text = self.response if self.response else f"{self.theme.secondary_color}{self.placeholder}{Colors.reset}"
        print(f"{self.theme.bar_color}{SymbolSet.bar}{Colors.reset}  {display_text}", end='\r')
        print(CURSOR_DOWN, end='\r')
        print(f"{self.theme.bar_color}{SymbolSet.bar_end} ", end='\r')
        print(CURSOR_UP, end='\r')

    def display_question_with_response(self):
        # Updated method to show the question with the current response
        print(CURSOR_UP, end='\r')
        dynamic_question = f"{self.question}: {self.response or self.placeholder}"
        self.display_question(dynamic_question, [self.theme.default_color, SymbolSet.step_active, self.theme.bar_color])

    def prompt(self, isLast=False):
        self.display_question_with_response()
        self.display()
        while True:
            key = readchar.readkey()
            if key == readchar.key.BACKSPACE:
                self.response = self.response[:-1]
            elif key == readchar.key.ENTER:
                if not self.response:
                    self.response = self.placeholder
                if self.validators:
                    is_valid, error_message = self.validate(self.validators, self.response)
                    if not is_valid:
                        self.display_question(self.question, [self.theme.error_color, SymbolSet.step_error, self.theme.error_color], update={"code": 1, "message": error_message})
                        continue
                self.display_question_with_response()
                print(CURSOR_DOWN, end='\r')
                if isLast:
                    self.display_outro()
                return self.response
            else:
                if not self.response:  # Clear placeholder on first key press
                    self.response = key
                else:
                    self.response += key
            self.display_question_with_response()
            # self.display()
