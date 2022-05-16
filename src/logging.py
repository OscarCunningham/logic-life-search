import settings
from src.utilities import format_carriage_returns

indent_level = 0
verbosity_level = settings.verbosity

def log(message='', indent=0, verbosity_threshold=3):
    """Prints an output message (with the specified indent) if the verbosity is sufficiently high"""
    global verbosity_level

    if verbosity_level >= verbosity_threshold:
        global indent_level
        if indent < 0:
            indent_level += indent
        # Split on newline, carriage return or both
        lines = format_carriage_returns(message).split('\n')
        for line in lines:
            print(("    " * indent_level) + line)
        if indent > 0:
            indent_level += indent
