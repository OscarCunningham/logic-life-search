import copy
import src.LLS_files as LLS_files
import src.LLS_formatting as LLS_formatting
import src.LLS_rules as LLS_rules
import src.LLS_defaults as LLS_defaults
from src.SearchPattern import SearchPattern
from src.LLS_messages import print_message
from src.LLS_literal_manipulation import neighbours_from_coordinates, variable_from_literal, negate


def search_pattern_from_string(input_string, indent = 0, verbosity = 0):
    """Create the grid and ignore_transitionof a search pattern from the given string"""
    grid, ignore_transition = LLS_formatting.parse_input_string(input_string, indent = indent, verbosity = verbosity)

    print_message(
        "Pattern parsed as:\n" + LLS_formatting.make_csv(grid, ignore_transition) + "\n",
        3,
        indent = indent, verbosity = verbosity
    )

    for t, generation in enumerate(grid):
        for y, row in enumerate(generation):
            for x, cell in enumerate(row):
                if cell not in ["0", "1", "*"]:
                    variable, negated = variable_from_literal(cell)
                    grid[t][y][x] = negate("user_input_" + variable, negated)

    return grid, ignore_transition


def blank_search_pattern(width, height, duration, indent = 0, verbosity = 0):
    print_message('Creating spaceship search pattern...', 3, indent = indent, verbosity = verbosity)

    grid = [[["*" for i in range(width)] for j in range(height)] for k in range(duration)]

    print_message("Pattern created:\n" + LLS_formatting.make_csv(grid) + "\n", 3, indent = indent+1, verbosity = verbosity)
    print_message('Done\n', 3, indent = indent, verbosity = verbosity)
    return grid

def check_orphan(file_name, number_of_generations, indent = 0, verbosity = 0):
    print_message(
        'Creating search pattern to see if file "' + file_name + '" contains an orphan...',
        3,
        indent = indent, verbosity = verbosity
    )
    input_string = LLS_files.string_from_file(file_name, indent = indent + 1, verbosity = verbosity)
    grid, _ = LLS_formatting.parse_input_string(input_string, indent = indent + 1, verbosity = verbosity)
    assert len(grid) == 1, "More than one generation in input"
    print_message(
        "Pattern parsed as:\n" + LLS_formatting.make_csv(grid) + "\n",
        3,
        indent = indent+1, verbosity = verbosity
    )

    pattern = grid[0]
    width = len(pattern[0])
    height = len(pattern)

    padding = number_of_generations
    pattern = [["*" for columns in range(padding)] + row + ["*" for columns in range(padding)] for row in [["*" for cell in range(
        width)] for rows in range(padding)] + pattern + [["*" for cell in range(width)] for rows in range(padding)]]

    width = len(pattern[0])
    height = len(pattern)
    duration = number_of_generations + 1

    grid = [[["0" for cell in range(width)] for row in range(
        height)] for generation in range(number_of_generations)] + [pattern]
    ignore_transition = [[[True for cell in range(width)] for row in range(
        height)] for generation in range(number_of_generations)] + [[[False for cell in range(width)] for row in range(
            height)]]

    for t in range(number_of_generations - 1, -1, -1):
        for y in range(height):
            for x in range(width):
                if t == number_of_generations - 1:
                    neighbours = neighbours_from_coordinates(grid,x,y,t,t_offset=1,background_grid=[[["*"]]])
                    nonempties = ["0", "1"]
                else:
                    neighbours = neighbours_from_coordinates(grid,x,y,t,t_offset=1)
                    nonempties = ["*"]
                if any(nonempty in neighbours for nonempty in nonempties):
                    grid[t][y][x] = "*"
                    ignore_transition[t][y][x] = False
    for y in range(height):
        for x in range(width):
            if grid[-1][y][x] not in ["0", "1"]:
                grid[-1][y][x] = "0"
                ignore_transition[-1][y][x] = True

    print_message("Search pattern:\n" + LLS_formatting.make_csv(grid, ignore_transition) + "\n", 3, indent = indent+1, verbosity = verbosity)
    print_message('Done\n', 3, indent = indent, verbosity = verbosity)
    return grid, ignore_transition


