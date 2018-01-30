import re, copy
import LLS_rules
from LLS_messages import print_message
from LLS_literal_manipulation import negate, variable_from_literal, neighbours_from_coordinates, implies

def parse_input_string(input_string, indent = 0, verbosity = 0):
    """Transforms a "search pattern" given as a string into a SearchPattern"""

    print_message("Parsing input pattern...", 3, indent = indent, verbosity = verbosity)

    # Remove any trailing (or leading) whitespace and commas
    input_string = input_string.strip(", \t\n\r\f\v")

    # Break down string into list-of-lists-of-lists
    split_by_generation = re.split("[ ,\t]*(?:\n|\r|(?:\r\n))(?:[ ,\t]*(?:\n|\r|(?:\r\n)))+[ ,\t]*", # Split on at least two newlines (or carriage returns) and any commas or spaces
                                   input_string)
    split_by_line = [re.split("[ ,\t]*(?:\n|\r|(?:\r\n))[ ,\t]*", # Split on signle newline (or carriage return) and any ammount of commas or spaces
                     generation)
                     for generation in split_by_generation]
    grid = [[re.split("[ ,\t]*",  # Split on any amount of commas or spaces
                    line)
                    for line in generation]
                    for generation in split_by_line]

    # Check that the list is cuboidal
    assert (all(
               len(generation) == len(grid[0])
               for generation in grid)
            and all(all(
               len(line) == len(grid[0][0])
               for line in generation) for generation in grid)), \
           "Search pattern is not cuboidal"

    # Tidy up any weird inputs
    grid = [[[standard_form_literal(cell)
                      for cell in row] for row in generation] for generation in grid]

    # Create array which says when a "'" means that a transition should be ignored
    ignore_transition = [[[(cell[-1] == "'")
                      for cell in row] for row in generation] for generation in grid]
    grid = [[[cell.rstrip("'") # The "'"s are now unnecessary
                      for cell in line] for line in generation] for generation in grid]

    # #Check that "" isn't being used as a variable name
    # assert all(all(all(
    #     cell not in ["","-"]
    #     for cell in row) for row in generation) for generation in grid), \
    #     "Malformed input and/or null string used as variable name"

    print_message("Done\n", 3, indent = indent, verbosity = verbosity)

    return grid, ignore_transition

def make_rle(grid, rule = None, determined = None, indent = 0, verbosity = 0):
    """Turn a search pattern into nicely formatted string form"""

    print_message('Format: RLE', 3, indent = indent, verbosity = verbosity)

    grid = copy.deepcopy(grid)

    width = len(grid[0][0])
    height = len(grid[0])

    for t, generation in enumerate(grid):
        for y, row in enumerate(generation):
            for x, cell in enumerate(row):
                assert cell in ["0","1"], "Cell not equal to 0 or 1 in RLE format"
                if cell == "0":
                    grid[t][y][x] = "b"
                elif cell == "1":
                    grid[t][y][x] = "o"

    rle_string = "x = " + str(width) + ", y = " + str(height)

    if rule != None:
        rle_string += ", rule = " + LLS_rules.rulestring_from_rule(rule)

    rle_string += "\n"

    rle_string += "$\n".join("".join(line)for line in grid[0])

    rle_string += "!"

    if not determined:
        rle_string += "\n\nOther generations:\n"
        rle_string += "\n\n".join("$\n".join("".join(line) for line in generation) for generation in grid[1:])


    return rle_string




def make_csv(grid, ignore_transition = None, rule = None, determined = None, indent = 0, verbosity = 0):
    """Turn a search pattern in list form into nicely formatted csv string"""

    print_message('Format: csv', 3, indent = indent, verbosity = verbosity)

    grid = copy.deepcopy(grid)
    if ignore_transition == None:
        ignore_transition = [[[False for cell in row] for row in generation] for generation in grid]

    lengths = []
    for t, generation in enumerate(grid):
        for y, row in enumerate(generation):
            for x, cell in enumerate(row):
                if x != 0:
                    lengths.append(len(cell) + ignore_transition[t][y][x-1])

    length_first_column = max([max([
                                    len(row[0])
                          for row in generation]) for generation in grid])
    if len(lengths) > 0:
        length_other_columns = max(lengths)
    for t, generation in enumerate(grid):
        for y, row in enumerate(generation):
            for x, cell in enumerate(row):
                if x == 0:
                    grid[t][y][x] = " " * (length_first_column - len(cell)) +  cell
                else:
                    grid[t][y][x] = " " * (length_other_columns - len(cell) - ignore_transition[t][y][x-1]) +  grid[t][y][x]
                if ignore_transition[t][y][x]:
                    grid[t][y][x] += "'"

    csv_string = ""

    if rule != None:
        csv_string += "Rule = " + LLS_rules.rulestring_from_rule(rule) + "\n"

    csv_string += "\n".join(",".join(line)for line in grid[0])

    if not determined:
        csv_string += "\n\n" + "\n\n".join("\n".join(",".join(line) for line in generation) for generation in grid[1:])


    return csv_string


def standard_form_literal(cell):
    """Tidies up a cell into a standard form"""

    cell = re.sub('\xe2\x80\x99', "'", cell) # Replace alternative "'" character
    cell = re.sub("'+$", "'", cell)  # Remove duplicate "'"s
    cell = re.sub("^(:?--)*", "", cell)  # Cancel double "-" signs
    # Other simplifications
    to_replace   = ["-*", "-*'", "-0", "-0'", "-1", "-1'"]
    replacements = [ "*",  "*'",  "1",  "1'",  "0",  "0'"]
    if cell in to_replace:
        cell = replacements[to_replace.index(cell)]

    return cell
