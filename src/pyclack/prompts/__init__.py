from .text import text
from .password import password
from .select import select
from .mutliselect import multiselect
from .confirm import confirm
from .spinner import spinner, with_spinner
from core import Option, is_cancel
from utils.styling import Color, strip_ansi, S_BAR, S_STEP_SUBMIT, S_CORNER_TOP_RIGHT, S_BAR_H, S_CONNECT_LEFT, S_CORNER_BOTTOM_RIGHT, S_BAR_START, S_BAR_END

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