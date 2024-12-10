import sys
import threading
import time
from utils.styling import Color, S_BAR, S_STEP_SUBMIT, S_STEP_CANCEL, S_STEP_ERROR, UNICODE

class Spinner:
    """Terminal spinner for loading states."""
    def __init__(self):
        self.frames = ['◒', '◐', '◓', '◑'] if UNICODE else ['•', 'o', 'O', '0']
        self.delay = 0.08 if UNICODE else 0.12
        self.active = False
        self.message = ''
        self._timer = None
        self._frame_index = 0

    def start(self, message: str = ''):
        """Start the spinner with an optional message."""
        self.message = message.rstrip('.')
        self.active = True
        
        def spin():
            while self.active:
                frame = Color.magenta(self.frames[self._frame_index])
                dots = '.' * (1 + (int(time.time() * 8) % 3))
                sys.stdout.write('\r\033[K' + f"{frame}  {self.message}{dots}")
                sys.stdout.flush()
                self._frame_index = (self._frame_index + 1) % len(self.frames)
                time.sleep(self.delay)

        self._timer = threading.Thread(target=spin)
        self._timer.daemon = True
        sys.stdout.write(f"{Color.gray(S_BAR)}\n")
        self._timer.start()

    def stop(self, message: str = None, code: int = 0):
        """Stop the spinner and show final message."""
        self.active = False
        if self._timer:
            self._timer.join()
        
        final_message = message or self.message
        step = (Color.green(S_STEP_SUBMIT) if code == 0 else 
                Color.red(S_STEP_CANCEL) if code == 1 else 
                Color.red(S_STEP_ERROR))
        
        sys.stdout.write('\r\033[K' + f"{step}  {final_message}\n")
        sys.stdout.flush()

    def update(self, message: str):
        """Update the spinner message."""
        self.message = message.rstrip('.')