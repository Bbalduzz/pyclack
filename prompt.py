from contextlib import asynccontextmanager
from functools import wraps
import asyncio
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, TypeVar, Union, Generic

from core import (
    is_cancel, TextPrompt, PasswordPrompt, ConfirmPrompt, 
    SelectPrompt, SelectKeyPrompt, MultiSelectPrompt
)
from utils.styling import (
    Color, symbol, S_BAR, S_BAR_END, S_BAR_START, S_STEP_SUBMIT,
    S_PASSWORD_MASK, S_RADIO_ACTIVE, S_RADIO_INACTIVE,
    S_CHECKBOX_ACTIVE, S_CHECKBOX_SELECTED, S_CHECKBOX_INACTIVE,
    strip_ansi, limit_options, S_BAR_H, S_CORNER_TOP_RIGHT, 
    S_CONNECT_LEFT, S_CORNER_BOTTOM_RIGHT
)
from core.spinner import Spinner

def is_cancelled(value: Any) -> bool:
    return is_cancel(value)

@dataclass
class Option:
    value: Any
    label: str = ''
    hint: str = ''

def create_note(message: str = '', title: str = '') -> str:
    lines = f"\n{message}\n".split('\n')
    title_len = len(strip_ansi(title))
    max_len = max(
        max(len(strip_ansi(ln)) for ln in lines),
        title_len
    ) + 2

    formatted_lines = [
        f"{Color.gray(S_BAR)}  {Color.dim(ln)}{' ' * (max_len - len(strip_ansi(ln)))}{Color.gray(S_BAR)}"
        for ln in lines
    ]
    
    note_display = "\n".join(formatted_lines)
    
    return (
        f"{Color.gray(S_BAR)}\n"
        f"{Color.reset(S_STEP_SUBMIT)}  {Color.reset(title)} {Color.gray(S_BAR_H * max(max_len - title_len - 1, 1))}{Color.gray(S_CORNER_TOP_RIGHT)}\n"
        f"{note_display}\n"
        f"{Color.gray(S_CONNECT_LEFT)}{Color.gray(S_BAR_H * (max_len + 2))}{Color.gray(S_CORNER_BOTTOM_RIGHT)}\n"
    )

def note(message: str = None, title: str = '', next_steps: list = []) -> str:
    print(create_note(
        message=message if message else '\n'.join(next_steps),
        title=title if title else "Next steps."
    ))

async def text(
    message: str,
    placeholder: str = '',
    default_value: str = '',
    initial_value: str = '',
    validate: Optional[Callable[[str], Optional[str]]] = None
) -> Union[str, object]:
    def render(prompt: TextPrompt) -> str:
        title = f"{Color.gray(S_BAR)}\n{symbol(prompt.state)}  {message}\n"
        placeholder_text = (
            Color.inverse(placeholder[0]) + Color.dim(placeholder[1:])
            if placeholder else Color.inverse(Color.hidden('_'))
        )
        value = placeholder_text if not prompt.value else prompt.value_with_cursor

        if prompt.state == 'error':
            return (f"{title.rstrip()}\n"
                   f"{Color.yellow(S_BAR)}  {value}\n"
                   f"{Color.yellow(S_BAR_END)}  {Color.yellow(prompt.error)}\n")
        elif prompt.state == 'submit':
            return (f"{Color.gray(S_BAR)}\n"
                   f"{symbol(prompt.state)}  {message}\n")
        elif prompt.state == 'cancel':
            return (f"{title}{Color.gray(S_BAR)}  "
                   f"{Color.strikethrough(Color.dim(prompt.value or ''))}"
                   f"{prompt.value and prompt.value.strip() and f'\n{Color.gray(S_BAR)}' or ''}")
        else:
            return f"{title}{Color.cyan(S_BAR)}  {value}\n{Color.cyan(S_BAR_END)}\n"

    prompt = TextPrompt(
        render=render,
        placeholder=placeholder,
        initial_value=initial_value,
        default_value=default_value,
        validate=validate
    )
    result = await prompt.prompt()
    
    if is_cancel(result):
        return result
        
    print(f"{Color.gray(S_BAR)}  {Color.dim(result)}")
    return result

async def password(
    message: str,
    mask: str = S_PASSWORD_MASK,
    validate: Optional[Callable[[str], Optional[str]]] = None
) -> Union[str, object]:
    def render(prompt: PasswordPrompt) -> str:
        title = f"{Color.gray(S_BAR)}\n{symbol(prompt.state)}  {message}\n"
        value = prompt.value_with_cursor
        masked = prompt.masked

        if prompt.state == 'error':
            return (f"{title.rstrip()}\n"
                   f"{Color.yellow(S_BAR)}  {masked}\n"
                   f"{Color.yellow(S_BAR_END)}  {Color.yellow(prompt.error)}\n")
        elif prompt.state == 'submit':
            return f"{title}"
        elif prompt.state == 'cancel':
            return (f"{title}{Color.gray(S_BAR)}  "
                   f"{Color.strikethrough(Color.dim(masked or ''))}"
                   f"{masked and f'\n{Color.gray(S_BAR)}' or ''}")
        else:
            return f"{title}{Color.cyan(S_BAR)}  {value}\n{Color.cyan(S_BAR_END)}\n"

    prompt = PasswordPrompt(render=render, mask=mask, validate=validate)
    result = await prompt.prompt()
    
    if is_cancel(result):
        return result

    print(f"{Color.gray(S_BAR)}  {Color.dim(S_PASSWORD_MASK * len(result))}")
    return result

