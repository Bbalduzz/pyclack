from typing import Callable, Optional, Union
from core import PasswordPrompt, is_cancel
from utils.styling import Color, symbol, S_BAR, S_BAR_END, S_PASSWORD_MASK

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
            return (f"{title.rstrip()}\n"
                   f"{Color.red(S_BAR)}  {masked}\n"
                   f"{Color.red(S_BAR_END)}  {Color.red('Operation cancelled')}\n")
        else:
            return f"{title}{Color.cyan(S_BAR)}  {value}\n{Color.cyan(S_BAR_END)}\n"

    prompt = PasswordPrompt(render=render, mask=mask, validate=validate)
    result = await prompt.prompt()
    
    if is_cancel(result):
        return result

    print(f"{Color.gray(S_BAR)}  {Color.dim(S_PASSWORD_MASK * len(result))}")
    return result