from .prompt import *
from typing import Optional, Callable, Any, Union

class PasswordPrompt(Prompt):
    def __init__(
        self,
        render: Callable[['PasswordPrompt'], Optional[str]],
        mask: str = '•',
        placeholder: str = '',
        validate: Optional[Callable[[Any], Optional[str]]] = None,
        debug: bool = False
    ):
        super().__init__(
            render=render,
            placeholder=placeholder,
            initial_value='',
            validate=validate,
            debug=debug
        )
        
        self._mask = mask
        self.value_with_cursor = ''
        self._text_buffer = []
        
        self.on('finalize', self._handle_finalize)
        self.on('key', self._handle_key)
        
    @property
    def cursor(self) -> int:
        return self._cursor
    
    @property
    def masked(self) -> str:
        """Return the masked version of the value."""
        return self._mask * len(self.value) if self.value else ''
    
    def _handle_finalize(self, *args):
        """Handle the finalize event."""
        self.value_with_cursor = self.masked
    
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
        color = Color()
        if self._cursor >= len(self.value):
            self.value_with_cursor = f"{self.masked}{color.inverse(color.hidden('_'))}"
        else:
            s1 = self.masked[:self._cursor]
            s2 = self.masked[self._cursor:]
            self.value_with_cursor = f"{s1}{color.inverse(s2[0])}{s2[1:]}"
    
    async def prompt(self) -> Union[str, object]:
        """Override prompt method to initialize text buffer."""
        self._text_buffer = list(self.initial_value) if self.initial_value else []
        self._cursor = len(self._text_buffer)
        self._update_value_with_cursor()
        return await super().prompt()