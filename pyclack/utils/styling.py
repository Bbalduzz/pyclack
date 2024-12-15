import sys
import re
import shutil
from typing import Any, List, Optional, Callable


def is_unicode_supported() -> bool:
    """Check if terminal supports Unicode characters."""
    try:
        return bool(sys.stdout.encoding.lower().startswith("utf"))
    except:
        return False


UNICODE = is_unicode_supported()


def s(unicode: str, fallback: str) -> str:
    """Select Unicode or fallback character based on terminal support."""
    return unicode if UNICODE else fallback


# Symbols
S_STEP_ACTIVE = s("◆", "*")
S_STEP_CANCEL = s("■", "x")
S_STEP_ERROR = s("▲", "x")
S_STEP_SUBMIT = s("◇", "o")

S_BAR_START = s("┌", "T")
S_BAR = s("│", "|")
S_BAR_END = s("└", "—")

S_RADIO_ACTIVE = s("●", ">")
S_RADIO_INACTIVE = s("○", " ")
S_CHECKBOX_ACTIVE = s("◻", "[•]")
S_CHECKBOX_SELECTED = s("◼", "[+]")
S_CHECKBOX_INACTIVE = s("◻", "[ ]")
S_PASSWORD_MASK = s("▪", "•")

S_BAR_H = s("─", "-")
S_CORNER_TOP_RIGHT = s("╮", "+")
S_CONNECT_LEFT = s("├", "+")
S_CORNER_BOTTOM_RIGHT = s("╯", "+")

S_INFO = s("●", "•")
S_SUCCESS = s("◆", "*")
S_WARN = s("▲", "!")
S_ERROR = s("■", "x")


class Color:
    """ANSI color and style utilities."""

    @staticmethod
    def gray(text: str) -> str:
        return f"\033[90m{text}\033[0m"

    @staticmethod
    def cyan(text: str) -> str:
        return f"\033[36m{text}\033[0m"

    @staticmethod
    def red(text: str) -> str:
        return f"\033[31m{text}\033[0m"

    @staticmethod
    def green(text: str) -> str:
        return f"\033[32m{text}\033[0m"

    @staticmethod
    def yellow(text: str) -> str:
        return f"\033[33m{text}\033[0m"

    @staticmethod
    def blue(text: str) -> str:
        return f"\033[34m{text}\033[0m"

    @staticmethod
    def magenta(text: str) -> str:
        return f"\033[35m{text}\033[0m"

    @staticmethod
    def dim(text: str) -> str:
        return f"\033[2m{text}\033[0m"

    @staticmethod
    def inverse(text: str) -> str:
        return f"\033[7m{text}\033[0m"

    @staticmethod
    def hidden(text: str) -> str:
        return f"\033[8m{text}\033[0m"

    @staticmethod
    def strikethrough(text: str) -> str:
        return f"\033[9m{text}\033[0m"

    @staticmethod
    def reset(text: str) -> str:
        return f"\033[0m{text}"


def strip_ansi(text: str) -> str:
    """Remove ANSI escape sequences from text."""
    ansi_pattern = r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])"
    return re.sub(ansi_pattern, "", text)


def symbol(state: str) -> str:
    """Get the appropriate symbol for the current state."""
    if state in ("initial", "active"):
        return Color.cyan(S_STEP_ACTIVE)
    elif state == "cancel":
        return Color.red(S_STEP_CANCEL)
    elif state == "error":
        return Color.yellow(S_STEP_ERROR)
    elif state == "submit":
        return Color.green(S_STEP_SUBMIT)
    return ""


def limit_options(
    options: List[Any],
    cursor: int,
    max_items: Optional[int] = None,
    style: Callable[[Any, bool], str] = lambda x, _: str(x),
) -> List[str]:
    """Limit visible options based on terminal size and cursor position."""
    param_max_items = max_items or float("inf")
    output_max_items = max(shutil.get_terminal_size().lines - 4, 0)
    max_items = min(output_max_items, max(param_max_items, 5))

    window_start = 0
    if cursor >= window_start + max_items - 3:
        window_start = max(min(cursor - max_items + 3, len(options) - max_items), 0)
    elif cursor < window_start + 2:
        window_start = max(cursor - 2, 0)

    show_top_dots = max_items < len(options) and window_start > 0
    show_bottom_dots = max_items < len(options) and window_start + max_items < len(
        options
    )

    visible_options = options[window_start : window_start + max_items]
    result = []

    for i, option in enumerate(visible_options):
        if (i == 0 and show_top_dots) or (
            i == len(visible_options) - 1 and show_bottom_dots
        ):
            result.append(Color.dim("..."))
        else:
            result.append(style(option, i + window_start == cursor))

    return result