async def confirm(
    message: str,
    active: str = "Yes",
    inactive: str = "No",
    initial_value: bool = True
) -> Union[bool, object]:
    def render(prompt: ConfirmPrompt) -> str:
        title = f"{Color.gray(S_BAR)}\n{symbol(prompt.state)}  {message}\n"
        value = active if prompt.value else inactive

        if prompt.state == 'submit':
            return f"{title}"
        elif prompt.state == 'cancel':
            return (f"{title}{Color.gray(S_BAR)}  "
                   f"{Color.strikethrough(Color.dim(value))}\n"
                   f"{Color.gray(S_BAR)}")
        else:
            active_style = (
                f"{Color.green(S_RADIO_ACTIVE)} {active}"
                if prompt.value else
                f"{Color.dim(S_RADIO_INACTIVE)} {Color.dim(active)}"
            )
            inactive_style = (
                f"{Color.green(S_RADIO_ACTIVE)} {inactive}"
                if not prompt.value else
                f"{Color.dim(S_RADIO_INACTIVE)} {Color.dim(inactive)}"
            )
            return (f"{title}{Color.cyan(S_BAR)}  "
                   f"{active_style} {Color.dim('/')} {inactive_style}\n"
                   f"{Color.cyan(S_BAR_END)}\n")

    prompt = ConfirmPrompt(
        render=render,
        active=active,
        inactive=inactive,
        initial_value=initial_value
    )
    result = await prompt.prompt()
    
    if is_cancel(result):
        return result
        
    
    print(f"{Color.gray(S_BAR)}  {Color.dim(result)}")
    return result

async def select(
    message: str,
    options: List[Option],
    initial_value: Any = None,
    max_items: Optional[int] = None
) -> Union[Any, object]:
    def opt(option: Option, state: str) -> str:
        label = option.label or str(option.value)
        if state == 'selected':
            return Color.dim(label)
        elif state == 'active':
            return (f"{Color.green(S_RADIO_ACTIVE)} {label} "
                   f"{option.hint and Color.dim(f'({option.hint})') or ''}")
        elif state == 'cancelled':
            return Color.strikethrough(Color.dim(label))
        else:
            return f"{Color.dim(S_RADIO_INACTIVE)} {Color.dim(label)}"

    def render(prompt: SelectPrompt) -> str:
        title = f"{Color.gray(S_BAR)}\n{symbol(prompt.state)}  {message}\n"

        if prompt.state == 'submit':
            return f"{title}"
        elif prompt.state == 'cancel':
            return (f"{title}{Color.gray(S_BAR)}  "
                   f"{opt(prompt.options[prompt.cursor], 'cancelled')}\n"
                   f"{Color.gray(S_BAR)}")
        else:
            styled_options = limit_options(
                options=prompt.options,
                cursor=prompt.cursor,
                max_items=max_items,
                style=lambda item, active: opt(item, 'active' if active else 'inactive')
            )
            return (f"{title}{Color.cyan(S_BAR)}  "
                   f"{f'\n{Color.cyan(S_BAR)}  '.join(styled_options)}\n"
                   f"{Color.cyan(S_BAR_END)}\n")

    prompt = SelectPrompt(
        render=render,
        options=options,
        initial_value=initial_value
    )
    result = await prompt.prompt()
    
    if is_cancel(result):
        return result
        
    selected_option = next((opt for opt in options if opt.value == result), None)
    if selected_option:
        print(f"{Color.gray(S_BAR)}  {Color.dim(selected_option.label)}")
    return result