def glider_eater_search_pattern(width,height,digestion_time,symmetry="C1",indent = 0, verbosity = 0):
    print_message('Creating eater search pattern...', 3, indent = indent, verbosity = verbosity)

    glider_in = [
                   [["1","0","0","0","0"],
                    ["0","1","1","0","0"],
                    ["1","1","0","0","0"],
                    ["0","0","0","0","0"],
                    ["0","0","0","0","0"]],
                   [["0","1","0","0","0"],
                    ["0","0","1","0","0"],
                    ["1","1","1","0","0"],
                    ["0","0","0","0","0"],
                    ["0","0","0","0","0"]],
                   [["0","0","0","0","0"],
                    ["1","0","1","0","0"],
                    ["0","1","1","0","0"],
                    ["0","1","0","0","0"],
                    ["0","0","0","0","0"]],
                   [["0","0","0","0","0"],
                    ["0","0","1","0","0"],
                    ["1","0","1","0","0"],
                    ["0","1","1","0","0"],
                    ["0","0","0","0","0"]],
                   [["0","0","0","0","0"],
                    ["0","1","0","0","0"],
                    ["0","0","1","1","0"],
                    ["0","1","1","0","0"],
                    ["0","0","0","0","0"]],
                   [["0","0","0","0","0"],
                    ["0","0","1","0","0"],
                    ["0","0","0","1","0"],
                    ["0","1","1","1","0"],
                    ["0","0","0","0","0"]]
                 ]
    width = width + 2
    height = height + 2
    duration = digestion_time + 6

    grid = [[["0"
        for i in range(width)] for j in range(height)] for k in range(duration)]

    for y in range(1,height-1):
        for x in range(1,width-1):
            grid[-1][y][x] = "*"
    search_pattern = SearchPattern(grid)
    search_pattern.standardise_varaibles_names(indent = indent + 1, verbosity = verbosity)
    for x in range(5):
        for y in range(5):
            search_pattern.grid[-1][y][x] = "0"
    search_pattern.force_symmetry(symmetry)
    for t, generation in enumerate(glider_in):
        search_pattern.grid[t] = copy.deepcopy(search_pattern.grid[-1])
    for t, generation in enumerate(glider_in):
        for y, row in enumerate(generation):
            for x, cell in enumerate(row):
                search_pattern.grid[t][y][x] = cell
    for t in range(6,duration-1):
        for y in range(1,height-1):
            for x in range(1,width-1):
                search_pattern.grid[t][y][x] = "*"
    search_pattern.standardise_varaibles_names(indent = indent + 1, verbosity = verbosity)
    print_message("Pattern created:\n" + search_pattern.make_string(pattern_output_format = "csv") + "\n", 3, indent = indent+1, verbosity = verbosity)
    print_message('Done\n', 3, indent = indent, verbosity = verbosity)
    return search_pattern.grid, search_pattern.ignore_transition

