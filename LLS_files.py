from LLS_messages import print_message



def string_from_file(file_name, indent = 0, verbosity = 0):
    """Read pattern file into string"""
    print_message('Reading file "' + file_name + '" ...', 3, indent = indent, verbosity = verbosity)
    with open(file_name, "r") as pattern_file:
        input_string = pattern_file.read()
    print_message('Done\n', 3, indent = indent, verbosity = verbosity)
    return input_string


def file_from_string(file_name, input_string, indent = 0, verbosity = 0):
    """Write string to file"""
    print_message('Writing file "' + file_name + '" ...', 3, indent = indent, verbosity = verbosity)
    with open(file_name, "w") as output_file:
        output_file.write(input_string)
    print_message('Done\n', 3, indent = indent, verbosity = verbosity)

def append_to_file_from_string(file_name, input_string, indent = 0, verbosity = 0):
    """Append string to file"""
    print_message('Writing to file "' + file_name + '" ...', 3, indent = indent, verbosity = verbosity)
    with open(file_name, "a+") as output_file:
        output_file.write(input_string)
    print_message('Done\n', 3, indent = indent, verbosity = verbosity)
