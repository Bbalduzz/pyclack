from .prompt import *
from typing import Optional, Callable, Any, Union

class ConfirmPrompt(Prompt):
    def __init__(
        self,
        render: Callable[['ConfirmPrompt'], Optional[str]],
        active: str = 'Yes',
        inactive: str = 'No',
        initial_value: bool = False,
        debug: bool = False
    ):
        super().__init__(
            render=render,
            initial_value=initial_value,
            debug=debug,
            track_value=False  # Important: we're handling value tracking differently for confirm
        )
        
        self.active = active
        self.inactive = inactive
        self.value = initial_value
        
        # Set up event handlers
        self.on('value', self._handle_value)
        self.on('confirm', self._handle_confirm)
        self.on('cursor', self._handle_cursor)
    
    @property
    def cursor(self) -> int:
        return 0 if self.value else 1
    
    @property
    def _value(self) -> bool:
        return self.cursor == 0
    
    def _handle_value(self, *args):
        """Handle value changes."""
        self.value = self._value
    
    def _handle_confirm(self, confirm: bool):
        """Handle confirmation (y/n key press)."""
        sys.stdout.write('\033[A')  # Move cursor up one line
        self.value = confirm
        self.state = 'submit'
        self.close()
    
    def _handle_cursor(self, direction: str):
        """Handle cursor movement (left/right/up/down)."""
        if direction in ('left', 'right', 'up', 'down'):
            self.value = not self.value
    
    def handle_key(self, key: str) -> bool:
        """Override key handling for confirm-specific behavior."""
        if key.lower() in ('y', 'n'):
            self._handle_confirm(key.lower() == 'y')
            return False
        
        return super().handle_key(key)
