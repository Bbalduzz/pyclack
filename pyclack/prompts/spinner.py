from contextlib import asynccontextmanager
from functools import wraps
from pyclack.core import Spinner
from pyclack.utils.styling import Color


@asynccontextmanager
async def spinner(message: str = "", options=None):
    """Async context manager for showing a loading spinner.

    Args:
        message: Message to display next to spinner
        options: Dict with 'color' styling (defaults to magenta for spinner)

    Usage:
        async with spinner("Loading..."):
            await some_async_operation()
    """
    if options is None:
        options = {"color": Color.magenta}

    spin = Spinner()
    try:
        spin.start(message)
        yield spin
    finally:
        spin.stop()


def with_spinner(message: str = ""):
    """Decorator to add a spinner to an async function.

    Args:
        message: Message to display next to spinner

    Usage:
        @with_spinner("Loading...")
        async def my_function():
            await some_async_operation()
    """

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            async with spinner(message) as spin:
                try:
                    result = await func(*args, **kwargs)
                    return result
                except Exception as e:
                    spin.stop(str(e), code=2)
                    raise

        return wrapper

    return decorator
