from typing import Callable, Optional, Union, Any
from pyclack.core import TextPrompt, is_cancel
from pyclack.utils.styling import Color, symbol, S_BAR, S_BAR_END

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
            return (f"{title.rstrip()}\n"
                   f"{Color.red(S_BAR)}  {Color.dim(prompt.value) if prompt.value else placeholder_text}\n"
                   f"{Color.red(S_BAR_END)}  {Color.red('Operation cancelled')}\n")
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