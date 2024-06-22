import platform
from pprint import pformat
from typing import Any


def is_windows_7():
    system = platform.system()
    release = platform.release()
    return system == 'Windows' and release == '7'

# from pygments import highlight
# from pygments.formatters import Terminal256Formatter
# from pygments.lexers import PythonLexer


# # https://gist.github.com/EdwardBetts/0814484fdf7bbf808f6f
# def pprint_color(obj: Any) -> None:
#     """Pretty-print in color."""
#     print(highlight(pformat(obj), PythonLexer(), Terminal256Formatter()), end="")
#     # print( highlight(pformat(obj), PythonLexer(), Terminal256Formatter()) )

def green(text):
    if is_windows_7():
        return f'* {text}'
    return f"\033[32m{text}\033[39m"


def yellow(text):
    if is_windows_7():
        return f'* {text}'
    return f"\033[33m{text}\033[0m"

def red(text):
    if is_windows_7():
        return f'* {text}'
    return f"\033[31m{text}\033[0m"

def blue(text):
    if is_windows_7():
        return f'* {text}'
    return f"\033[94m{text}\033[0m"


def key_visualize(key):
    if key.lower() == 'ctrl':
        return 'Ctrl'
    if key.lower() == 'alt':
        return 'Alt'    
    if key.lower() == 'shift':
        return 'Shift'

    if key.lower() == 'up':
        return '↑'
    if key.lower() == 'down':
        return '↓'
    if key.lower() == 'left':
        return '←'
    if key.lower() == 'right':
        return '→'
    
    return key