def lwss_eater_search_pattern(width,height,digestion_time,symmetry="C1",indent = 0, verbosity = 0):
    print_message('Creating lwss search pattern...', 3, indent = indent, verbosity = verbosity)
    assert height % 2 == 1, "Height must be odd"

    lwss_in = [
                   [["0","0","0","0","0","0","0"],
                    ["0","0","0","0","0","0","0"],
                    ["0","0","0","0","0","0","0"],
                    ["0","0","0","0","0","0","0"],
                    ["0","0","0","0","0","0","0"],
                    ["0","0","0","0","0","0","0"],
                    ["0","0","0","0","0","0","0"]],
                   [["0","0","0","0","0","0","0"],
                    ["0","0","0","0","0","0","0"],
                    ["0","0","0","0","0","0","0"],
                    ["1","0","0","0","0","0","0"],
                    ["0","0","0","0","0","0","0"],
                    ["0","0","0","0","0","0","0"],
                    ["0","0","0","0","0","0","0"]],
                   [["0","0","0","0","0","0","0"],
                    ["0","0","0","0","0","0","0"],
                    ["1","0","0","0","0","0","0"],
                    ["1","0","0","0","0","0","0"],
                    ["1","0","0","0","0","0","0"],
                    ["0","0","0","0","0","0","0"],
                    ["0","0","0","0","0","0","0"]],
                   [["0","0","0","0","0","0","0"],
                    ["0","0","0","0","0","0","0"],
                    ["1","0","0","0","0","0","0"],
                    ["1","1","0","0","0","0","0"],
                    ["1","0","0","0","0","0","0"],
                    ["0","0","0","0","0","0","0"],
                    ["0","0","0","0","0","0","0"]],
                   [["0","0","0","0","0","0","0"],
                    ["1","0","0","0","0","0","0"],
                    ["0","1","0","0","0","0","0"],
                    ["0","1","0","0","0","0","0"],
                    ["1","1","0","0","0","0","0"],
                    ["0","0","0","0","0","0","0"],
                    ["0","0","0","0","0","0","0"]],
                   [["0","0","0","0","0","0","0"],
                    ["0","0","0","0","0","0","0"],
                    ["1","1","0","0","0","0","0"],
                    ["0","1","1","0","0","0","0"],
                    ["1","1","0","0","0","0","0"],
                    ["1","0","0","0","0","0","0"],
                    ["0","0","0","0","0","0","0"]],
                   [["0","0","0","0","0","0","0"],
                    ["0","0","0","0","0","0","0"],
                    ["1","1","1","0","0","0","0"],
                    ["0","0","1","0","0","0","0"],
                    ["0","0","1","0","0","0","0"],
                    ["0","1","0","0","0","0","0"],
                    ["0","0","0","0","0","0","0"]],
                   [["0","0","0","0","0","0","0"],
                    ["1","1","0","0","0","0","0"],
                    ["1","1","1","0","0","0","0"],
                    ["1","0","1","1","0","0","0"],
                    ["0","1","1","0","0","0","0"],
                    ["0","0","0","0","0","0","0"],
                    ["0","0","0","0","0","0","0"]],
                   [["0","0","0","0","0","0","0"],
                    ["0","0","1","0","0","0","0"],
                    ["0","0","0","1","0","0","0"],
                    ["0","0","0","1","0","0","0"],
                    ["1","1","1","1","0","0","0"],
                    ["0","0","0","0","0","0","0"],
                    ["0","0","0","0","0","0","0"]],
                   [["0","0","0","0","0","0","0"],
                    ["0","0","0","0","0","0","0"],
                    ["0","0","1","1","0","0","0"],
                    ["1","1","0","1","1","0","0"],
                    ["1","1","1","1","0","0","0"],
                    ["0","1","1","0","0","0","0"],
                    ["0","0","0","0","0","0","0"]],
                   [["0","0","0","0","0","0","0"],
                    ["0","0","0","0","0","0","0"],
                    ["0","1","1","1","1","0","0"],
                    ["1","0","0","0","1","0","0"],
                    ["0","0","0","0","1","0","0"],
                    ["1","0","0","1","0","0","0"],
                    ["0","0","0","0","0","0","0"]],
                   [["0","0","0","0","0","0","0"],
                    ["0","0","1","1","0","0","0"],
                    ["0","1","1","1","1","0","0"],
                    ["0","1","1","0","1","1","0"],
                    ["0","0","0","1","1","0","0"],
                    ["0","0","0","0","0","0","0"],
                    ["0","0","0","0","0","0","0"]]
                 ]
    in_time = len(lwss_in)
    width = width + 2
    height = height + 2
    duration = digestion_time + in_time

    grid = [[["0"
        for i in range(width)] for j in range(height)] for k in range(duration)]

    for y in range(1,height-1):
        for x in range(1,width-1):
            grid[-1][y][x] = "*"
    search_pattern = SearchPattern(grid)
    search_pattern.standardise_varaibles_names(indent = indent + 1, verbosity = verbosity)
    for x in range(7):
        for y in range(height/2 - 3, height/2 + 4):
            search_pattern.grid[-1][y][x] = "0"
    search_pattern.force_symmetry(symmetry)
    for t, generation in enumerate(lwss_in):
        search_pattern.grid[t] = copy.deepcopy(search_pattern.grid[-1])
    for t, generation in enumerate(lwss_in):
        for y, row in enumerate(generation):
            if y not in [0, len(generation) - 1]:
                search_pattern.ignore_transition[t][height/2 - 3 + y][0] = True
            for x, cell in enumerate(row):
                search_pattern.grid[t][height/2 - 3 + y][x] = cell
    for t in range(in_time,duration-1):
        for y in range(1,height-1):
            for x in range(1,width-1):
                search_pattern.grid[t][y][x] = "*"
    search_pattern.standardise_varaibles_names(indent = indent + 1, verbosity = verbosity)
    print_message("Pattern created:\n" + search_pattern.make_string(pattern_output_format = "csv") + "\n", 3, indent = indent+1, verbosity = verbosity)
    print_message('Done\n', 3, indent = indent, verbosity = verbosity)
    return search_pattern.grid, search_pattern.ignore_transition


