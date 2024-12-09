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

<h1 align="center">
  Documentation
</h1>

`/core`: This is your toolkit for building custom CLIs from scratch. It provides robust, unstyled components that give you complete creative freedom while handling all the complex functionality under the hood.

`/prompts`: Need something ready to use? This package offers a collection of beautifully designed prompts with an intuitive API. Just import and start using them - perfect when you want professional results without the custom styling work.

#### Installation
```cmd
pip install pyclack-cli           # Base installation
pip install pyclack-cli[core]     # Core features
pip install pyclack-cli[prompts]  # Prompts features
pip install pyclack-cli[all]      # Everything
```

## Core Prompt Base Class: `/core`

Low-level components for building custom CLI interfaces.

The `Prompt` class is the foundation for all interactive prompts. It handles keyboard input, rendering, and state management.

```python
from core import Prompt

class Prompt:
    def __init__(
        self,
        render: Callable[['Prompt'], Optional[str]],  # Function to render the prompt
        placeholder: str = '',                        # Placeholder text when empty
        initial_value: Any = None,                    # Starting value
        validate: Optional[Callable[[Any], Optional[str]]] = None,  # Validation function
        debug: bool = False,                          # Enable debug mode
        track_value: bool = True                      # Enable value tracking
    )
```

#### Key Properties:
- `state`: Current prompt state ('initial', 'active', 'cancel', 'submit', 'error')
- `value`: Current value of the prompt
- `error`: Current error message if validation fails

#### Methods:
- `prompt()`: Start the prompt and handle user input
- `handle_key(key: str)`: Process keyboard input
- `render()`: Render the current frame
- `on(event: str, callback: Callable)`: Add event listener
- `emit(event: str, *args)`: Emit an event

### `TextPrompt`
```python
TextPrompt(
    render: Callable[['TextPrompt'], str],        # Render function
    placeholder: str = '',                        # Placeholder text
    default_value: str = '',                      # Default if empty
    initial_value: str = '',                      # Starting value
    validate: Optional[Callable[[str], Optional[str]]] = None,  # Validation
    debug: bool = False                           # Debug mode
)
```
Basic text input component with cursor movement and editing capabilities.

example:
```python
from core import TextPrompt

async def custom_text_prompt():
    def render(prompt):
        return f"Enter text: {prompt.value_with_cursor}"

    prompt = TextPrompt(
        render=render,
        placeholder="Type here...",
        initial_value=""
    )
    result = await prompt.prompt()
```

### `PasswordPrompt`
```python
PasswordPrompt(
    render: Callable[['PasswordPrompt'], Optional[str]],  # Render function
    mask: str = '•',                              # Character for masking
    placeholder: str = '',                        # Placeholder text
    validate: Optional[Callable[[Any], Optional[str]]] = None,  # Validation
    debug: bool = False                           # Debug mode
)
```
Masked input component for secure password entry.

example:
```python
from core import PasswordPrompt

async def custom_password_prompt():
    def render(prompt):
        return f"Password: {prompt.masked}"

    prompt = PasswordPrompt(
        render=render,
        mask="*"
    )
    result = await prompt.prompt()
```

#### `SelectPrompt`
```python
SelectPrompt(
    render: Callable[['SelectPrompt'], str],      # Render function
    options: List[Option],                        # List of selectable options
    initial_value: Any = None,                    # Initially selected value
    validate: Optional[Callable[[Any], Optional[str]]] = None,  # Validation
    debug: bool = False                           # Debug mode
)
```
Single-selection component for choosing from a list of options.

example:
```python
from core import SelectPrompt, Option

async def custom_select_prompt():
    options = [
        Option("apple", "Apple"),
        Option("banana", "Banana")
    ]
    
    def render(prompt):
        return f"Select fruit: {prompt.options[prompt.cursor].label}"

    prompt = SelectPrompt(
        render=render,
        options=options
    )
    result = await prompt.prompt()
```

#### `MultiSelectPrompt`
```python
MultiSelectPrompt(
    render: Callable[['MultiSelectPrompt'], Optional[str]],  # Render function
    options: List[Option],                        # List of selectable options
    initial_values: List[Any] = None,             # Initially selected values
    required: bool = False,                       # Require at least one selection
    cursor_at: Any = None,                        # Initial cursor position
    debug: bool = False                           # Debug mode
)
```
Multiple-selection component for choosing multiple items from a list.

example:
```python
from core import MultiSelectPrompt, Option

async def custom_multiselect_prompt():
    options = [
        Option("red", "Red"),
        Option("blue", "Blue")
    ]
    
    def render(prompt):
        selected = [opt.label for opt in prompt.options if opt.value in prompt.value]
        return f"Selected: {', '.join(selected)}"

    prompt = MultiSelectPrompt(
        render=render,
        options=options
    )
    result = await prompt.prompt()
```

