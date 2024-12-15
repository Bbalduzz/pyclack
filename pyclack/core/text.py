from .prompt import *
from pyclack.utils.styling import Color
from typing import Optional, Callable, Any, Union


class TextPrompt(Prompt):
    def __init__(
        self,
        render: Callable[["TextPrompt"], str],
        placeholder: str = "",
        default_value: str = "",
        initial_value: str = "",
        validate: Optional[Callable[[str], Optional[str]]] = None,
        debug: bool = False,
    ):
        super().__init__(
            render=render,
            placeholder=placeholder,
            initial_value=initial_value,
            validate=validate,
            debug=debug,
        )

        self.default_value = default_value
        self.value_with_cursor = ""
        self._text_buffer = list(initial_value) if initial_value else []

        # Set up event handlers
        self.on("finalize", self._handle_finalize)
        self.on("key", self._handle_key)
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

        self.value = "".join(self._text_buffer)
        self._update_value_with_cursor()

    def _update_value_with_cursor(self):
        """Update the value_with_cursor property based on current cursor position."""
        if self._cursor >= len(self.value):
            self.value_with_cursor = f"{self.value}{Color.inverse(Color.hidden('_'))}"
        else:
            s1 = self.value[: self._cursor]
            s2 = self.value[self._cursor :]
            self.value_with_cursor = f"{s1}{Color.inverse(s2[0])}{s2[1:]}"

    async def prompt(self) -> str:
        """Start the prompt and handle initial setup."""
        self._text_buffer = list(self.initial_value) if self.initial_value else []
        self._cursor = len(self._text_buffer)
        self._update_value_with_cursor()
        return await super().prompt()


class MultilineTextPrompt(TextPrompt):
    def __init__(
        self,
        render: Callable[["MultilineTextPrompt"], str],
        placeholder: str = "",
        default_value: str = "",
        initial_value: str = "",
        validate: Optional[Callable[[str], Optional[str]]] = None,
        debug: bool = False,
    ):
        super().__init__(
            render=render,
            placeholder=placeholder,
            initial_value=initial_value,
            validate=validate,
            debug=debug,
        )

        # Track line and column position
        self._current_line = 0
        self._lines = (
            [[]]
            if not initial_value
            else [list(line) for line in initial_value.split("\n")]
        )
        self._cursor_line = 0
        self._cursor_col = 0

    @property
    def cursor(self) -> tuple[int, int]:
        """Return current cursor position as (line, column)."""
        return (self._cursor_line, self._cursor_col)

    def _handle_key(self, char: str):
        """Handle key input events with multiline support."""
        if (
            char == readchar.key.CTRL_J
        ):  # Shift+Enter (CTRL_J typically represents this)
            # Insert newline
            current_line = self._lines[self._cursor_line]
            rest_of_line = current_line[self._cursor_col :]
            self._lines[self._cursor_line] = current_line[: self._cursor_col]
            self._lines.insert(self._cursor_line + 1, rest_of_line)
            self._cursor_line += 1
            self._cursor_col = 0
        elif char == readchar.key.BACKSPACE:
            if self._cursor_col > 0:
                self._lines[self._cursor_line].pop(self._cursor_col - 1)
                self._cursor_col -= 1
            elif self._cursor_line > 0:
                # Merge with previous line
                self._cursor_col = len(self._lines[self._cursor_line - 1])
                self._lines[self._cursor_line - 1].extend(
                    self._lines[self._cursor_line]
                )
                self._lines.pop(self._cursor_line)
                self._cursor_line -= 1
        elif char == readchar.key.UP and self._cursor_line > 0:
            self._cursor_line -= 1
            self._cursor_col = min(
                self._cursor_col, len(self._lines[self._cursor_line])
            )
        elif char == readchar.key.DOWN and self._cursor_line < len(self._lines) - 1:
            self._cursor_line += 1
            self._cursor_col = min(
                self._cursor_col, len(self._lines[self._cursor_line])
            )
        elif char == readchar.key.LEFT and self._cursor_col > 0:
            self._cursor_col -= 1
        elif char == readchar.key.RIGHT and self._cursor_col < len(
            self._lines[self._cursor_line]
        ):
            self._cursor_col += 1
        elif char.isprintable():
            self._lines[self._cursor_line].insert(self._cursor_col, char)
            self._cursor_col += 1

        # Update the value property
        self.value = "\n".join("".join(line) for line in self._lines)
        self._update_value_with_cursor()

    def _update_value_with_cursor(self):
        """Update the value_with_cursor property for multiline text."""
        lines_with_cursor = []
        for i, line in enumerate(self._lines):
            if i == self._cursor_line:
                if self._cursor_col >= len(line):
                    line_str = "".join(line) + Color.inverse(Color.hidden("_"))
                else:
                    s1 = "".join(line[: self._cursor_col])
                    s2 = "".join(line[self._cursor_col :])
                    line_str = f"{s1}{Color.inverse(s2[0])}{s2[1:]}"
            else:
                line_str = "".join(line)
            lines_with_cursor.append(line_str)

        self.value_with_cursor = "\n".join(lines_with_cursor)
