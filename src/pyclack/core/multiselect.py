from .prompt import *
from .select import Option
from typing import Any, Generic, TypeVar, List, Optional

T = TypeVar('T')

class MultiSelectPrompt(Prompt, Generic[T]):
    def __init__(
        self,
        render: Callable[['MultiSelectPrompt'], Optional[str]],
        options: List[Option],
        initial_values: List[Any] = None,
        required: bool = False,
        cursor_at: Any = None,
        debug: bool = False
    ):
        super().__init__(
            render=render,
            debug=debug,
            track_value=False  # We handle value tracking ourselves
        )
        
        self.options = options
        self.value = list(initial_values or [])
        self._cursor = max(
            next((i for i, opt in enumerate(options) if opt.value == cursor_at), 0),
            0
        )
        self.required = required
        
        # Set up event handlers
        self.on('key', self._handle_key)
        self.on('cursor', self._handle_cursor)
    
    @property
    def cursor(self) -> int:
        return self._cursor
    
    @cursor.setter
    def cursor(self, value: int):
        self._cursor = value
    
    @property
    def _value(self) -> Any:
        """Get the value at current cursor position."""
        return self.options[self.cursor].value
    
    def toggle_all(self):
        """Toggle all options selection."""
        all_selected = len(self.value) == len(self.options)
        if all_selected:
            self.value = [] if not self.required else [self._value]
        else:
            self.value = [opt.value for opt in self.options]
    
    def toggle_value(self):
        """Toggle current value selection."""
        current = self._value
        if current in self.value:
            # Don't deselect if it's the last item and required is True
            if not (self.required and len(self.value) == 1):
                self.value = [v for v in self.value if v != current]
        else:
            self.value = [*self.value, current]
    
    def _handle_key(self, char: str):
        """Handle key press events."""
        if char == 'a':
            self.toggle_all()
    
    def _handle_cursor(self, key: str):
        """Handle cursor movement and space selection."""
        if key in ('left', 'up'):
            self.cursor = (
                len(self.options) - 1 if self.cursor == 0 
                else self.cursor - 1
            )
        elif key in ('down', 'right'):
            self.cursor = (
                0 if self.cursor == len(self.options) - 1 
                else self.cursor + 1
            )
        elif key == 'space':
            self.toggle_value()
    
    def handle_key(self, key: str) -> bool:
        """Override key handling for multi-select specific behavior."""
        if key == readchar.key.ENTER:
            if self.required and not self.value:
                self.error = "At least one option must be selected"
                self.state = 'error'
                return True
            
            if self.validate:
                problem = self.validate(self.value)
                if problem:
                    self.error = problem
                    self.state = 'error'
                    return True
            
            self.state = 'submit'
            return False
            
        return super().handle_key(key)