#### `ConfirmPrompt`
```python
ConfirmPrompt(
    render: Callable[['ConfirmPrompt'], Optional[str]],  # Render function
    active: str = 'Yes',                          # Text for true value
    inactive: str = 'No',                         # Text for false value
    initial_value: bool = False,                  # Starting value
    debug: bool = False                           # Debug mode
)
```
Yes/No confirmation component.

example
```python
from core import ConfirmPrompt

async def custom_confirm_prompt():
    def render(prompt):
        return f"Proceed? {prompt.active if prompt.value else prompt.inactive}"

    prompt = ConfirmPrompt(
        render=render,
        active="Yes",
        inactive="No"
    )
    result = await prompt.prompt()
```

#### `Spinner`
```python
Spinner(
    # No initialization parameters
    
    # Methods:
    start(message: str = '')      # Start spinning with message
    stop(message: str = None,     # Stop spinning with final message
         code: int = 0)           # Status code (0=success, 1=cancel, 2=error)
    update(message: str)          # Update spinner message
)
```
Loading indicator for async operations.

example:
```python
from core import Spinner

spinner = Spinner()
spinner.start("Loading...")
# Do some work
spinner.stop("Completed!")
```

## Ready-to-Use Prompts: `/prompts`

Pre-styled, ready-to-use components with a simple API.

#### `text()`
```python
async def text(
    message: str,                                 # Prompt message
    placeholder: str = '',                        # Placeholder text
    default_value: str = '',                      # Default if empty
    initial_value: str = '',                      # Starting value
    validate: Optional[Callable[[str], Optional[str]]] = None  # Validation
) -> Union[str, object]                          # Returns value or CANCEL
```
Styled text input with placeholder support.

example:
```python
from prompts import text

result = await text(
    message="What's your name?",
    placeholder="Enter name",
    initial_value=""
)
```

#### `password()`
```python
async def password(
    message: str,                                 # Prompt message
    mask: str = '•',                             # Masking character
    validate: Optional[Callable[[str], Optional[str]]] = None  # Validation
) -> Union[str, object]                          # Returns value or CANCEL
```
Secure password input with masked characters.

example:
```python
from prompts import password

result = await password(
    message="Enter your password:",
    mask="•"
)
```

### select()
```python
async def select(
    message: str,                                 # Prompt message
    options: List[Option],                        # List of options
    initial_value: Any = None,                    # Initially selected value
    max_items: Optional[int] = None               # Max visible items
) -> Union[Any, object]                          # Returns selected value or CANCEL
```
Styled single-selection menu.

example:
```python
from prompts import select, Option

result = await select(
    message="Choose a fruit:",
    options=[
        Option("apple", "Apple"),
        Option("banana", "Banana")
    ]
)
```

### multiselect()
```python
async def multiselect(
    message: str,                                 # Prompt message
    options: List[Option],                        # List of options
    initial_values: List[Any] = None,             # Initially selected values
    max_items: Optional[int] = None,              # Max visible items
    required: bool = True,                        # Require at least one selection
    cursor_at: Any = None                         # Initial cursor position
) -> Union[List[Any], object]                    # Returns selected values or CANCEL
```
Styled multiple-selection menu with checkboxes.

example:
```python
from prompts import multiselect, Option

result = await multiselect(
    message="Select colors:",
    options=[
        Option("red", "Red"),
        Option("blue", "Blue"),
        Option("green", "Green")
    ]
)
```

### confirm()
```python
async def confirm(
    message: str,                                 # Prompt message
    active: str = "Yes",                          # Text for true value
    inactive: str = "No",                         # Text for false value
    initial_value: bool = True                    # Starting value
) -> Union[bool, object]                         # Returns boolean or CANCEL
```
Styled Yes/No confirmation prompt.

example:
```python
from prompts import confirm

result = await confirm(
    message="Do you want to continue?",
    active="Yes",
    inactive="No"
)
```

### spinner()
### spinner()
```python
# As context manager
async with spinner(
    message: str = '',                            # Spinner message
    options: Optional[Dict] = None                # Styling options
) as spin:
    spin.update("New message")                    # Update message

# As decorator
@with_spinner(message: str = '')
async def my_function():
    pass
```
Styled loading spinner with async context manager support.

example:
```python
from prompts import spinner
import asyncio

async def main():
    async with spinner("Installing dependencies..."):
        await asyncio.sleep(2)
    
    # Or use as decorator
    @with_spinner("Loading...")
    async def long_task():
        await asyncio.sleep(2)
```

### Additional Features

- All prompts support cancellation with Ctrl+C
- Built-in error handling and validation
- Unicode support with fallbacks
- Consistent styling and color themes
- Keyboard navigation (arrow keys, vim-style hjkl)
