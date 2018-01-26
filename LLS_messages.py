import re

def print_message(message, needed_verbosity = 2, indent = 0, verbosity = 0):
    """Prints an output message (with the specified indent) if the verbosity is sufficiently high"""

    if verbosity >= needed_verbosity:
        
        lines = re.split("(?:\n|\r|(?:\r\n))", message) # Split on newline (or carriage return)

        for line in lines:
            print ("    " * indent) + line
