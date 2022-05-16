import src.files
import src.formatting
import src.rules
from src.logging import log
from src.utilities import make_grid
from src.literal_manipulation import variable_from_literal, negate


def search_pattern_from_string(input_string):
    """Create the grid and ignore_transition of a search pattern from the given string"""
    grid, ignore_transition = src.formatting.parse_input_string(input_string)

    log("Pattern parsed as:",1)
    log(src.formatting.make_csv(grid, ignore_transition))
    log('Done\n',-1)

    for t, generation in enumerate(grid):
        for y, row in enumerate(generation):
            for x, cell in enumerate(row):
                if cell not in ["0", "1", "*"]:
                    variable, negated = variable_from_literal(cell)
                    grid[t][y][x] = negate("user_input_" + variable, negated)

    return grid, ignore_transition


def blank_search_pattern(width, height, duration):
    log('Creating spaceship search pattern...', 1)

    grid = make_grid('*', width, height, duration)

    log("Pattern created:\n" + src.formatting.make_csv(grid) + "\n")
    log('Done\n', -1)
    return grid