async def multiselect(
    message: str,
    options: List[Option],
    initial_values: List[Any] = None,
    max_items: Optional[int] = None,
    required: bool = True,
    cursor_at: Any = None
) -> Union[List[Any], object]:
    
    def render(prompt: MultiSelectPrompt) -> str:
        def opt(option: Option, state: str) -> str:
            label = option.label or str(option.value)
            if state == 'active':
                return (f"{Color.cyan(S_CHECKBOX_ACTIVE)} {label} "
                       f"{option.hint and Color.dim(f'({option.hint})') or ''}")
            elif state == 'selected':
                return f"{Color.green(S_CHECKBOX_SELECTED)} {Color.dim(label)}"
            elif state == 'cancelled':
                return Color.strikethrough(Color.dim(label))
            elif state == 'active-selected':
                return (f"{Color.green(S_CHECKBOX_SELECTED)} {label} "
                       f"{option.hint and Color.dim(f'({option.hint})') or ''}")
            elif state == 'submitted':
                return Color.dim(label)
            return f"{Color.dim(S_CHECKBOX_INACTIVE)} {Color.dim(label)}"

        title = f"{Color.gray(S_BAR)}\n{symbol(prompt.state)}  {message}\n"

        if prompt.state == 'submit':
            selected = [opt for opt in prompt.options if opt.value in prompt.value]
            selected_labels = [opt.label for opt in selected]
            return (f"{Color.gray(S_BAR)}\n"
                   f"{symbol(prompt.state)}  {message}\n")

        if prompt.state == 'cancel':
            selected = [opt for opt in prompt.options if opt.value in prompt.value]
            selected_str = Color.dim(', ').join(opt(o, 'cancelled') for o in selected)
            return (f"{title}{Color.gray(S_BAR)}  "
                   f"{selected_str}\n{Color.gray(S_BAR) if selected_str else ''}")
        elif prompt.state == 'error':
            footer = prompt.error.split('\n')
            footer = [
                f"{Color.yellow(S_BAR_END)}  {Color.yellow(footer[0])}",
                *[f"   {line}" for line in footer[1:]]
            ]
            styled_options = limit_options(
                options=prompt.options,
                cursor=prompt.cursor,
                max_items=max_items,
                style=lambda item, active: opt(
                    item,
                    'active-selected' if active and item.value in prompt.value
                    else 'selected' if item.value in prompt.value
                    else 'active' if active
                    else 'inactive'
                )
            )
            return (f"{title}{Color.yellow(S_BAR)}  "
                   f"{f'\n{Color.yellow(S_BAR)}  '.join(styled_options)}\n"
                   f"{'\n'.join(footer)}\n")
        else:
            styled_options = limit_options(
                options=prompt.options,
                cursor=prompt.cursor,
                max_items=max_items,
                style=lambda item, active: opt(
                    item,
                    'active-selected' if active and item.value in prompt.value
                    else 'selected' if item.value in prompt.value
                    else 'active' if active
                    else 'inactive'
                )
            )
            return (f"{title}{Color.cyan(S_BAR)}  "
                   f"{f'\n{Color.cyan(S_BAR)}  '.join(styled_options)}\n"
                   f"{Color.cyan(S_BAR_END)}\n")

    prompt = MultiSelectPrompt(
        render=render,
        options=options,
        initial_values=initial_values,
        required=required,
        cursor_at=cursor_at,
        debug=False
    )
    result = await prompt.prompt()
    
    if is_cancel(result):
        return result
    
    # Print final state
    selected = [opt for opt in options if opt.value in result]
    print(f"{Color.gray(S_BAR)}  {Color.dim(', '.join(opt.label for opt in selected))}")
    
    return result

@asynccontextmanager
async def spinner(message: str = '', options=None):
    """Async context manager for showing a loading spinner.
    
    Args:
        message: Message to display next to spinner
        options: Dict with 'color' styling (defaults to magenta for spinner)
    
    Usage:
        async with spinner("Loading..."):
            await some_async_operation()
    """
    if options is None:
        options = {"color": Color.magenta}
        
    spin = Spinner()
    try:
        spin.start(message)
        yield spin
    finally:
        spin.stop()

def with_spinner(message: str = ''):
    """Decorator to add a spinner to an async function.
    
    Args:
        message: Message to display next to spinner
    
    Usage:
        @with_spinner("Loading...")
        async def my_function():
            await some_async_operation()
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            async with spinner(message) as spin:
                try:
                    result = await func(*args, **kwargs)
                    return result
                except Exception as e:
                    spin.stop(str(e), code=2)
                    raise
        return wrapper
    return decorator

def link(url, label=None, options=None):
    """Generate a terminal hyperlink with optional styling.
    
    Args:
        url: The URL to link to
        label: Optional text to display (defaults to URL if None)
        options: Dict with 'color' and 'bg_color' keys for styling
    """
    if options is None:
        options = {"color": Color.cyan, "bg_color": None}
    
    label = label or url
    color = options.get('color')
    
    # Build link with color function applied to the whole link if color exists
    link = f"\033]8;;{url}\033\\{label}\033]8;;\033\\"
    return color(link) if color else link

def intro(title: str = '', options=None) -> None:
    """Display intro with optional title and styling.
    
    Args:
        title: Optional title text
        options: Dict with 'color' styling (defaults to gray)
    """
    if options is None:
        options = {"color": Color.gray}
    
    color = options.get('color', Color.gray)
    print("\033[H\033[J")  # Clear screen
    print(f"{color(S_BAR_START)}  {title}")

def outro(message: str = '', options=None) -> None:
    """Display outro with optional message and styling.
    
    Args:
        message: Optional message text
        options: Dict with 'color' styling (defaults to gray) 
    """
    if options is None:
        options = {"color": Color.gray}
    
    color = options.get('color', Color.gray)
    print(f"{color(S_BAR)}\n{color(S_BAR_END)}  {message}\n")