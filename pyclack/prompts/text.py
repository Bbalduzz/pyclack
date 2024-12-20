from typing import Callable, Optional, Union, Any
from pyclack.core import TextPrompt, MultilineTextPrompt, is_cancel
from pyclack.utils.styling import Color, symbol, S_BAR, S_BAR_END


async def text(
    message: str,
    placeholder: str = "",
    default_value: str = "",
    initial_value: str = "",
    validate: Optional[Callable[[str], Optional[str]]] = None,
) -> Union[str, object]:
    def render(prompt: TextPrompt) -> str:
        title = f"{Color.gray(S_BAR)}\n{symbol(prompt.state)}  {message}\n"
        placeholder_text = (
            Color.inverse(placeholder[0]) + Color.dim(placeholder[1:])
            if placeholder
            else Color.inverse(Color.hidden("_"))
        )
        value = placeholder_text if not prompt.value else prompt.value_with_cursor

        if prompt.state == "error":
            return (
                f"{title.rstrip()}\n"
                f"{Color.yellow(S_BAR)}  {value}\n"
                f"{Color.yellow(S_BAR_END)}  {Color.yellow(prompt.error)}\n"
            )
        elif prompt.state == "submit":
            return f"{Color.gray(S_BAR)}\n" f"{symbol(prompt.state)}  {message}\n"
        elif prompt.state == "cancel":
            return (
                f"{title.rstrip()}\n"
                f"{Color.red(S_BAR)}  {Color.dim(prompt.value) if prompt.value else placeholder_text}\n"
                f"{Color.red(S_BAR_END)}  {Color.red('Operation cancelled')}\n"
            )
        else:
            return f"{title}{Color.cyan(S_BAR)}  {value}\n{Color.cyan(S_BAR_END)}\n"

    prompt = TextPrompt(
        render=render,
        placeholder=placeholder,
        initial_value=initial_value,
        default_value=default_value,
        validate=validate,
    )
    result = await prompt.prompt()

    if is_cancel(result):
        return result

    print(f"{Color.gray(S_BAR)}  {Color.dim(result)}")
    return result


async def multiline_text(
    message: str,
    placeholder: str = "",
    default_value: str = "",
    initial_value: str = "",
    validate: Optional[Callable[[str], Optional[str]]] = None,
) -> Union[str, object]:
    def render(prompt: MultilineTextPrompt) -> str:
        output = []

        output.append(f"{Color.gray(S_BAR)}")
        output.append(f"{symbol(prompt.state)}  {message}")

        placeholder_text = (
            Color.inverse(placeholder[0]) + Color.dim(placeholder[1:])
            if placeholder
            else Color.inverse(Color.hidden("_"))
        )

        value_lines = (
            prompt.value_with_cursor.split("\n") if prompt.value else [placeholder_text]
        )

        for i, line in enumerate(value_lines):
            if i == len(value_lines) - 1:  # Last line
                output.append(f"{Color.cyan(S_BAR)}  {line}")
                output.append(f"{Color.cyan(S_BAR_END)}")
            else:  # Middle lines
                output.append(f"{Color.cyan(S_BAR)}  {line}")

        if prompt.state == "error":
            output.append(f"{Color.yellow(S_BAR)}  {Color.yellow(prompt.error)}")
        elif prompt.state == "submit":
            output = [f"{Color.gray(S_BAR)}", f"{symbol(prompt.state)}  {message}"]
            lines = prompt.value.split("\n")
            for line in lines:
                output.append(f"{Color.gray(S_BAR)}  {Color.dim(line)}")
        elif prompt.state == "cancel":
            output.append(
                f"{Color.red(S_BAR)}  {Color.dim(prompt.value) if prompt.value else placeholder_text}"
            )
            output.append(f"{Color.red(S_BAR_END)}  {Color.red('Operation cancelled')}")

        return "\n".join(output) + "\n"

    prompt = MultilineTextPrompt(
        render=render,
        placeholder=placeholder,
        initial_value=initial_value,
        default_value=default_value,
        validate=validate,
    )

    result = await prompt.prompt()
    return result if is_cancel(result) else result
