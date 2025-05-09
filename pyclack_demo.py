"""
demo file
"""
from pyclack.core import group, PromptGroupOptions
from pyclack.prompts import *
import asyncio


async def simulate_install():
    """Simulate installation process with updates."""
    await asyncio.sleep(1)
    return "Installation complete!"


@with_spinner("Installing dependencies...")
async def install_deps():
    """Example of using spinner as a decorator."""
    await asyncio.sleep(2)
    return "Dependencies installed!"


async def main():
    # Intro
    intro("pyclack")

    # Project location
    project_path = await text(
        message="Where should we create your project?",
        placeholder=".",
        initial_value=".",
    )
    if is_cancel(project_path):
        return

    textarea = await multiline_text(
        message="Enter your multiline text (Ctrl + J for new line):",
        placeholder="Start typing...",
    )
    if is_cancel(textarea):
        return

    pwd = await password(
        message="Enter your secret",
        validate=lambda x: "password is too short" if len(x) < 5 else None,
    )
    if is_cancel(pwd):
        return

    # Project type
    project_type = await select(
        message=f'Pick a project type within "{project_path}"',
        options=[
            Option("typescript", "TypeScript"),
            Option("javascript", "JavaScript"),
        ],
        initial_value="typescript",
    )
    if is_cancel(project_type):
        return

    # Tools selection
    tools = await multiselect(
        message="Select additional tools.",
        options=[
            Option("prettier", "Prettier"),
            Option("eslint", "ESLint"),
            Option("jest", "Jest"),
        ],
        initial_values=["prettier", "eslint"],
    )
    if is_cancel(tools):
        return

    # Install dependencies
    install = await confirm(
        message="Install dependencies?", active="Yes", inactive="No", initial_value=True
    )
    if is_cancel(install):
        return

    if install:
        # Method 1: Using context manager
        async with spinner("Setting up project...") as spin:
            await asyncio.sleep(1)
            spin.update("Installing packages...")
            await asyncio.sleep(1)
            spin.update("Configuring tools...")
            await asyncio.sleep(1)
            spin.update("Dependencies installed!")

        # Method 2: Using decorated function
        # await install_deps()

    # Next steps
    steps = ["cd .", "pnpm dev"]

    note(title="Next steps.", content=steps)
    outro(
        f"{Color.dim(f'Problems? {link(url='https://github.com/Bbalduzz/pyclack')}')}"
    )

async def group_main():
    intro("pyclack")

    user_info = await group({
        "project_path": lambda _: text(
            message="Where should we create your project?",
            placeholder=".",
            initial_value=".",
        ),
        "textarea": lambda _: multiline_text(
            message="Enter your multiline text (Ctrl + J for new line):",
            placeholder="Start typing...",
        ),
        "password": lambda _: password(
            message="Enter your secret",
            validate=lambda x: "password is too short" if len(x) < 5 else None,
        )
    }, PromptGroupOptions(
        on_cancel=lambda results: print(f"Canceled with partial results: {results}")
    ))

    note(title="Group results:", content=[f"user_info: {user_info}"])
    outro("Bye!")
    if any(is_cancel(value) for value in user_info.values()):
        return

if __name__ == "__main__":
    import sys
    if sys.argv[1] == "group":
        asyncio.run(group_main())
    elif sys.argv[1] == "main":
        asyncio.run(main())
