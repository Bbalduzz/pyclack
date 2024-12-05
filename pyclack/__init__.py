__all__ = ['Clack', 'Theme', 'Colors']

from .prompt import Prompt
from .themes import Theme
from .prompts.confirm import Confirm
from .prompts.text import Text, DinamicText
from .prompts.password import Password
from .prompts.multiselect import MultiSelect
from .prompts.group_multiselect import GroupMultiSelect
from .prompts.select import Select
from .prompts.spinner import Work as Spinner, SpinnerGroup
from .utils import Colors

class Clack(Prompt):
    def __init__(self):
        super().__init__()
        pass

    def text(self, dinamic=False, *args, **kwargs):
        if dinamic:
            return DinamicText(*args, **kwargs)
        return Text(*args, **kwargs)


    def password(self, *args, **kwargs):
        return Password(*args, **kwargs)

    def multiselect(self, *args, **kwargs):
        return MultiSelect(*args, **kwargs)

    def group_multiselect(self, *args, **kwargs):
        return GroupMultiSelect(*args, **kwargs)

    def select(self, *args, **kwargs):
        return Select(*args, **kwargs)

    def spinner(self, *args, **kwargs):
        return Spinner(*args, **kwargs)

    def spinner_group(self, *args, **kwargs):
        return SpinnerGroup(*args, **kwargs)

    def confirm(self, *args, **kwargs):
        return Confirm(*args, **kwargs)
