from .utils import *
from enum import Enum, unique

class BaseTheme:
    title_color = Colors.white
    title_bg_color = Colors.red
    outro_color = Colors.white
    text_color = Colors.white
    secondary_color = Colors.grey
    default_color = Colors.cyan
    cursor_color = Colors.green
    note_color = Colors.green
    bar_color = Colors.grey
    submitted_bar_color = Colors.grey
    error_color = Colors.yellow
    cancel_color = Colors.red

class DarkModeTheme(BaseTheme):
    title_bg_color = Colors.bg_black
    default_color = Colors.white
    cursor_color = Colors.red
    error_color = Colors.red
    bar_color = Colors.grey

class LightModeTheme(BaseTheme):
    title_color = Colors.black
    title_bg_color = Colors.bg_white
    outro_color = Colors.black
    text_color = Colors.grey
    default_color = Colors.black
    cursor_color = Colors.black
    bar_color = Colors.black


@unique
class Theme(Enum):
    DEFAULT = BaseTheme
    DARK_MODE = DarkModeTheme
    LIGHT_MODE = LightModeTheme

    @classmethod
    def list(cls):
        return list(map(lambda c: c.name, cls))

theme_classes = {theme: theme.value for theme in Theme}
