<h1 align="center">
  pyclack
  <br>
  <img width="4%" align="center" src="https://img.shields.io/badge/python-blue" alt="logo">
  <img width="6%" align="center" src="https://img.shields.io/pypi/v/pyclack-cli?style=flat&color=blue" alt="logo">
</h1>


<p align="center">
  <b>Building interactive command line interfaces effortlessly.</b>
</p>

<div align="center">
    <kbd>
      <video width="80%" align="center" src="https://github.com/user-attachments/assets/07b959fb-165e-4419-93ba-74c235a7bc38" alt="demo /prompts">
    </kbd>
</div>

## Documentation

<details>
<summary>Table of Contents</summary>

- [Overview](#overview)
- [Installation](#installation)
- [Architecture](#architecture)
- [Core Components](#core-components)
- [Ready-to-Use Prompts](#ready-to-use--prompts)
- [Advanced Usage](#advanced-usage)
- [Contributing](#contributing)
- [Troubleshooting](#troubleshooting)

</details>

### Overview

PyClack is a Python library designed to simplify the creation of interactive command-line interfaces. It provides both low-level components for custom CLI development and high-level, pre-styled prompts for immediate use.

### Key Features

- Rich set of interactive prompts (text, password, select, multiselect, confirm)
- Unicode support with automatic fallbacks
- Consistent styling and color themes
- Keyboard navigation (arrow keys, vim-style hjkl)
- Error handling and validation
- Support for async/await
- Spinner for async operations
- Extensive customization options

## Installation

PyClack can be installed using pip with different installation options:

```bash
pip install pyclack-cli           # Base installation
pip install pyclack-cli[core]     # Core features
pip install pyclack-cli[prompts]  # Prompts features
pip install pyclack-cli[all]      # Everything
```

##### Requirements
- readchar library: https://github.com/magmax/python-readchar

## Architecture

The library follows a two-tier architecture:
- Core components provide the foundational building blocks with maximum flexibility
- Prompts package offers pre-styled, production-ready components for immediate use

PyClack is organized into three main packages:

1. `/core`: Low-level components for building custom CLIs
2. `/prompts`: Ready-to-use, styled prompt components
3. `/utils`: Utility functions for styling and terminal operations
## Core Components

### Base Prompt Class

The `Prompt` class in `/core` is the foundation for all interactive prompts in PyClack. It handles:
- Keyboard input processing
- Terminal rendering
- State management
- Event handling
- Cursor positioning

#### Base Prompt Class Structure

```python
from pyclack.core import Prompt
from typing import Optional, Callable, Any, Union

class Prompt:
    def __init__(
        self,
        render: Callable[['Prompt'], Optional[str]],  # Render function
        placeholder: str = '',                        # Placeholder text
        initial_value: Any = None,                    # Starting value
        validate: Optional[Callable[[Any], Optional[str]]] = None,  # Validation
        debug: bool = False,                          # Debug mode
        track_value: bool = True                      # Value tracking
    )
```

#### Key Properties

- `state`: Current prompt state ('initial', 'active', 'cancel', 'submit', 'error')
- `value`: Current value of the prompt
- `error`: Current error message if validation fails
- `_cursor`: Internal cursor position
- `cols`: Terminal width

#### Key Methods

- `prompt()`: Start the prompt and handle user input
- `handle_key(key: str)`: Process keyboard input
- `render()`: Render the current frame
- `on(event: str, callback: Callable)`: Add event listener
- `emit(event: str, *args)`: Emit an event

### Implementing a Custom Prompt

Here's a step-by-step guide to creating a custom prompt. Let's implement a simple numeric input prompt as an example:

```python
from pyclack.core import Prompt
from pyclack.utils.styling import Color
from typing import Optional, Callable, Any, Union

class NumericPrompt(Prompt):
    def __init__(
        self,
        render: Callable[['NumericPrompt'], str],
        min_value: float = float('-inf'),
        max_value: float = float('inf'),
        initial_value: float = 0,
        debug: bool = False
    ):
        # Initialize parent class
        super().__init__(
            render=render,
            initial_value=initial_value,
            validate=self._validate,  # Custom validation
            debug=debug
        )
        
        self.min_value = min_value
        self.max_value = max_value
        self._text_buffer = []
        self.value_with_cursor = ''
        
        # Set up event handlers
        self.on('key', self._handle_key)
        self.on('finalize', self._handle_finalize)
    
    def _validate(self, value: str) -> Optional[str]:
        """Custom validation logic."""
        try:
            num = float(value)
            if num < self.min_value:
                return f"Value must be ≥ {self.min_value}"
            if num > self.max_value:
                return f"Value must be ≤ {self.max_value}"
            return None
        except ValueError:
            return "Please enter a valid number"
    
    def _handle_key(self, char: str):
        """Handle numeric input and decimal point."""
        if char == readchar.key.BACKSPACE:
            if self._cursor > 0:
                self._text_buffer.pop(self._cursor - 1)
                self._cursor -= 1
        elif char.isdigit() or (char == '.' and '.' not in self._text_buffer):
            self._text_buffer.insert(self._cursor, char)
            self._cursor += 1
            
        self.value = ''.join(self._text_buffer)
        self._update_value_with_cursor()
    
    def _handle_finalize(self, *args):
        """Handle final value conversion."""
        try:
            self.value = float(self.value) if self.value else 0
        except ValueError:
            self.value = 0
        self.value_with_cursor = str(self.value)
    
    def _update_value_with_cursor(self):
        """Update display value with cursor."""
        if self._cursor >= len(self.value):
            self.value_with_cursor = f"{self.value}{Color.inverse(Color.hidden('_'))}"
        else:
            s1 = self.value[:self._cursor]
            s2 = self.value[self._cursor:]
            self.value_with_cursor = f"{s1}{Color.inverse(s2[0])}{s2[1:]}"

    async def prompt(self) -> Union[float, object]:
        """Start the prompt and return final value."""
        self._text_buffer = list(str(self.initial_value)) if self.initial_value else []
        self._cursor = len(self._text_buffer)
        self._update_value_with_cursor()
        result = await super().prompt()
        return float(result) if result is not None else result
```

#### Usage Example

```python
async def main():
    def render(prompt):
        return f"Enter a number ({prompt.min_value}-{prompt.max_value}): {prompt.value_with_cursor}"

    numeric = NumericPrompt(
        render=render,
        min_value=0,
        max_value=100,
        initial_value=50
    )
    
    result = await numeric.prompt()
    print(f"You entered: {result}")
```

### Key Implementation Concepts

### 1. State Management

The prompt maintains its state internally:
```python
self.state = 'initial'  # One of: initial, active, cancel, submit, error
```

### 2. Event System

Subscribe to events using the `on()` method:
```python
self.on('key', self._handle_key)            # Key press events
self.on('finalize', self._handle_finalize)  # Value finalization
self.on('cursor', self._handle_cursor)      # Cursor movement
```

### 3. Rendering

The render function determines the prompt's appearance:
```python
def render(prompt):
    return f"Value: {prompt.value_with_cursor}"
```

### 4. Value Tracking

Track and update the value:
```python
self.value = ''.join(self._text_buffer)  # Current value
self._update_value_with_cursor()         # Display value
```

### 5. Input Handling

Process keyboard input in `_handle_key`:
```python
def _handle_key(self, char: str):
    if char.isdigit():  # Allow only digits
        self._text_buffer.insert(self._cursor, char)
        self._cursor += 1
```

### 6. Validation

Implement validation logic:
```python
def _validate(self, value: str) -> Optional[str]:
    try:
        num = float(value)
        return None  # Valid
    except ValueError:
        return "Invalid number"  # Error message
```

## Core components: `/core`

### TextPrompt

Text input component with cursor movement and editing:

```python
from pyclack.core import TextPrompt

async def custom_text():
    prompt = TextPrompt(
        render=lambda p: f"Enter text: {p.value_with_cursor}",
        placeholder="Type here...",
        initial_value=""
    )
    result = await prompt.prompt()
```

### PasswordPrompt

Secure password input with masked characters:

```python
from pyclack.core import PasswordPrompt

async def custom_password():
    prompt = PasswordPrompt(
        render=lambda p: f"Password: {p.masked}",
        mask="*"
    )
    result = await prompt.prompt()
```

### SelectPrompt

Single-selection menu:

```python
from pyclack.core import SelectPrompt, Option

async def custom_select():
    options = [
        Option("apple", "Apple"),
        Option("banana", "Banana")
    ]
    
    prompt = SelectPrompt(
        render=lambda p: f"Select: {p.options[p.cursor].label}",
        options=options
    )
    result = await prompt.prompt()
```

### MultiSelectPrompt

Multiple-selection component with checkboxes:

```python
from pyclack.core import MultiSelectPrompt, Option

async def custom_multiselect():
    options = [
        Option("red", "Red"),
        Option("blue", "Blue")
    ]
    
    prompt = MultiSelectPrompt(
        render=lambda p: "Selected: " + 
            ", ".join(opt.label for opt in p.options if opt.value in p.value),
        options=options
    )
    result = await prompt.prompt()
```

### Spinner

Loading indicator for async operations:

```python
from pyclack.core import Spinner

spinner = Spinner()
spinner.start("Loading...")
# Do work
spinner.stop("Completed!")
```

## Ready-to-Use : `/prompts`

The `prompts` package provides pre-styled components ready for immediate use.

### Text Input

```python
from pyclack.prompts import text

result = await text(
    message="What's your name?",
    placeholder="Enter name",
    initial_value="",
    validate=lambda x: "Too short" if len(x) < 3 else None
)
```

### Password Input

```python
from pyclack.prompts import password

result = await password(
    message="Enter your password:",
    mask="•",
    validate=lambda x: "Too short" if len(x) < 8 else None
)
```

### Select Menu

```python
from pyclack.prompts import select, Option

result = await select(
    message="Choose a fruit:",
    options=[
        Option("apple", "Apple", "Sweet and crunchy"),
        Option("banana", "Banana", "Yellow fruit")
    ],
    initial_value="apple"
)
```

### Multiple Selection

```python
from pyclack.prompts import multiselect, Option

result = await multiselect(
    message="Select colors:",
    options=[
        Option("red", "Red"),
        Option("blue", "Blue"),
        Option("green", "Green")
    ],
    required=True
)
```

### Confirmation Dialog

```python
from pyclack.prompts import confirm

result = await confirm(
    message="Do you want to continue?",
    active="Yes",
    inactive="No",
    initial_value=True
)
```

### Spinner

```python
from pyclack.prompts import spinner
import asyncio

# As context manager
async with spinner("Installing dependencies...") as spin:
    await asyncio.sleep(1)
    spin.update("Almost done...")

# As decorator
@with_spinner("Loading...")
async def long_task():
    await asyncio.sleep(2)
```

## Advanced Usage

### Custom Styling

The `utils.styling` module provides utilities for terminal styling:

```python
from pyclack.utils.styling import Color

# Available colors
text = Color.cyan("Cyan text")
text = Color.red("Red text")
text = Color.green("Green text")
text = Color.yellow("Yellow text")
text = Color.blue("Blue text")
text = Color.magenta("Magenta text")
text = Color.gray("Gray text")

# Text effects
text = Color.dim("Dimmed text")
text = Color.inverse("Inverse text")
text = Color.hidden("Hidden text")
text = Color.strikethrough("Strikethrough text")
```

### Validation

All prompts support custom validation:

```python
async def main():
    result = await text(
        message="Enter email:",
        validate=lambda x: "Invalid email" 
            if not re.match(r"[^@]+@[^@]+\.[^@]+", x) 
            else None
    )
```

### Error Handling

```python
from pyclack.prompts import text, is_cancel

async def main():
    result = await text("Enter name:")
    if is_cancel(result):
        print("User cancelled")
        return
```

### Unicode Support

PyClack automatically detects Unicode support and falls back to ASCII characters when needed:

```python
from pyclack.utils.styling import is_unicode_supported

if is_unicode_supported():
    # Use Unicode symbols
    symbol = "◆"
else:
    # Use ASCII fallback
    symbol = "*"
```

## Contributing

### Development Setup

1. Clone the repository:
```bash
git clone https://github.com/Bbalduzz/pyclack.git
cd pyclack
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Unix
venv\Scripts\activate     # Windows
```

3. Install development dependencies:
```bash
pip install -e ".[all]"
```

### Coding Standards

- Follow PEP 8 guidelines
- Include type hints for all functions
- Document all public APIs
- Write unit tests for new features
- Maintain Unicode fallbacks for all symbols

### Getting Help

- Submit issues on GitHub
- Check the [GitHub repository](https://github.com/Bbalduzz/pyclack) for updates
- Read the source code for detailed implementation