import sys
import shutil
import readchar
from typing import Any, Callable, Dict, List, Optional, Union

# Constants
CANCEL = object()  # Symbol equivalent
KEYS = {'up', 'down', 'left', 'right', 'space', 'enter'}
ALIASES = {
    'k': 'up',
    'j': 'down',
    'h': 'left',
    'l': 'right'
}

def is_cancel(value: Any) -> bool:
    return value is CANCEL

class Color:
    """Simple color handling class to mimic picocolors functionality."""
    @staticmethod
    def inverse(text: str) -> str:
        return f"\033[7m{text}\033[27m"
    
    @staticmethod
    def hidden(text: str) -> str:
        return f"\033[8m{text}\033[28m"

def wrap_ansi(text: str, width: int, hard: bool = False) -> str:
    """Simple text wrapping implementation."""
    lines = []
    for line in text.split('\n'):
        while len(line) > width:
            if hard:
                lines.append(line[:width])
                line = line[width:]
            else:
                space_index = line[:width].rfind(' ')
                if space_index == -1:
                    space_index = width
                lines.append(line[:space_index])
                line = line[space_index:].lstrip()
        lines.append(line)
    return '\n'.join(lines)

class Prompt:
    def __init__(
        self,
        render: Callable[['Prompt'], Optional[str]],
        placeholder: str = '',
        initial_value: Any = None,
        validate: Optional[Callable[[Any], Optional[str]]] = None,
        debug: bool = False,
        track_value: bool = True
    ):
        self._subscribers: Dict[str, List[dict]] = {}
        self.render_fn = render
        self.placeholder = placeholder
        self.initial_value = initial_value
        self.validate = validate
        self.debug = debug
        self._track = track_value
        
        # State
        self.state = 'initial'  # One of: initial, active, cancel, submit, error
        self.value = initial_value
        self.error = ''
        self._cursor = 0
        self._prev_frame = ''
        self._frame_lines = 0
        self._start_line = 0  # Track where our prompt starts
        
        # Terminal settings
        self.cols = shutil.get_terminal_size().columns

    def _save_cursor_position(self):
        """Save current cursor position."""
        sys.stdout.write('\033[s')

    def _restore_cursor_position(self):
        """Restore saved cursor position."""
        sys.stdout.write('\033[u')

    def _move_to_start(self):
        """Move cursor to start of prompt area."""
        if self._frame_lines > 0:
            sys.stdout.write(f"\033[{self._frame_lines}A")

    def _clear_lines(self, count: int):
        """Clear specified number of lines."""
        for _ in range(count):
            sys.stdout.write('\033[2K')  # Clear line
            sys.stdout.write('\033[1B')  # Move down
        sys.stdout.write(f"\033[{count}A")  # Move back up
    
    def on(self, event: str, callback: Callable[..., Any]) -> None:
        """Add an event listener."""
        if event not in self._subscribers:
            self._subscribers[event] = []
        self._subscribers[event].append({'cb': callback, 'once': False})
    
    def once(self, event: str, callback: Callable[..., Any]) -> None:
        """Add a one-time event listener."""
        if event not in self._subscribers:
            self._subscribers[event] = []
        self._subscribers[event].append({'cb': callback, 'once': True})
    
    def emit(self, event: str, *args: Any) -> None:
        """Emit an event to all listeners."""
        if event not in self._subscribers:
            return
            
        cleanup = []
        for sub in self._subscribers[event]:
            sub['cb'](*args)
            if sub['once']:
                cleanup.append(sub)
                
        for sub in cleanup:
            self._subscribers[event].remove(sub)
    
    def handle_key(self, key: str) -> bool:
        """Handle a keypress. Returns True if should continue, False if should exit."""
        if self.state == 'error':
            self.state = 'active'

        # Special key handling
        if key == readchar.key.CTRL_C:
            self.state = 'cancel'
            return False
            
        elif key == readchar.key.ENTER:
            if self.validate:
                problem = self.validate(self.value)
                if problem:
                    self.error = problem
                    self.state = 'error'
                    return True
            self.state = 'submit'
            return False
            
        # Handle navigation keys
        elif key in (readchar.key.UP, 'k'):
            self.emit('cursor', 'up')
        elif key in (readchar.key.DOWN, 'j'):
            self.emit('cursor', 'down')
        elif key in (readchar.key.LEFT, 'h'):
            self.emit('cursor', 'left')
        elif key in (readchar.key.RIGHT, 'l'):
            self.emit('cursor', 'right')
            
        # Handle regular input
        elif key == ' ':
            self.emit('cursor', 'space')
        elif key in 'yYnN':
            self.emit('confirm', key.lower() == 'y')
        elif key == '\t' and self.placeholder and not self.value:
            self.value = self.placeholder
            self._cursor = len(self.value)
            self.emit('value', self.value)
        
        if key and len(key) == 1:
            self.emit('key', key.lower())
            
        return True

    def render(self) -> None:
        """Render the current frame."""
        frame = wrap_ansi(self.render_fn(self) or '', self.cols, hard=True)
        if frame == self._prev_frame:
            return

        new_lines = frame.count('\n') + 1

        if self.state == 'initial':
            # First render - just write and track position
            sys.stdout.write('\033[?25l')  # Hide cursor
            self._save_cursor_position()  # Save starting position
            sys.stdout.write(frame)
        else:
            # Move to start of prompt area
            self._restore_cursor_position()
            # Clear prompt area
            self._clear_lines(self._frame_lines)
            # Write new frame
            sys.stdout.write(frame)
        
        sys.stdout.flush()
        self._prev_frame = frame
        self._frame_lines = new_lines
        
        if self.state == 'initial':
            self.state = 'active'

    async def prompt(self) -> Union[str, object]:
        """Start the prompt and return the final value."""
        try:
            if self.initial_value is not None and self._track:
                self.value = str(self.initial_value)
                self._cursor = len(self.value)
            
            self.render()
            
            while True:
                try:
                    key = readchar.readkey()
                    if not self.handle_key(key):
                        break
                    self.render()
                except KeyboardInterrupt:
                    self.state = 'cancel'
                    break
            
            # Handle final state
            self._restore_cursor_position()
            self._clear_lines(self._frame_lines)
            if self.state in ('submit', 'cancel'):
                final_frame = self.render_fn(self)
                sys.stdout.write(final_frame)
                sys.stdout.flush()
            
            return self.value if self.state == 'submit' else CANCEL
            
        finally:
            sys.stdout.write('\033[?25h')  # Show cursor
            self.emit(self.state, self.value)
            self._subscribers.clear()

    def close(self) -> None:
        """Clean up and restore terminal settings."""
        sys.stdout.write('\033[?25h')  # Show cursor