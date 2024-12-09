from .password import PasswordPrompt
from .text import TextPrompt
from .confirm import ConfirmPrompt
from .select import SelectPrompt
from .multiselect import MultiSelectPrompt, Option
from .select_key import SelectKeyPrompt
from .prompt import is_cancel
from .spinner import Spinner

from typing import Any
from dataclasses import dataclass
@dataclass
class Option:
    value: Any
    label: str = ''
    hint: str = ''