import os

def get_terminal_type():
    """
    Detect terminal type to use appropriate escape sequences.
    More on: https://stackoverflow.com/questions/25879183/can-terminal-app-be-made-to-respect-ansi-escape-codes
    """
    term = os.environ.get('TERM', '')
    if 'xterm' in term:
        return 'xterm'
    elif 'screen' in term or 'tmux' in term:
        return 'screen'
    return 'unknown'

TERMINAL_TYPE = get_terminal_type()