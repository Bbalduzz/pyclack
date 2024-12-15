from typing import List, Any, Optional, Union, Any
from pyclack.core import MultiSelectPrompt, Option, is_cancel
from pyclack.utils.styling import (
    Color,
    symbol,
    limit_options,
    S_BAR,
    S_BAR_END,
    S_CHECKBOX_ACTIVE,
    S_CHECKBOX_SELECTED,
    S_CHECKBOX_INACTIVE,
)


async def multiselect(
    message: str,
    options: List[Option],
    initial_values: List[Any] = None,
    max_items: Optional[int] = None,
    required: bool = True,
    cursor_at: Any = None,
) -> Union[List[Any], object]:

    def render(prompt: MultiSelectPrompt) -> str:
        def opt(option: Option, state: str) -> str:
            label = option.label or str(option.value)
            if state == "active":
                return (
                    f"{Color.cyan(S_CHECKBOX_ACTIVE)} {label} "
                    f"{option.hint and Color.dim(f'({option.hint})') or ''}"
                )
            elif state == "selected":
                return f"{Color.green(S_CHECKBOX_SELECTED)} {Color.dim(label)}"
            elif state == "cancelled":
                return Color.strikethrough(Color.dim(label))
            elif state == "active-selected":
                return (
                    f"{Color.green(S_CHECKBOX_SELECTED)} {label} "
                    f"{option.hint and Color.dim(f'({option.hint})') or ''}"
                )
            elif state == "submitted":
                return Color.dim(label)
            return f"{Color.dim(S_CHECKBOX_INACTIVE)} {Color.dim(label)}"

        title = f"{Color.gray(S_BAR)}\n{symbol(prompt.state)}  {message}\n"

        if prompt.state == "submit":
            selected = [opt for opt in prompt.options if opt.value in prompt.value]
            selected_labels = [opt.label for opt in selected]
            return f"{Color.gray(S_BAR)}\n" f"{symbol(prompt.state)}  {message}\n"

        if prompt.state == "cancel":
            styled_options = limit_options(
                options=prompt.options,
                cursor=prompt.cursor,
                max_items=max_items,
                style=lambda item, active: opt(
                    item, "cancelled" if item.value in prompt.value else "inactive"
                ),
            )
            return (
                f"{title}{Color.red(S_BAR)}  "
                f"{f'\n{Color.red(S_BAR)}  '.join(styled_options)}\n"
                f"{Color.red(S_BAR_END)}  {Color.red('Operation cancelled')}\n"
            )
        elif prompt.state == "error":
            footer = prompt.error.split("\n")
            footer = [
                f"{Color.yellow(S_BAR_END)}  {Color.yellow(footer[0])}",
                *[f"   {line}" for line in footer[1:]],
            ]
            styled_options = limit_options(
                options=prompt.options,
                cursor=prompt.cursor,
                max_items=max_items,
                style=lambda item, active: opt(
                    item,
                    (
                        "active-selected"
                        if active and item.value in prompt.value
                        else (
                            "selected"
                            if item.value in prompt.value
                            else "active" if active else "inactive"
                        )
                    ),
                ),
            )
            return (
                f"{title}{Color.yellow(S_BAR)}  "
                f"{f'\n{Color.yellow(S_BAR)}  '.join(styled_options)}\n"
                f"{'\n'.join(footer)}\n"
            )
        else:
            styled_options = limit_options(
                options=prompt.options,
                cursor=prompt.cursor,
                max_items=max_items,
                style=lambda item, active: opt(
                    item,
                    (
                        "active-selected"
                        if active and item.value in prompt.value
                        else (
                            "selected"
                            if item.value in prompt.value
                            else "active" if active else "inactive"
                        )
                    ),
                ),
            )
            return (
                f"{title}{Color.cyan(S_BAR)}  "
                f"{f'\n{Color.cyan(S_BAR)}  '.join(styled_options)}\n"
                f"{Color.cyan(S_BAR_END)}\n"
            )

    prompt = MultiSelectPrompt(
        render=render,
        options=options,
        initial_values=initial_values,
        required=required,
        cursor_at=cursor_at,
        debug=False,
    )
    result = await prompt.prompt()

    if is_cancel(result):
        return result

    # Print final state
    selected = [opt for opt in options if opt.value in result]
    print(f"{Color.gray(S_BAR)}  {Color.dim(', '.join(opt.label for opt in selected))}")

    return result
