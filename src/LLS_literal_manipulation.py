def negate(literal, flag = True, DIMACS = False):
    """The negation of the given literal"""

    if flag:
        if literal == "0":
            negation = "1"
        elif literal == "1" and not DIMACS:
            negation = "0"
        elif literal[0] == "-":
            negation = literal[1:]
        else:
            negation = "-" + literal
    else:
        negation = literal

    return negation


def variable_from_literal(literal, DIMACS = False):
    """Breaks down a literal into a variable and a flag for negation"""

    if not DIMACS:
        assert literal not in ["0","1"], 'Trying to find the underlying variable of "0" or "1"'

    if literal[0] == "-":
        variable = literal[1:]
        negated = True
    else:
        variable = literal
        negated = False

    return (variable, negated)

def implies(antecedents, consequent):
    """Creates a clause saying that the antecedent literals imply the consequent"""
    if isinstance(antecedents, basestring):
        antecedents = [antecedents]
    return map(negate, list(antecedents)) + [consequent]

def neighbours_from_coordinates(grid,x,y,t,t_offset=-1,outside_border="0"):

    width = len(grid[0][0])
    height = len(grid[0])

    neighbours = []
    for x_offset, y_offset in [(1,0),(1,1),(0,1),(-1,1),(-1,0),(-1,-1),(0,-1),(1,-1)]:
        if (x + x_offset in range(width) and y + y_offset in range(height)):
            neighbours.append(grid[t + t_offset][y + y_offset][x + x_offset])
        else:
            neighbours.append(outside_border)

    return neighbours
