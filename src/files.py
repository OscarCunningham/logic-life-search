import pickle
import os
from src.logging import log


def string_from_file(file_name):
    """Read file into string"""
    log('Reading file "' + file_name + '" ...', 1)
    with open(file_name, "r") as pattern_file:
        input_string = pattern_file.read()
    log('Done\n', -1)
    return input_string


def file_from_string(file_name, input_string):
    """Write string to file"""
    log('Writing file "' + file_name + '" ...', 1)
    with open(file_name, "w") as output_file:
        output_file.write(input_string)
    log('Done\n', -1)


def append_to_file_from_string(file_name, input_string):
    """Append string to file"""
    log('Writing to file "' + file_name + '" ...', 1)
    with open(file_name, "a+") as output_file:
        output_file.write(input_string)
    log('Done\n', -1)


def file_from_object(file_name, input_object):
    """Write object to file"""
    log('Writing file "' + file_name + '" ...', 1)
    with open(file_name, "wb") as output_file:
        pickle.dump(input_object, output_file)
    log('Done\n', -1)


def object_from_file(file_name):
    """Load object from file"""
    log('Reading file "' + file_name + '" ...', 1)
    with open(file_name, "rb") as object_file:
        input_object = pickle.load(object_file)
    log('Done\n', -1)
    return input_object

def find_free_file_name(prefix, suffix):
    file_number = 0
    while True:
        file_name = prefix + str(file_number) + suffix
        if not os.path.isfile(file_name):
            break
        file_number += 1
    return file_name

