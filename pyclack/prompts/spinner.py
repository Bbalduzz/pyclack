from pyclack.utils import *
from pyclack.prompt import Prompt
import sys
import time
import threading
import signal

class Spinner():
    def __init__(self, theme, unicode=True):
        self.theme = theme
        self.frames = ['◒', '◐', '◓', '◑'] if unicode else ['•', 'o', 'O', '0']
        self.delay = 0.08 if unicode else 0.12
        self.is_spinner_active = False
        self._message = ''
        self.loop = None
        self._lock = threading.Lock()  # Lock for synchronizing access to _message

    def _spinner_task(self, sub_indent):
        frame_index = 0
        while self.is_spinner_active:
            with self._lock:
                frame = self.frames[frame_index]
                message = self._message
            sys.stdout.write(f"{sub_indent}{self.theme.default_color}{frame}{Colors.reset}  {self.theme.text_color}{message}{Colors.reset}\r")
            sys.stdout.flush()
            frame_index = (frame_index + 1) % len(self.frames)
            time.sleep(self.delay)

    def start(self, message='', sub_indent=""):
        if self.is_spinner_active:  # Ensure starting on a new line if another spinner is active
            sys.stdout.write("\n")
        self.is_spinner_active = True
        with self._lock:
            self._message = message.rstrip('.')
        self.loop = threading.Thread(target=self._spinner_task, args=(sub_indent,))
        self.loop.start()
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

    def stop(self, message='', indent="", code=0):
        self.is_spinner_active = False
        if self.loop and self.loop.is_alive():
            self.loop.join()
        with self._lock:
            final_message = message or self._message
        step = '✓' if code == 0 else '✗'
        text_color = self.theme.text_color if indent == "" else self.theme.secondary_color
        sys.stdout.write(f"{indent}{self.theme.default_color}{step}{Colors.reset}  {text_color}{final_message}{Colors.reset}\n")
        sys.stdout.flush()

    def signal_handler(self, signum, frame):
        self.stop('Canceled', code=1)
        sys.exit(1)

    def update_message(self, message=''):
        with self._lock:
            self._message = message or self._message

class SpinnerGroup(Prompt):
    def __init__(self, spinners, message="Group Task Running...", finish_message="Group Task Completed"):
        super().__init__()
        self.spinners = [spinner for spinner in spinners if spinner is not None]
        self.message = message
        self.finish_message = finish_message

    def prompt(self, isLast=False):
        self.display_question(self.message, [self.theme.default_color, f"{SymbolSet.step_active}{self.theme.secondary_color}{SymbolSet.bar_h*2}", self.theme.bar_color])
        for i, spinner in enumerate(self.spinners, start=1):
            if (i == len(self.spinners)):  # Check if this spinner is the last
                spinner.prompt(isGroup=True, isLast=True)
            else: spinner.prompt(isGroup=True)
        self.display_question(self.finish_message, [self.theme.default_color, f"{SymbolSet.step_submit}{self.theme.secondary_color}{SymbolSet.bar_h*2}", self.theme.bar_color])
        if isLast:
            self.display_outro()


class Work(Prompt):
    def __init__(self, message, function, args=(), indent=4):
        super().__init__()
        self.message = message
        self.spinner = Spinner(self.theme)
        self.function = function
        self.args = args
        self.indent = indent  # Default indentation

    def message(self, message):
        self.spinner.update_message(message)

    def prompt(self, isGroup=False, isLast=False):
        indent_str = f"{self.theme.bar_color}{SymbolSet.bar}" + (" " * (int(self.indent)-1)) if isGroup else ""
        sub_indent = f"{indent_str}" if isGroup else ""
        self.spinner.start(self.message, sub_indent=sub_indent)
        try:
            result = self.function(*self.args)
            return result
        except Exception as e:
            self.spinner.stop(str(e), code=1)
            raise
        finally:
            if result is not None:
                if isGroup:
                    self.spinner.stop(f'{result}', indent=f'{self.theme.bar_color}{SymbolSet.bar}{(" " * (int(self.indent)-1))}', code=0)
                else:
                    self.spinner.stop(f'{result}', code=0)
                if not isLast and not isGroup:
                    print(f"{indent_str}{self.theme.bar_color}{SymbolSet.bar}")
