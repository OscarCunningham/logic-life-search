import re
import os
import copy
from src.rules import rulestring_from_rule
from src.logging import log
from src.utilities import format_carriage_returns, make_grid
from src.literal_manipulation import standard_form_literal


# get the nth (0-indexed) curly brace array from the given line
def get_array(line, n):
    return eval('[' + re.findall(r"\{(.*?)\}", line)[n] + ']')


def parse_jdf(input_string):
    # JLS cell states
    OFF              = 0
    ON               = 1
    EMPTY            = 2
    UNCHECKED        = 6    # 'X'
    UNSET            = 10   # '#' Obtained in JLS by selecting a cell and pressing 'U'.
    FROZEN           = 18   # 'F'
    UNCHECKED_FROZEN = 22   # Obtained in JLS by selecting a frozen cell and pressing 'O'.

    cell_rows = []
    cell_array = []
    subperiod_array = []

    # Read the JLS status file and extract important info
    for line in input_string.splitlines():

        # Get width, height, and depth
        if line.startswith("columns="):
            columns = eval(line.split("=")[1])

        if line.startswith("rows="):
            rows = eval(line.split("=")[1])

        if line.startswith("generations="):
            generations = eval(line.split("=")[1])

        # Element 0 of subperiods is the full period (same as generations), and elements 1 through 6 are the subperiods
        if line.startswith("periods="):
            subperiods = get_array(line,0)

        # Get the cell array as a big list of row arrays. We'll organize this later.
        if line.startswith("cells"):
            cell_rows.append(get_array(line,1))

        # To get the subperiod settings for each cell, we must reduce every entry in the "stacks" array mod 8.
        if line.startswith("stacks"):
            subperiod_array.append(list(map(lambda x: x % 8, get_array(line,1))))

        # Lines after "[Search]" represent the search state. We only want the initial setup.
        if line.startswith("[Search]"):
            break

    # Convert our list of cell rows into a 3D array
    for gen in range(generations):
        cell_array.append(cell_rows[gen*rows:(gen+1)*rows])

    # Set the sixth subperiod to be the full period. We only use
    # it to identify cells that do not need to obey the CA rules
    subperiods[6] = generations

    # For each cell in cell_array, set the corresponding variable name in lls_array
    lls_array = [[["" for k in range(columns)] for j in range(rows)] for i in range(generations)]
    for gen in range(generations):
        for row in range(rows):
            for column in range(columns):
                the_cell = cell_array[gen][row][column]
                if the_cell == OFF:
                    lls_array[gen][row][column] = "0"
                elif the_cell == ON:
                    lls_array[gen][row][column] = "1"
                elif gen == 0 or the_cell == EMPTY or the_cell == UNCHECKED or the_cell == UNSET:
                    lls_array[gen][row][column] = "x" + str(gen % subperiods[subperiod_array[row][column]]) + "_" + str(row) + "_" + str(column)
                elif the_cell == FROZEN or the_cell == UNCHECKED_FROZEN:
                    lls_array[gen][row][column] = lls_array[gen - 1][row][column]

                # Special suffix so that unchecked cells don't have to have to obey subperiodicity
                if the_cell == UNCHECKED:
                    lls_array[gen][row][column] += "_uc" + str(gen)

                # apostrophe suffix means the cell does not need to obey the CA rules
                if the_cell == UNSET or subperiod_array[row][column] == 6:
                    lls_array[gen][row][column] += "'"

    # We have to do a second pass of generation 0 in case it contains any frozen cells
    for row in range(rows):
        for column in range(columns):
            the_cell = cell_array[0][row][column]
            if the_cell == FROZEN or the_cell == UNCHECKED_FROZEN:
                lls_array[0][row][column] = lls_array[generations - 1][row][column]

    # Create the LLS input file text
    lls_input = ""

    for gen in range(generations):
        for row in range(rows):
            for column in range(columns):
                lls_input += lls_array[gen][row][column] + ","
            lls_input += "\n"
        if gen == 0:
            gen_zero = lls_input
        lls_input += "\n"

    lls_input += gen_zero

    return lls_input


def parse_input_string(input_string):
    """Parses a search pattern given as a string"""

    log("Parsing input pattern...", 1)

    if input_string.startswith("# JavaLifeSearch status file"):
        input_string = parse_jdf(input_string)

    input_string = format_carriage_returns(input_string)

    # Remove any comments
    input_string = re.sub('#.*', '', input_string)

    # Remove any trailing or leading whitespace and commas
    input_string = input_string.strip(" ,\t\n")

    # Break down string into list-of-lists-of-lists
    split_by_generation = re.split(
        r"[ ,\t]*\n(?:[ ,\t]*\n)+[ ,\t]*",  # Split on at least two newlines and any spaces, commas or tabs
        input_string
    )
    split_by_line = [
        re.split(
            r"[ ,\t]*\n[ ,\t]*",  # Split on single newline and any amount of commas or spaces
            generation
        )
        for generation in split_by_generation]
    grid = [[
        re.split(
            r"[ ,\t]+",  # Split on any amount of commas or spaces
            line
        )
        for line in generation] for generation in split_by_line]

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
    ignore_transition = [[[(cell[-1] in "'’")
                           for cell in row] for row in generation] for generation in grid]
    grid = [[[cell.rstrip("'’")  # The "'"s are now unnecessary
              for cell in row] for row in generation] for generation in grid]

    log("Done\n", -1)

    return grid, ignore_transition