def hwss_eater_search_pattern(width,height,digestion_time,symmetry="C1",indent = 0, verbosity = 0):
    print_message('Creating lwss search pattern...', 3, indent = indent, verbosity = verbosity)
    assert height % 2 == 1, "Height must be odd"

    hwss_in = [
               [["0","0","0","0","0","0","0","0","0"],
                ["0","0","0","0","0","0","0","0","0"],
                ["0","0","0","0","0","0","0","0","0"],
                ["0","0","0","0","0","0","0","0","0"],
                ["0","0","0","0","0","0","0","0","0"],
                ["0","0","0","0","0","0","0","0","0"],
                ["0","0","0","0","0","0","0","0","0"],
                ["0","0","0","0","0","0","0","0","0"],
                ["0","0","0","0","0","0","0","0","0"]],

               [["0","0","0","0","0","0","0","0","0"],
                ["0","0","0","0","0","0","0","0","0"],
                ["0","0","0","0","0","0","0","0","0"],
                ["0","0","0","0","0","0","0","0","0"],
                ["1","0","0","0","0","0","0","0","0"],
                ["0","0","0","0","0","0","0","0","0"],
                ["0","0","0","0","0","0","0","0","0"],
                ["0","0","0","0","0","0","0","0","0"],
                ["0","0","0","0","0","0","0","0","0"]],

               [["0","0","0","0","0","0","0","0","0"],
                ["0","0","0","0","0","0","0","0","0"],
                ["0","0","0","0","0","0","0","0","0"],
                ["1","0","0","0","0","0","0","0","0"],
                ["1","0","0","0","0","0","0","0","0"],
                ["1","0","0","0","0","0","0","0","0"],
                ["0","0","0","0","0","0","0","0","0"],
                ["0","0","0","0","0","0","0","0","0"],
                ["0","0","0","0","0","0","0","0","0"]],

               [["0","0","0","0","0","0","0","0","0"],
                ["0","0","0","0","0","0","0","0","0"],
                ["0","0","0","0","0","0","0","0","0"],
                ["1","0","0","0","0","0","0","0","0"],
                ["1","1","0","0","0","0","0","0","0"],
                ["1","0","0","0","0","0","0","0","0"],
                ["0","0","0","0","0","0","0","0","0"],
                ["0","0","0","0","0","0","0","0","0"],
                ["0","0","0","0","0","0","0","0","0"]],

               [["0","0","0","0","0","0","0","0","0"],
                ["0","0","0","0","0","0","0","0","0"],
                ["1","0","0","0","0","0","0","0","0"],
                ["0","1","0","0","0","0","0","0","0"],
                ["0","1","0","0","0","0","0","0","0"],
                ["1","1","0","0","0","0","0","0","0"],
                ["0","0","0","0","0","0","0","0","0"],
                ["0","0","0","0","0","0","0","0","0"],
                ["0","0","0","0","0","0","0","0","0"]],

               [["0","0","0","0","0","0","0","0","0"],
                ["0","0","0","0","0","0","0","0","0"],
                ["0","0","0","0","0","0","0","0","0"],
                ["1","1","0","0","0","0","0","0","0"],
                ["0","1","1","0","0","0","0","0","0"],
                ["1","1","0","0","0","0","0","0","0"],
                ["1","0","0","0","0","0","0","0","0"],
                ["0","0","0","0","0","0","0","0","0"],
                ["0","0","0","0","0","0","0","0","0"]],

               [["0","0","0","0","0","0","0","0","0"],
                ["0","0","0","0","0","0","0","0","0"],
                ["0","0","0","0","0","0","0","0","0"],
                ["1","1","1","0","0","0","0","0","0"],
                ["0","0","1","0","0","0","0","0","0"],
                ["0","0","1","0","0","0","0","0","0"],
                ["0","1","0","0","0","0","0","0","0"],
                ["0","0","0","0","0","0","0","0","0"],
                ["0","0","0","0","0","0","0","0","0"]],

               [["0","0","0","0","0","0","0","0","0"],
                ["0","0","0","0","0","0","0","0","0"],
                ["1","1","0","0","0","0","0","0","0"],
                ["1","1","1","0","0","0","0","0","0"],
                ["1","0","1","1","0","0","0","0","0"],
                ["0","1","1","0","0","0","0","0","0"],
                ["0","0","0","0","0","0","0","0","0"],
                ["0","0","0","0","0","0","0","0","0"],
                ["0","0","0","0","0","0","0","0","0"]],

               [["0","0","0","0","0","0","0","0","0"],
                ["1","0","0","0","0","0","0","0","0"],
                ["0","0","1","0","0","0","0","0","0"],
                ["0","0","0","1","0","0","0","0","0"],
                ["0","0","0","1","0","0","0","0","0"],
                ["1","1","1","1","0","0","0","0","0"],
                ["0","0","0","0","0","0","0","0","0"],
                ["0","0","0","0","0","0","0","0","0"],
                ["0","0","0","0","0","0","0","0","0"]],

               [["0","0","0","0","0","0","0","0","0"],
                ["0","0","0","0","0","0","0","0","0"],
                ["0","0","0","0","0","0","0","0","0"],
                ["0","0","1","1","0","0","0","0","0"],
                ["1","1","0","1","1","0","0","0","0"],
                ["1","1","1","1","0","0","0","0","0"],
                ["1","1","1","0","0","0","0","0","0"],
                ["0","0","0","0","0","0","0","0","0"],
                ["0","0","0","0","0","0","0","0","0"]],

               [["0","0","0","0","0","0","0","0","0"],
                ["0","0","0","0","0","0","0","0","0"],
                ["0","0","0","0","0","0","0","0","0"],
                ["1","1","1","1","1","0","0","0","0"],
                ["0","0","0","0","1","0","0","0","0"],
                ["0","0","0","0","1","0","0","0","0"],
                ["0","0","0","1","0","0","0","0","0"],
                ["1","1","0","0","0","0","0","0","0"],
                ["0","0","0","0","0","0","0","0","0"]],

               [["0","0","0","0","0","0","0","0","0"],
                ["0","0","0","0","0","0","0","0","0"],
                ["1","1","1","1","0","0","0","0","0"],
                ["1","1","1","1","1","0","0","0","0"],
                ["1","1","1","0","1","1","0","0","0"],
                ["0","0","0","1","1","0","0","0","0"],
                ["0","0","0","0","0","0","0","0","0"],
                ["0","0","0","0","0","0","0","0","0"],
                ["0","0","0","0","0","0","0","0","0"]],

               [["0","0","0","0","0","0","0","0","0"],
                ["0","1","1","0","0","0","0","0","0"],
                ["0","0","0","0","1","0","0","0","0"],
                ["0","0","0","0","0","1","0","0","0"],
                ["0","0","0","0","0","1","0","0","0"],
                ["1","1","1","1","1","1","0","0","0"],
                ["0","0","0","0","0","0","0","0","0"],
                ["0","0","0","0","0","0","0","0","0"],
                ["0","0","0","0","0","0","0","0","0"]],

               [["0","0","0","0","0","0","0","0","0"],
                ["0","0","0","0","0","0","0","0","0"],
                ["0","0","0","0","0","0","0","0","0"],
                ["0","0","0","0","1","1","0","0","0"],
                ["1","1","1","1","0","1","1","0","0"],
                ["1","1","1","1","1","1","0","0","0"],
                ["0","1","1","1","1","0","0","0","0"],
                ["0","0","0","0","0","0","0","0","0"],
                ["0","0","0","0","0","0","0","0","0"]],

               [["0","0","0","0","0","0","0","0","0"],
                ["0","0","0","0","0","0","0","0","0"],
                ["0","0","0","0","0","0","0","0","0"],
                ["0","1","1","1","1","1","1","0","0"],
                ["1","0","0","0","0","0","1","0","0"],
                ["0","0","0","0","0","0","1","0","0"],
                ["1","0","0","0","0","1","0","0","0"],
                ["0","0","1","1","0","0","0","0","0"],
                ["0","0","0","0","0","0","0","0","0"]],

               [["0","0","0","0","0","0","0","0","0"],
                ["0","0","0","0","0","0","0","0","0"],
                ["0","0","1","1","1","1","0","0","0"],
                ["0","1","1","1","1","1","1","0","0"],
                ["0","1","1","1","1","0","1","1","0"],
                ["0","0","0","0","0","1","1","0","0"],
                ["0","0","0","0","0","0","0","0","0"],
                ["0","0","0","0","0","0","0","0","0"],
                ["0","0","0","0","0","0","0","0","0"]]
               ]
    in_time = len(hwss_in)
    width = width + 2
    height = height + 2
    duration = digestion_time + in_time

    grid = [[["0"
        for i in range(width)] for j in range(height)] for k in range(duration)]

    for y in range(1,height-1):
        for x in range(1,width-1):
            grid[-1][y][x] = "*"
    search_pattern = SearchPattern(grid)
    search_pattern.standardise_varaibles_names(indent = indent + 1, verbosity = verbosity)
    for x in range(9):
        for y in range(height/2 - 4, height/2 + 5):
            search_pattern.grid[-1][y][x] = "0"
    search_pattern.force_symmetry(symmetry)
    for t, generation in enumerate(hwss_in):
        search_pattern.grid[t] = copy.deepcopy(search_pattern.grid[-1])
    for t, generation in enumerate(hwss_in):
        for y, row in enumerate(generation):
            if y not in [0, len(generation) - 1]:
                search_pattern.ignore_transition[t][height/2 - 4 + y][0] = True
            for x, cell in enumerate(row):
                search_pattern.grid[t][height/2 - 4 + y][x] = cell
    for t in range(in_time,duration-1):
        for y in range(1,height-1):
            for x in range(1,width-1):
                search_pattern.grid[t][y][x] = "*"
    search_pattern.standardise_varaibles_names(indent = indent + 1, verbosity = verbosity)
    print_message("Pattern created:\n" + search_pattern.make_string(pattern_output_format = "csv") + "\n", 3, indent = indent+1, verbosity = verbosity)
    print_message('Done\n', 3, indent = indent, verbosity = verbosity)
    return search_pattern.grid, search_pattern.ignore_transition

