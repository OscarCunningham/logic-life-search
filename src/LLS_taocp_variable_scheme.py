from LLS_literal_manipulation import negate, implies, neighbours_from_coordinates

def children(letter, x, y):
    """Gives the indices of the "children" of the variables describing the neighbours of a cell, according to the scheme described by Knuth"""
    assert letter in ["a", "b", "c", "d", "e", "f", "g"], "Letter does not have children in Knuth's scheme"
    if letter == "a":
        return ("b", x, y | 1, "c", x, y)
    elif letter == "b":
        return ("d", x - (x & 2), y, "e", x + (x & 2), y)
    elif letter == "c":
        if y % 2 == 0:
            return ("f", x - (x & 1), y, "g", x, y)
        else:
            return ("f", (x - 1) | 1, y + 2, "g", x, y)
    elif letter == "d":
        return (None, x + 1, y - 1, None, x + 1, y)
    elif letter == "e":
        return (None, x - 1, y - 1, None, x - 1, y)
    elif letter == "f":
        return (None, x, y - 1, None, x + 1, y - 1)
    elif letter == "g":
        if y % 2 == 0:
            return (None, x, y + 1 - ((y & 1) << 1),
                    None, x - 1 + ((x & 1) << 1), y - 1)
        else:
            return (None, x, y + 1 - ((y & 1) << 1), None, x ^ 1, y + 1)



def maximum_number_of_live_cells(letter):
    """Defines the maximum nuber of cells that can be counted in each area, in Knuth's neighbour counting scheme"""
    assert letter in ["a", "b", "c", "d", "e", "f", "g", None], "Letter not used in Knuth's scheme"
    if letter == "a":
        return 8
    elif letter in ["b", "c"]:
        return 4
    elif letter in ["d", "e", "f", "g"]:
        return 2
    elif letter == None:
        return 1



def definition_clauses(search_pattern, grid, x, y, t, letter, at_least):
    """Defines clauses that define variables for Knuth's neighbour counting scheme"""

    if letter == None:
        return []
    else:
        (child_1_letter, child_1_x, child_1_y,
         child_2_letter, child_2_x, child_2_y) = children(letter, x, y)

        maximum_number_of_live_cells_1 = maximum_number_of_live_cells(child_1_letter)
        maximum_number_of_live_cells_2 = maximum_number_of_live_cells(child_2_letter)

        child_1_needing_definition = []  # A list of child1 variables we need to define
        child_2_needing_definition = []  # A list of child2 variables we need to define

        # If at_least is obviously too small or too big, give the obvious answer
        if at_least <= 0:
            search_pattern.clauses.append([literal_name(search_pattern, grid, x, y, t, letter, at_least)])
        elif at_least > maximum_number_of_live_cells_1 + maximum_number_of_live_cells_2:
            search_pattern.clauses.append([negate(literal_name(search_pattern, grid, x, y, t, letter, at_least))])

        # Otherwise define the appropriate clauses
        else:
            if at_least <= maximum_number_of_live_cells_1:
                search_pattern.clauses.append([negate(literal_name(search_pattern, grid, child_1_x, child_1_y, t, child_1_letter, at_least)),
                                literal_name(search_pattern, grid, x, y, t, letter, at_least)])
                child_1_needing_definition.append(at_least)
            for j in range(1, maximum_number_of_live_cells_2 + 1):
                for i in range(1, maximum_number_of_live_cells_1 + 1):
                    if i + j == at_least:
                        search_pattern.clauses.append([
                                negate(literal_name(search_pattern, grid, child_1_x, child_1_y, t, child_1_letter, i)),
                                negate(literal_name(search_pattern, grid, child_2_x, child_2_y, t, child_2_letter, j)),
                                literal_name(search_pattern, grid, x, y, t, letter, at_least)])
                        child_1_needing_definition.append(i)
                        child_2_needing_definition.append(j)
            if at_least <= maximum_number_of_live_cells_2:
                search_pattern.clauses.append([negate(literal_name(search_pattern, grid, child_2_x, child_2_y, t, child_2_letter, at_least)),
                                literal_name(search_pattern, grid, x, y, t, letter, at_least)])
                child_2_needing_definition.append(at_least)

            if at_least > maximum_number_of_live_cells_2:
                i = at_least - maximum_number_of_live_cells_2
                search_pattern.clauses.append([literal_name(search_pattern, grid, child_1_x, child_1_y, t, child_1_letter, i),
                                negate(literal_name(search_pattern, grid, x, y, t, letter, at_least))])
                child_1_needing_definition.append(i)
            for j in range(1, maximum_number_of_live_cells_2 + 1):
                for i in range(1, maximum_number_of_live_cells_1 + 1):
                    if i + j == at_least + 1:
                        search_pattern.clauses.append([
                                literal_name(search_pattern, grid, child_1_x, child_1_y, t, child_1_letter, i),
                                literal_name(search_pattern, grid, child_2_x, child_2_y, t, child_2_letter, j),
                                negate(literal_name(search_pattern, grid, x, y, t, letter, at_least))])
                        child_1_needing_definition.append(i)
                        child_2_needing_definition.append(j)
            if at_least > maximum_number_of_live_cells_1:
                j = at_least - maximum_number_of_live_cells_1
                search_pattern.clauses.append([literal_name(search_pattern, grid, child_2_x, child_2_y, t, child_2_letter, j),
                                negate(literal_name(search_pattern, grid, x, y, t, letter, at_least))])
                child_2_needing_definition.append(j)

        # Remove duplicates from our lists of child variables we need to define
        child_1_needing_definition = set(child_1_needing_definition)
        child_2_needing_definition = set(child_2_needing_definition)

        # Define the child variables
        for child_1_at_least in child_1_needing_definition:
            definition_clauses(search_pattern, grid, child_1_x, child_1_y, t, child_1_letter, child_1_at_least)
        for child_2_at_least in child_2_needing_definition:
            definition_clauses(search_pattern, grid, child_2_x, child_2_y, t, child_2_letter, child_2_at_least)