def make_jdf(grid):
    """Turn a search pattern into a JLS status file"""

    log('Format: jdf')

    width = len(grid[0][0])
    height = len(grid[0])
    duration = len(grid)

    jdf_string = "[Properties]\n\ncolumns=" \
                + str(width-2) \
                + "\nrows=" + str(height-2) \
                + "\ngenerations=" + str(duration-1) \
                + "\nperiods={" + str(duration-1) + ",1,2,3,4,5,6}\n"

    with open(os.path.dirname(os.path.realpath(__file__)) + "/jls_defaults", "r") as file:
        jdf_string += file.read()
        #for line in file:
        #    jdf_string += line

    stacks_rows = [["0"]*(width-2) for y in range(height-2)]

    for x in range(1,width-1):
        for y in range(1,height-1):
            for t in range(duration):
                if grid[t][y][x] != grid[0][y][x]:
                    stacks_rows [y-1][x-1] = "16"

    for t, generation in enumerate(grid):
        if t == duration-1:
            continue
        for y, row in enumerate(generation):
            if y == 0 or y == height-1:
                continue
            jdf_string += "cells{" + str(t) + "," + str(y-1) + "}={" + ",".join(row[1:-1]) + "}\n"
        jdf_string += "\n"

    stacks_string = ""
    for y, row in enumerate(stacks_rows):
        stacks_string += "stacks{" + str(y) + "}={" + ",".join(row) + "}\n"

    jdf_string += stacks_string

    return jdf_string


def make_rle(grid, background_grid=None, rule=None, determined=None, show_background=None):
    """Turn a search pattern into nicely formatted string form"""

    log('Format: RLE')

    grid = copy.deepcopy(grid)

    width = len(grid[0][0])
    height = len(grid[0])

    for t, generation in enumerate(grid):
        for y, row in enumerate(generation):
            for x, cell in enumerate(row):
                assert cell in ["0", "1"], "Cell not equal to 0 or 1 in RLE format"
                if cell == "0":
                    grid[t][y][x] = "b"
                elif cell == "1":
                    grid[t][y][x] = "o"

    rle_string = "x = " + str(width) + ", y = " + str(height)

    if rule is not None:
        rle_string += ", rule = " + rulestring_from_rule(rule)

    rle_string += "\n"

    rle_string += "$\n".join("".join(line) for line in grid[0])

    rle_string += "!\n"

    if not determined:
        rle_string += "\nOther generations:\n"
        rle_string += "\n\n".join("$\n".join("".join(line) for line in generation) for generation in grid[1:]) + "\n"

    if show_background:
        rle_string += "\nBackground:\n"
        background_grid = copy.deepcopy(background_grid)

        for t, generation in enumerate(background_grid):
            for y, row in enumerate(generation):
                for x, cell in enumerate(row):
                    assert cell in ["0", "1"], "Cell not equal to 0 or 1 in RLE format"
                    if cell == "0":
                        background_grid[t][y][x] = "b"
                    elif cell == "1":
                        background_grid[t][y][x] = "o"

        rle_string += "\n\n".join(
            "$\n".join("".join(line) for line in generation) for generation in background_grid) + "\n"

    return rle_string


def make_csv(
        grid,
        ignore_transition=None,
        background_grid=None,
        background_ignore_transition=None,
        rule=None,
        determined=None,
        show_background=None
):
    """Turn a search pattern in list form into nicely formatted csv string"""

    log('Format: csv')

    grid = space_evenly(grid, ignore_transition)

    csv_string = ""

    if rule is not None:
        csv_string += "Rule = " + rulestring_from_rule(rule) + "\n"

    csv_string += "\n".join(",".join(line) for line in grid[0]) + "\n"

    if not determined:
        csv_string += "\n" + "\n\n".join(
            "\n".join(",".join(line) for line in generation) for generation in grid[1:]) + "\n"

    if show_background:
        csv_string += "\nBackground:\n"
        background_grid = space_evenly(background_grid, background_ignore_transition)
        csv_string += "\n" + "\n\n".join(
            "\n".join(",".join(line) for line in generation) for generation in background_grid) + "\n"

    return csv_string


def space_evenly(grid, ignore_transition=None):
    grid = copy.deepcopy(grid)
    if ignore_transition is None:
        ignore_transition = make_grid(False, template=grid)

    lengths = []
    for t, generation in enumerate(grid):
        for y, row in enumerate(generation):
            for x, cell in enumerate(row):
                if x != 0:
                    lengths.append(len(cell) + ignore_transition[t][y][x - 1])

    length_first_column = max([max([
        len(row[0])
        for row in generation]) for generation in grid])
    length_other_columns = max(lengths) if lengths else 0
    for t, generation in enumerate(grid):
        for y, row in enumerate(generation):
            for x, cell in enumerate(row):
                if x == 0:
                    grid[t][y][x] = " " * (length_first_column - len(cell)) + cell
                else:
                    grid[t][y][x] = " " * (length_other_columns - len(cell) - ignore_transition[t][y][x - 1]) + \
                                    grid[t][y][x]
                if ignore_transition[t][y][x]:
                    grid[t][y][x] += "'"

    return grid
