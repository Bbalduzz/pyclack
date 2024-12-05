from dataclasses import dataclass
import readchar
import sys
import os
import re

CURSOR_UP = "\033[1A"
CURSOR_DOWN = "\033[1B"
CLEAR = "\x1b[2K"
CLEAR_LINE =  CURSOR_UP + CLEAR

PROMPT_EVENT_LISTENERS = ["on_cancel"]

@dataclass
class SymbolSet:
    step_active: str = '◆'
    step_cancel: str = '■'
    step_error: str = '▲'
    step_submit: str = '◇'
    cursor: str = '➤'
    bar_start: str = '┌'
    bar: str = '│'
    bar_end: str = '└'
    radio_active: str = '◉'
    radio_inactive: str = '○'
    checkbox_active: str = '◻'
    checkbox_selected: str = '◼'
    checkbox_inactive: str = '◻'
    password_mask: str = '▪'
    bar_h: str = '─'
    corner_top_right: str = '╮'
    connect_left: str = '├'
    corner_bottom_right: str = '╯'
    info: str = '●'
    success: str = '◆'
    warn: str = '▲'
    error: str = '■'
    next: str = '▶'

@dataclass
class Colors:
    underline = "\u001b[4m"
    bg_blue = "\u001b[44m"
    bg_cyan = "\u001b[46m"
    bg_grey = "\u001b[100m"
    bg_black = "\u001b[40m"
    bg_white = "\u001b[47m"
    bg_magenta = "\u001b[45m"
    black = "\u001b[30m"
    red = "\u001b[31m"
    green = "\u001b[32m"
    yellow = "\u001b[33m"
    blue = "\u001b[34m"
    magenta = "\u001b[35m"
    cyan = "\u001b[36m"
    white = "\u001b[37m"
    grey = "\u001b[90m"
    reset = "\u001b[0m"