def stator_search_pattern(pattern, rule=None, background_grid=None, indent=0, verbosity=0):
    if rule == None:
        rule = LLS_rules.rule_from_rulestring(LLS_defaults.rulestring)
    if background_grid == None:
        (
            background_grid,
            _
        ) = LLS_formatting.parse_input_string(
            LLS_files.string_from_file(
                "backgrounds/" + LLS_defaults.background,
            )
        )
    width = len(pattern[0])
    height = len(pattern)
    grid = [pattern]
    duration = 1
    print_message('Creating oscillator...', 3, indent = indent, verbosity = verbosity)
    while True:
        print_message('Generation: ' + str(duration), 3, indent = indent + 1, verbosity = verbosity)
        grid.append([["0" for x in xrange(width)] for y in xrange(height)])
        duration += 1
        for x in xrange(width):
            for y in xrange(height):
                BS_letter = "S" if grid[-2][y][x] == "1" else "B"
                grid[-1][y][x] = rule[BS_letter + LLS_rules.transition_from_cells(neighbours_from_coordinates(grid,x,y,-1, background_grid = background_grid))]
        if grid[0] == grid[-1]:
            break
    number_of_variables = 0
    for x in xrange(width):
        for y in xrange(height):
            if all(grid[t][y][x] == grid[0][y][x] for t in xrange(duration)):
                for t in xrange(duration):
                    grid[t][y][x] = "stator_cell_" + str(number_of_variables)
                number_of_variables += 1
    grid = [[["0" for x in range(width)]] + generation + [["0" for x in range(width)]] for generation in grid]
    grid = [[["0"] + row + ["0"] for row in generation] for generation in grid]
    print_message('Done\n', 3, indent = indent, verbosity = verbosity)
    return grid
