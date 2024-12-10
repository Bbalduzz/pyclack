from .prompt import *
from src.pyclack.utils.styling import Color
from typing import Optional, Callable, Any, Union

class TextPrompt(Prompt):
    def __init__(
        self,
        render: Callable[['TextPrompt'], str],
        placeholder: str = '',
        default_value: str = '',
        initial_value: str = '',
        validate: Optional[Callable[[str], Optional[str]]] = None,
        debug: bool = False
    ):
        super().__init__(
            render=render,
            placeholder=placeholder,
            initial_value=initial_value,
            validate=validate,
            debug=debug
        )
        
        self.default_value = default_value
        self.value_with_cursor = ''
        self._text_buffer = list(initial_value) if initial_value else []
        
        # Set up event handlers
        self.on('finalize', self._handle_finalize)
        self.on('key', self._handle_key)
        self._cursor = len(self._text_buffer)
        
    @property
    def cursor(self) -> int:
        return self._cursor
    
    def _handle_finalize(self, *args):
        """Handle the finalize event."""
        if not self.value and self.default_value:
            self.value = self.default_value
        self.value_with_cursor = self.value
    
    def _handle_key(self, char: str):
        """Handle key input events."""
        if char == readchar.key.BACKSPACE:
            if self._cursor > 0:
                self._text_buffer.pop(self._cursor - 1)
                self._cursor -= 1
        elif char.isprintable():
            self._text_buffer.insert(self._cursor, char)
            self._cursor += 1
            
        self.value = ''.join(self._text_buffer)
        self._update_value_with_cursor()
    
    def _update_value_with_cursor(self):
        """Update the value_with_cursor property based on current cursor position."""
        if self._cursor >= len(self.value):
            self.value_with_cursor = f"{self.value}{Color.inverse(Color.hidden('_'))}"
        else:
            s1 = self.value[:self._cursor]
            s2 = self.value[self._cursor:]
            self.value_with_cursor = f"{s1}{Color.inverse(s2[0])}{s2[1:]}"
    
    async def prompt(self) -> str:
        """Start the prompt and handle initial setup."""
        self._text_buffer = list(self.initial_value) if self.initial_value else []
        self._cursor = len(self._text_buffer)
        self._update_value_with_cursor()
        return await super().prompt()