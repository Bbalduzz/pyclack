"""
Group functionality for pyclack prompts.
"""
from typing import Any, Callable, Dict, Optional, TypeVar, Generic, Union, Awaitable
from .prompt import is_cancel

T = TypeVar('T', bound=Dict[str, Any])
PromptResult = Union[Any, None]


class PromptGroupOptions(Generic[T]):
    """Options for prompt groups."""
    
    def __init__(self, on_cancel: Optional[Callable[[Dict[str, Any]], None]] = None):
        """
        Initialize prompt group options.
        
        Args:
            on_cancel: Function to call when a prompt is canceled
        """
        self.on_cancel = on_cancel


async def group(prompts: Dict[str, Callable[[Dict[str, Any]], Awaitable[PromptResult]]], 
                options: Optional[PromptGroupOptions] = None) -> Dict[str, Any]:
    """
    Define a group of prompts to be displayed and return results of objects within the group.
    
    Args:
        prompts: Dictionary of prompt functions
        options: Optional configuration for the prompt group
    
    Returns:
        Dictionary of prompt results
    """
    results: Dict[str, Any] = {}
    prompt_names = list(prompts.keys())
    
    for name in prompt_names:
        prompt = prompts[name]
        try:
            result = await prompt({"results": results})
        except Exception as e:
            raise e
        
        # Pass the results to the on_cancel function
        # so the user can decide what to do with the results
        if options and options.on_cancel and is_cancel(result):
            results[name] = "canceled"
            options.on_cancel({"results": results})
            continue
        
        results[name] = result
    
    return results