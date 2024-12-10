from typing import List, Any, Optional, Union, Any
from core import SelectPrompt, Option, is_cancel
from utils.styling import Color, symbol, limit_options, S_BAR, S_BAR_END, S_RADIO_ACTIVE, S_RADIO_INACTIVE

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
            styled_options = limit_options(
                options=prompt.options,
                cursor=prompt.cursor,
                max_items=max_items,
                style=lambda item, active: opt(item, 'cancelled')
            )
            return (f"{title}{Color.red(S_BAR)}  "
                f"{f'\n{Color.red(S_BAR)}  '.join(styled_options)}\n"
                f"{Color.red(S_BAR_END)}  {Color.red('Operation cancelled')}\n")
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