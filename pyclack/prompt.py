from .utils import *
from .themes import *
import signal, sys

# a bit of a mess :)
class Prompt:
    def __init__(self):
        print('\033[?25l', end="") # Hide cursor
        self.tite = ""
        self.outro_msg = "Bye!"
        self.prompts = {}
        self.form_results = {}
        self.theme = Theme.DARK_MODE.value

    def set_theme(self, theme_name):
        if theme_name in Theme.__members__:
            self.theme = Theme[theme_name].value
        else:
            raise ValueError(f"Unknown theme: {theme_name}")

    def group(self, prompts_dict, **event_listeners):
        self.prompt_generators = prompts_dict
        self.event_handlers = {event: handler for event, handler in event_listeners.items() if event in PROMPT_EVENT_LISTENERS}
        # Registering event handlers
        if 'on_cancel' in self.event_handlers:
            def on_cancel_wrapper(signum, frame):
                self.event_handlers['on_cancel']()
                self.on_cancel()
            signal.signal(signal.SIGINT, on_cancel_wrapper)

    def prompt(self):
        self.display_intro_title()
        for key, prompt_generator in self.prompt_generators.items():
            # Generate the prompt instance here, with access to previous responses
            prompt_instance = prompt_generator(self.form_results)
            if prompt_instance != None:
                response = prompt_instance.prompt()
                self.form_results[key] = response
        if hasattr(self, 'is_note_set'):
            self.display_note()
        self.display_outro()

    def prompt_reponse_raw(self, raw_input):
        if isinstance(raw_input, list):
            self.len_input = len(raw_input)
        else:
            self.len_input = len(raw_input.split('\n'))

    def validate(self, validators, response):
        if not isinstance(validators, list):
            validators = [validators]

        for validator in validators:
            is_valid, error_message = validator(response)
            if not is_valid:
                return False, error_message

        return True, ""

    def strip(self, text):
        """Remove ANSI escape sequences for accurate length calculation."""
        return re.sub(r'\x1B[@-_][0-?]*[ -/]*[@-~]', '', text)

    def display_question(self, question, options, update={"code": 0, "message": ""}):
        if update["code"] == 1 or update["code"] == 2:
            print(CLEAR_LINE, end='\r')
        print(f"{options[0]}{options[1]}{Colors.reset}  {question}")
        print(f"{options[2]}{SymbolSet.bar} ", end='\r')

        match update["code"]:
            case 1: # error occurred
                print(CURSOR_DOWN * (self.len_input), end='')
                print(f"{self.theme.error_color}{SymbolSet.bar_end}  {update['message']} {Colors.reset}")
                print(CURSOR_UP * (self.len_input + 1), end='')
            case 2: # text based input submitted
                print((CURSOR_UP * self.len_input) + CLEAR, end='')
                print(f"{options[0]}{SymbolSet.step_submit}{Colors.reset}  {question}")
            case 3: # selection based input submitted
                print("\033[K", end='\r') # clean the question line
                print(f"{options[0]}{SymbolSet.step_submit}{Colors.reset}  {question}")
            case 4:
                print("\033[K", end='\r') # clean the question line


    def display_formatted_response(self, input_response):
        print(CURSOR_UP * self.len_input, end='\r')
        print(CLEAR, end='\r')
        print(f"{self.theme.bar_color}{SymbolSet.bar_end}{Colors.reset}  {input_response}")

    def intro(self, msg):
        self.title = msg
    def display_intro_title(self):
        clear_command = 'cls' if os.name == 'nt' else 'clear'
        os.system(clear_command)
        print(f"{self.theme.bar_color}{SymbolSet.bar_start}{Colors.reset} {Colors.cyan}{self.theme.title_color} {self.title} {Colors.reset}\n{self.theme.bar_color}{SymbolSet.bar}{Colors.reset}")

    def outro(self, msg='', disabled=False):
        if disabled:
            self.outro_msg = None
        self.outro_msg = msg
    def display_outro(self):
        if self.outro_msg == None: return
        print(f"{self.theme.bar_color}{SymbolSet.bar_end}{Colors.reset}  {self.theme.outro_color}{self.outro_msg}")
        print('\033[?25h', end="")  # Show cursor

    def note(self, title, message):
        self.is_note_set = True
        self.note_title = title
        self.note_message = message
    def display_note(self):
        if self.note_title is None or self.note_message is None:  return
        title, message = self.note_title, self.note_message
        lines = f"\n{message}\n".split('\n')
        title_len = len(self.strip(title))
        max_len = max(max(len(self.strip(ln)) for ln in lines), title_len) + 2
        formatted_lines = [
            f"{self.theme.bar_color}{SymbolSet.bar}  {ln}{' ' * (max_len - len(self.strip(ln)))}{self.theme.bar_color}{SymbolSet.bar}"
            for ln in lines
        ]
        note_display = "\n".join(formatted_lines)
        print(
            f"{self.theme.bar_color}{SymbolSet.bar}\n{Colors.white}{SymbolSet.info}  {Colors.reset}{title} {self.theme.bar_color}"
            f"{SymbolSet.bar_h * max(max_len - title_len - 1, 1)}{SymbolSet.corner_top_right}\n{note_display}\n"
            f"{self.theme.bar_color}{SymbolSet.connect_left}{SymbolSet.bar_h * (max_len + 2)}{SymbolSet.corner_bottom_right}\n",
            end="\r"
        )

    def skip(self): return None

    def link(self, url, label=None, options={"color": Colors.cyan, "bg_color": None}):
        if options["color"] is None: options["color"] = ""
        if label is None: label = url
        parameters = ''
        escape_mask = '\033]8;{};{}\033\\{}\033]8;;\033\\' #
        return f"{options['color']}{escape_mask.format(parameters, url, label)}{Colors.reset}"

    # event listeners
    def on_cancel(self):
        print(CURSOR_DOWN, end='\r')
        self.display_outro()
        print('\033[?25h', end="")  # Show cursor
        sys.exit(0)

    @staticmethod
    def validator(validator_func):
        def wrapper(*args, **kwargs):
            result = validator_func(*args, **kwargs)
            if isinstance(result, tuple) and len(result) == 2:
                return result
            if isinstance(result, tuple) and result[0] is False:
                return result
            if result is False:
                return False, "Invalid input"
            return True, ""
        return wrapper