def literal_name(search_pattern, grid, x, y, t, letter=None, at_least=1):
    """Creates a unique variable name to be used in CNF, given coordinates and an extra letter for Knuth's neighbour counting scheme"""
    if at_least > maximum_number_of_live_cells(letter):
        literal = "0"
    elif at_least < 0:
        literal = "1"
    elif letter == None:

        width = len(grid[0][0])
        height = len(grid[0])

        if 0 <= x < width and 0 <= y < height:
            literal = grid[t][y][x]
        else:
            background_width = len(search_pattern.background_grid[0][0])
            background_height = len(search_pattern.background_grid[0])
            background_duration = len(search_pattern.background_grid)
            literal = search_pattern.background_grid[t%background_duration][y%background_height][x%background_width]
    else:
        literal = "knuth_" + letter + str(at_least) + "x" + str(x) + "y" + str(y) + "t" + str(t)

    return literal


def transition_rule(search_pattern, grid, x, y, t):
    """Creates clauses enforcing the transition rule at coordinates x, y, t of grid"""

    duration = len(grid)

    # These clauses define variables a_i meaning at least i of the neighbours were alive at time t - 1
    definition_clauses(search_pattern, grid, x, y, (t - 1) % duration, "a", at_least = 2)
    definition_clauses(search_pattern, grid, x, y, (t - 1) % duration, "a", at_least = 3)
    definition_clauses(search_pattern, grid, x, y, (t - 1) % duration, "a", at_least = 4)

    cell = literal_name(search_pattern, grid, x, y, t)
    predecessor_cell = literal_name(search_pattern, grid, x, y, (t - 1) % duration)
    # These clauses implement the cellular automaton rule

    # If there are at least 4 neighbours in the previous generation then the cell dies
    search_pattern.clauses.append(implies(
        literal_name(search_pattern, grid, x, y, (t - 1) % duration, "a", at_least = 4),
        negate(cell)))
    # If there aren't at least 2 neighbours in the previous generation then the cell dies
    search_pattern.clauses.append(implies(
        negate(literal_name(search_pattern, grid, x, y, (t - 1) % duration, "a", at_least = 2)),
        negate(cell)))
    # If the predecessor is dead and there aren't at least 3 neighbours then the cell dies
    search_pattern.clauses.append(implies([
        negate(predecessor_cell),
        negate(literal_name(search_pattern, grid, x, y, (t - 1) % duration, "a", at_least = 3))],
        negate(cell)))
    # If there are exactly 3 neighbours then the cell lives
    search_pattern.clauses.append(implies([
        negate(literal_name(search_pattern, grid, x, y, (t - 1) % duration, "a", at_least = 4)),
        literal_name(search_pattern, grid, x, y, (t - 1) % duration, "a", at_least = 3)],
        cell))
    # If the predecessor is alive and there are at least 2 neighbours but not at least 4 neighbours then the cell lives
    search_pattern.clauses.append(implies([
        predecessor_cell,
        literal_name(search_pattern, grid, x, y, (t - 1) % duration, "a", at_least = 2),
        negate(literal_name(search_pattern, grid, x, y, (t - 1) % duration, "a", at_least = 4))],
        cell))
