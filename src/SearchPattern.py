import collections
import copy
import itertools
import LLS_taocp_variable_scheme
import LLS_formatting
import LLS_rules
import LLS_defaults
import LLS_files
import LLS_literal_manipulation
from ClauseList import ClauseList
from UnsatInPreprocessing import UnsatInPreprocessing
from LLS_messages import print_message
from LLS_literal_manipulation import negate, variable_from_literal, neighbours_from_coordinates, implies

class SearchPattern:


    def __init__(
        self,
        grid,
        ignore_transition = None,
        background_grid = None,
        background_ignore_transition = None,
        rule = None,
        add_border = True,
        indent = 0, verbosity = 0
    ):
        self.grid = copy.deepcopy(grid)
        self.ignore_transition = (
            copy.deepcopy(ignore_transition)
            if (ignore_transition != None)
            else [[[False for cell in row] for row in generation] for generation in grid]
        )
        if background_grid == None:
            (
                self.background_grid,
                self.background_ignore_transition
            ) = LLS_formatting.parse_input_string(
                LLS_files.string_from_file(
                    "backgrounds/" + LLS_defaults.background,
                )
            )
        else:
            self.background_grid = copy.deepcopy(background_grid)
            self.background_ignore_transition = (
                copy.deepcopy(background_ignore_transition)
                if (background_ignore_transition != None)
                else [[[False for cell in row] for row in generation] for generation in background_grid]
            )
        self.clauses = ClauseList()
        self.rule = (copy.deepcopy(rule)
                                  if (rule != None)
                                  else LLS_rules.rule_from_rulestring(LLS_defaults.rulestring))

        if add_border:
            width = len(self.grid[0][0])
            height = len(self.grid[0])
            duration = len(self.grid)
            background_width = len(self.background_grid[0][0])
            background_height = len(self.background_grid[0])
            background_duration = len(self.background_grid)

            # Surround the grid by one cell from the background, and offset the background accodingly
            LLS_literal_manipulation.offset_background(self.background_grid,1,1,0)
            new_grid = [[["0" for x in xrange(width + 2)] for y in xrange(height + 2)] for t in xrange(duration)]
            for x in xrange(width + 2):
                for y in xrange(height + 2):
                    for t in xrange(duration):
                        if x in range(1, width + 1) and y in range(1, height + 1):
                            new_grid[t][y][x] = self.grid[t][y - 1][x - 1]
                        else:
                            new_grid[t][y][x] = self.background_grid[t % background_duration][y % background_height][x % background_width]
            self.grid = new_grid
            LLS_literal_manipulation.offset_background(self.background_ignore_transition,1,1,0)
            new_ignore_transition = [[["0" for x in xrange(width + 2)] for y in xrange(height + 2)] for t in xrange(duration)]
            for x in xrange(width + 2):
                for y in xrange(height + 2):
                    for t in xrange(duration):
                        if x in range(1, width + 1) and y in range(1, height + 1):
                            new_ignore_transition[t][y][x] = self.ignore_transition[t][y - 1][x - 1]
                        else:
                            new_ignore_transition[t][y][x] = self.background_ignore_transition[t % background_duration][y % background_height][x % background_width]
            self.ignore_transition = new_ignore_transition



    def __eq__(self, other):
        if other == None:
            return False
        else:
            return (
                self.grid == other.grid
                and self.ignore_transition == other.ignore_transition
                and self.background_grid == other.background_grid
                and self.background_ignore_transition == other.ignore_transition
                and self.clauses == other.clauses
                and self.rule == other.rule
            )


    def __ne__(self, other):
        return not __eq__(self, other)


    def standardise_varaibles_names(self, indent = 0, verbosity = 0):
        print_message("Standardising variable names...", 3, indent = indent, verbosity = verbosity)

        #Give variables standard names and replace stars with new variable names
        standard_variables_from_input_variables = {}
        current_variable_number = 0

        for t, generation in enumerate(self.background_grid):
            for y, row in enumerate(generation):
                for x, cell in enumerate(row):
                    if cell == "*":
                        self.background_grid[t][y][x] = "c" + str(current_variable_number)
                        current_variable_number += 1
                    elif cell not in ["0","1"]:
                        (variable, negated) = variable_from_literal(cell)
                        if not standard_variables_from_input_variables.has_key(variable):
                            standard_variables_from_input_variables[variable] = negate("c" + str(current_variable_number),negated)
                            current_variable_number += 1
                        self.background_grid[t][y][x] = negate(standard_variables_from_input_variables[variable],negated)
        for t, generation in enumerate(self.grid):
            for y, row in enumerate(generation):
                for x, cell in enumerate(row):
                    if cell == "*":
                        self.grid[t][y][x] = "c" + str(current_variable_number)
                        current_variable_number += 1
                    elif cell not in ["0","1"]:
                        (variable, negated) = variable_from_literal(cell)
                        if not standard_variables_from_input_variables.has_key(variable):
                            standard_variables_from_input_variables[variable] = negate("c" + str(current_variable_number),negated)
                            current_variable_number += 1
                        self.grid[t][y][x] = negate(standard_variables_from_input_variables[variable],negated)
        # Rename any literals in rule
        for transition, literal in self.rule.items():
            if literal not in ["0", "1"]:
                (variable, negated) = variable_from_literal(literal)
                if not standard_variables_from_input_variables.has_key(variable):
                    standard_variables_from_input_variables[variable] = negate("c" + str(current_variable_number),negated)
                    current_variable_number += 1
                self.rule[transition] = negate(standard_variables_from_input_variables[variable],negated)

        print_message("Done\n", 3, indent = indent, verbosity = verbosity)

    def number_of_cells(self):
        return len(set(variable_from_literal(cell) for generation in self.grid for row in generation for cell in row if cell not in ["0", "1"]))

    def remove_redundancies(self, indent = 0, verbosity = 0):
        print_message("Removing redundant transitions...", 3, indent = indent, verbosity = verbosity)
        parents_dict = {}
        to_force_equal = []
        background_duration = len(self.background_grid)
        for t, generation in enumerate(self.background_grid):
            for y, row in enumerate(generation):
                for x, cell in enumerate(row):
                    predecessor_cell = self.background_grid[(t - 1) % background_duration][y][x]
                    neighbours = neighbours_from_coordinates(self.background_grid, x, y, t, background_grid = self.background_grid)
                    if not self.background_ignore_transition[t][y][x]:
                        parents = [predecessor_cell] + list(LLS_rules.sort_neighbours(neighbours))
                        parents_string = str(parents)
                        if parents_dict.has_key(parents_string):
                            self.background_grid[t][y][x] = parents_dict[parents_string]
                            to_force_equal.append((parents_dict[parents_string],cell))
                            self.background_ignore_transition[t][y][x] = True
                        elif all(parent in ["0", "1"] for parent in parents):
                            BS_letter = ["B", "S"][["0", "1"].index(predecessor_cell)]
                            transition = LLS_rules.transition_from_cells(neighbours)
                            child = self.rule[BS_letter + transition]
                            if cell not in ["0","1"]:
                                self.background_grid[t][y][x] = child
                            to_force_equal.append((cell, child))
                            self.background_ignore_transition[t][y][x] = True
                            parents_dict[parents_string] = self.background_grid[t][y][x]
                        else:
                            parents_dict[parents_string] = cell
        self.force_equal(to_force_equal)
        to_force_equal = []
        for t, generation in enumerate(self.grid):
            if t > 0:
                for y, row in enumerate(generation):
                    for x, cell in enumerate(row):
                        predecessor_cell = self.grid[t - 1][y][x]
                        neighbours = neighbours_from_coordinates(self.grid, x, y, t, background_grid = self.background_grid)

                        if not self.ignore_transition[t][y][x]:
                            parents = [predecessor_cell] + list(LLS_rules.sort_neighbours(neighbours))
                            parents_string = str(parents)
                            if parents_dict.has_key(parents_string):
                                self.grid[t][y][x] = parents_dict[parents_string]
                                to_force_equal.append((parents_dict[parents_string],cell))
                                self.ignore_transition[t][y][x] = True
                            elif all(parent in ["0", "1"] for parent in parents):
                                BS_letter = ["B", "S"][["0", "1"].index(predecessor_cell)]
                                transition = LLS_rules.transition_from_cells(neighbours)
                                child = self.rule[BS_letter + transition]
                                if cell not in ["0","1"]:
                                    self.grid[t][y][x] = child
                                to_force_equal.append((cell, child))
                                self.ignore_transition[t][y][x] = True
                                parents_dict[parents_string] = self.grid[t][y][x]
                            else:
                                parents_dict[parents_string] = cell
        self.force_equal(to_force_equal)
        print_message("Done\n", 3, indent = indent, verbosity = verbosity)

    def force_transition(self, grid, x, y, t, method):
        cell = grid[t][y][x]
        duration = len(grid)
        if method == 0:
            LLS_taocp_variable_scheme.transition_rule(self, grid, x, y, t)

        elif method == 1:
            predecessor_cell = grid[(t - 1) % duration][y][x]
            neighbours = neighbours_from_coordinates(grid, x, y, t, background_grid = self.background_grid)

            # If any four neighbours were live, then the cell is
            # dead
            for four_neighbours in itertools.combinations(neighbours, 4):
                clause = implies(four_neighbours, negate(cell))
                self.clauses.append(clause)

            # If any seven neighbours were dead, the cell is dead
            for seven_neighbours in itertools.combinations(neighbours, 7):
                clause = implies(map(negate,seven_neighbours), negate(cell))
                self.clauses.append(clause)

            # If the cell was dead, and any six neighbours were
            # dead, the cell is dead
            for six_neighbours in itertools.combinations(neighbours, 6):
                clause = implies([negate(predecessor_cell)] + map(negate,six_neighbours), negate(cell))
                self.clauses.append(clause)

            # If three neighbours were alive and five were dead,
            # then the cell is live
            for three_neighbours in itertools.combinations(neighbours, 3):
                neighbours_counter = collections.Counter(neighbours)
                neighbours_counter.subtract(three_neighbours)
                three_neighbours, five_neighbours = list(three_neighbours), list(neighbours_counter.elements())

                clause = implies(three_neighbours + map(negate, five_neighbours), cell)
                self.clauses.append(clause)

            # Finally, if the cell was live, and two neighbours
            # were live, and five neighbours were dead, then the
            # cell is live (independantly of the final neighbour)
            for two_neighbours in itertools.combinations(neighbours, 2):
                neighbours_counter = collections.Counter(neighbours)
                neighbours_counter.subtract(two_neighbours)
                two_neighbours, five_neighbours = list(two_neighbours), list(neighbours_counter.elements())[1:]

                clause = implies([predecessor_cell] + two_neighbours + map(negate, five_neighbours), cell)
                self.clauses.append(clause)

        elif method == 2:

            predecessor_cell = grid[(t - 1) % duration][y][x]
            neighbours = neighbours_from_coordinates(self.grid,x,y,t, background_grid = self.background_grid)

            booleans = [True, False]

            # For each combination of neighbourhoods
            for predecessor_cell_alive in booleans:
                for neighbours_alive in itertools.product(booleans,repeat=8):

                    BS_letter = "S" if predecessor_cell_alive else "B"
                    transition = LLS_rules.transition_from_cells(neighbours_alive)
                    transition_literal = self.rule[BS_letter + transition]

                    self.clauses.append(implies([transition_literal] + [negate(predecessor_cell, not predecessor_cell_alive)] + map(negate, neighbours, map(lambda P: not P, neighbours_alive)), cell))
                    self.clauses.append(implies([negate(transition_literal)] + [negate(predecessor_cell, not predecessor_cell_alive)] + map(negate, neighbours, map(lambda P: not P, neighbours_alive)), negate(cell)))

    def force_evolution(self, method=None, indent = 0, verbosity = 0):
        """Adds clauses that force the search pattern to obey the transition rule"""

        # Methods:
        # 0. An implementation of the scheme Knuth describes in TAOCP Volume 4, Fascile 6, solution to exercise 65b (57 clauses and 13 auxillary variables per cell)
        # 1. An implementation of the naive scheme Knuth gives in the solution to exercise 65a                      (190 clauses and 0 auxillary variables per cell)
        # 2. A very naive scheme just listing all possible predecessor neighbourhoods                               (512 clauses and 0 auxillary variables per cell)

        print_message("Enforcing evolution rule...", 3, indent = indent, verbosity = verbosity)

        if method is None:
            if LLS_rules.rulestring_from_rule(self.rule) == "B3/S23":
                method = LLS_defaults.life_encoding_method
            else:
                method = 2 # Default method
        assert method in range(3), "Method not found"
        assert method == 2 or LLS_rules.rulestring_from_rule(self.rule) == "B3/S23", "Rules other than Life can only use method 2"

        print_message("Method: " + str(method), 3, indent = indent + 1, verbosity = verbosity)
        starting_number_of_clauses = len(self.clauses.clause_set)
        # Iterate over all cells not in the first generation
        for t, generation in enumerate(self.grid):
            if t > 0:
                for y, row in enumerate(generation):
                    for x, cell in enumerate(row):
                        if not self.ignore_transition[t][y][x]:
                            self.force_transition(self.grid, x,y,t, method)

        # Iterate over all background cells
        for t, generation in enumerate(self.background_grid):
            for y, row in enumerate(generation):
                for x, cell in enumerate(row):
                    if not self.background_ignore_transition[t][y][x]:
                        self.force_transition(self.background_grid, x,y,t, method)

        print_message(
            "Number of clauses used: " + str(len(self.clauses.clause_set) - starting_number_of_clauses),
            3,
            indent = indent + 1, verbosity = verbosity
        )
        print_message("Done\n", 3, indent = indent, verbosity = verbosity)


    def force_change(self, times, indent = 0, verbosity = 0):
        """Adds clauses forcing at least one cell to change between specified generations"""

        (t_0, t_1) = times
        print_message("Forcing at least one cell to change between generations " + str(t_0) + " and " + str(t_1) + " ...", 3, indent = indent, verbosity = verbosity)

        starting_number_of_clauses = len(self.clauses.clause_set)

        width = len(self.grid[0][0])
        height = len(self.grid[0])

        self.force_unequal([(self.grid[t_0][y][x],self.grid[t_1][y][x]) for x in xrange(width) for y in xrange(height)])

        print_message(
            "Number of clauses used: " + str(len(self.clauses.clause_set) - starting_number_of_clauses),
            3,
            indent = indent + 1, verbosity = verbosity
        )
        print_message("Done\n", 3, indent = indent, verbosity = verbosity)


    def force_distinct(self, solution, determined = False, indent = 0, verbosity = 0):
        """Force search_pattern to have at least one differnence from given solution"""

        print_message("Forcing pattern to be different from solution...", 3, indent = indent, verbosity = verbosity)

        clause = []

        for t, generation in enumerate(self.grid):
            if t == 0 or not determined:
                for y, row in enumerate(generation):
                    for x, cell in enumerate(row):
                        other_cell = solution.grid[t][y][x]
                        assert other_cell in ["0", "1"], "Only use force_distinct against solved patterns"
                        if other_cell == "0":
                            clause.append(cell)
                        else:
                            clause.append(negate(cell))

        for t, generation in enumerate(self.background_grid):
            for y, row in enumerate(generation):
                for x, cell in enumerate(row):
                    other_cell = solution.background_grid[t][y][x]
                    assert other_cell in ["0", "1"], "Only use force_distinct against solved patterns"
                    if other_cell == "0":
                        clause.append(cell)
                    else:
                        clause.append(negate(cell))

        for transition, literal in self.rule.items():
            other_literal = solution.rule[transition]
            assert other_literal in ["0", "1"], "Only use force_distinct against solved patterns"
            if other_literal == "0":
                clause.append(literal)
            else:
                clause.append(negate(literal))
        self.clauses.append(clause)
        print_message("Number of clauses used: 1", 3, indent = indent + 1, verbosity = verbosity)
        print_message("Done\n", 3, indent = indent, verbosity = verbosity)

    def define_cardinality_variable(self, literals, at_least, already_defined = None, preprocessing = True):
        """Generates clauses defining a cardinality variable"""

        if preprocessing:
            #Remove "0"s and "1"s
            literals_copy = []
            for literal in literals:
                if literal in ["0","1"]:
                    at_least -= int(literal)
                else:
                    literals_copy.append(literal)

            literals_copy.sort()
        else:
            literals_copy = copy.deepcopy(literals)

        if already_defined == None:
            already_defined = []


        def cardinality_variable_name(literals, at_least):
            return "at_least_" + str(at_least) + "_of_" + str(literals)

        name = cardinality_variable_name(literals_copy, at_least)

        if name not in already_defined:
            already_defined.append(name)

            max_literals = len(literals_copy) #The most literals that could be true
            max_literals_1 = max_literals/2
            literals_1 = literals_copy[:max_literals_1]
            variables_to_define_1 = []  # A list of variables we need to define
            max_literals_2 = max_literals - max_literals_1
            literals_2 = literals_copy[max_literals_1:]
            variables_to_define_2 = []  # A list of variables we need to define

            # If at_least is obviously too small or too big, give the obvious answer
            if at_least <= 0:
                self.clauses.append([name])
            elif at_least > max_literals:
                self.clauses.append([negate(name)])
            elif max_literals == 1:
                literal = literals_copy[0]
                self.clauses.append([negate(name), literal])
                self.clauses.append([name, negate(literal)])

            # Otherwise define the appropriate clauses
            else:
                if at_least <= max_literals_1:
                    self.clauses.append(
                        implies(
                            cardinality_variable_name(literals_1, at_least),
                            name))
                    variables_to_define_1.append(at_least)
                for j in range(1, max_literals_2 + 1):
                    for i in range(1, max_literals_1 + 1):
                        if i + j == at_least:
                            self.clauses.append(
                                implies(
                                    [cardinality_variable_name(literals_1, i),
                                    cardinality_variable_name(literals_2, j)],
                                    name))
                            variables_to_define_1.append(i)
                            variables_to_define_2.append(j)
                if at_least <= max_literals_2:
                    self.clauses.append(
                        implies(
                            cardinality_variable_name(literals_2, at_least),
                            name))
                    variables_to_define_2.append(at_least)

                if at_least > max_literals_2:
                    i = at_least - max_literals_2
                    self.clauses.append(
                        implies(
                            negate(cardinality_variable_name(literals_1, i)),
                            negate(name)))
                    variables_to_define_1.append(i)
                for j in range(1, max_literals_2 + 1):
                    for i in range(1, max_literals_1 + 1):
                        if i + j == at_least + 1:
                            self.clauses.append(implies([
                                    negate(cardinality_variable_name(literals_1, i)),
                                    negate(cardinality_variable_name(literals_2, j))],
                                    negate(name)))
                            variables_to_define_1.append(i)
                            variables_to_define_2.append(j)
                if at_least > max_literals_1:
                    j = at_least - max_literals_1
                    self.clauses.append(
                        implies(
                            negate(cardinality_variable_name(literals_2, j)),
                            negate(name)))
                    variables_to_define_2.append(j)

            # Remove duplicates from our lists of child variables we need to define
            variables_to_define_1 = set(variables_to_define_1)
            variables_to_define_2 = set(variables_to_define_2)

            # Define the child variables
            for at_least_1 in variables_to_define_1:
                self.define_cardinality_variable(literals_1, at_least_1, already_defined, preprocessing = False)
            for at_least_2 in variables_to_define_2:
                self.define_cardinality_variable(literals_2, at_least_2, already_defined, preprocessing = False)
        return name

    def force_symmetry(self, symmetry, indent = 0, verbosity = 0):
        to_force_equal = self.cell_pairs_from_transformation(symmetry, indent = indent, verbosity = verbosity)
        self.force_equal(to_force_equal)

    def force_asymmetry(self, asymmetry, indent = 0, verbosity = 0):
        to_force_unequal = self.cell_pairs_from_transformation(asymmetry, indent = indent, verbosity = verbosity)
        self.force_unequal(to_force_unequal)

    def cell_pairs_from_transformation(self, symmetry, indent = 0, verbosity = 0):
        (
            transformation,
            x_translate,
            y_translate,
            period
        ) = symmetry
        transformation = transformation.upper()
        width = len(self.grid[0][0])
        height = len(self.grid[0])
        duration = len(self.grid)
        background_width = len(self.background_grid[0][0])
        background_height = len(self.background_grid[0])
        background_duration = len(self.background_grid)

        if transformation == "RO0":
            f = lambda x, y: (x + x_translate, y + y_translate)
            f_inv = lambda x, y: (x - x_translate, y - y_translate)
        elif transformation == "RO1":
            f = lambda x, y: ((height - 1) - y + x_translate, x + y_translate)
            f_inv = lambda x, y: (y - y_translate, (height - 1) - (x - x_translate))
        elif transformation == "RO2":
            f = lambda x, y: ((width - 1) - x + x_translate, (height - 1) - y + y_translate)
            f_inv = lambda x, y: ((width - 1) - (x - x_translate), (height - 1) - (y - y_translate))
        elif transformation == "RO3":
            f = lambda x, y:  (y + x_translate, (height - 1) - x + y_translate)
            f_inv = lambda x, y: ((height - 1) - (y - y_translate), x - x_translate)
        elif transformation == "RE-":
            f = lambda x, y: (x + x_translate, (height - 1) - y + y_translate)
            f_inv = lambda x, y: (x - x_translate, (height - 1) - (y - y_translate))
        elif transformation == "RE\\":
            f = lambda x, y: (y + x_translate, x + y_translate)
            f_inv = lambda x, y: (y - y_translate, x - x_translate)
        elif transformation == "RE|":
            f = lambda x, y: ((width - 1) - x + x_translate, y + y_translate)
            f_inv = lambda x, y: ((width - 1) - (x - x_translate), y - y_translate)
        elif transformation == "RE/":
            f = lambda x, y: ((height - 1) - y + x_translate, (height - 1) - x + y_translate)
            f_inv = lambda x, y: ((height - 1) - (y - y_translate), (height - 1) - (x - x_translate))

        cell_pairs = []

        for x in xrange(width):
            for y in xrange(height):
                for t in xrange(duration):
                    cell = self.grid[t][y][x]
                    if t < duration - period:
                        other_x, other_y = f(x,y)
                        if 0 <= other_x < width and 0 <= other_y < height:
                            other_cell = self.grid[t + period][other_y][other_x]
                        else:
                            other_cell = self.background_grid[(t + period) % background_duration][other_y % background_height][other_x % background_width]
                        cell_pairs.append((cell, other_cell))
                    if t >= period:
                        other_x, other_y = f_inv(x,y)
                        if 0 <= other_x < width and 0 <= other_y < height:
                            other_cell = self.grid[t - period][other_y][other_x]
                        else:
                            other_cell = self.background_grid[(t - period) % background_duration][other_y % background_height][other_x % background_width]
                        cell_pairs.append((cell, other_cell))
        return cell_pairs

    def force_at_least(self, literals, amount, indent = 0, verbosity = 0):
        """Adds clauses forcing at least the given amount of literals to be true"""

        starting_number_of_clauses = len(self.clauses.clause_set)
        name = self.define_cardinality_variable(literals, amount)
        self.clauses.append([name])
        print_message(
            "Number of clauses used: " + str(len(self.clauses.clause_set) - starting_number_of_clauses),
            3,
            indent = indent, verbosity = verbosity
        )


    def force_at_most(self, literals, amount, indent = 0, verbosity = 0):
        """Adds clauses forcing at most the given amount of literals to be true"""

        self.force_at_least(map(negate, literals), len(literals) - amount, indent = indent, verbosity = verbosity)


    def force_exactly(self, literals, amount, indent=0, verbosity=0):
        """Adds clauses forcing exactly the given amount of literals to be true"""

        self.force_at_least(literals, amount, indent = indent, verbosity = verbosity)
        self.force_at_most(literals, amount, indent = indent, verbosity = verbosity)

    def force_population_at_least(self, constraint, indent=0, verbosity=0):
        (times, population) = constraint
        print_message(
            "Forcing the population in generation" + ("s" if len(times) > 1 else "") + " " + ", ".join(str(t) for t in times) + " to be at least " + str(population),
            3,
            indent = indent, verbosity = verbosity
        )
        literals = [cell for t in times for row in self.grid[t] for cell in row]
        self.force_at_least(literals, population, indent = indent + 1, verbosity = verbosity)
        print_message(
            "Done\n",
            3,
            indent = indent, verbosity = verbosity
        )

    def force_population_at_most(self, constraint, indent = 0, verbosity = 0):
        (times, population) = constraint
        print_message(
            "Forcing the population in generation" + ("s" if len(times) > 1 else "") + " " + ", ".join(str(t) for t in times) + " to be at most " + str(population),
            3,
            indent = indent, verbosity = verbosity
        )
        literals = [cell for t in times for row in self.grid[t] for cell in row]
        self.force_at_most(literals, population, indent = indent + 1, verbosity = verbosity)
        print_message(
            "Done\n",
            3,
            indent = indent, verbosity = verbosity
        )

    def force_population_exactly(self, constraint, indent = 0, verbosity = 0):
        (times, population) = constraint
        print_message(
            "Forcing the population in generation" + ("s" if len(times) > 1 else "") + " " + ", ".join(str(t) for t in times) + " to be exactly " + str(population),
            3,
            indent = indent, verbosity = verbosity
        )
        literals = [cell for t in times for row in self.grid[t] for cell in row]
        self.force_exactly(literals, population, indent = indent + 1, verbosity = verbosity)
        print_message(
            "Done\n",
            3,
            indent = indent, verbosity = verbosity
        )

    def force_equal(self, argument_0, argument_1 = None):

        if argument_1 != None:
            assert isinstance(argument_0, basestring) and isinstance(argument_1, basestring), "force_equal arguments not understood"
            cell_pair_list = [(argument_0, argument_1)]
        elif argument_0 == []:
            return
        elif isinstance(argument_0[0], basestring):
                assert len(argument_0) == 2 and isinstance(argument_0[1], basestring), "force_equal arguments not understood"
                cell_pair_list = [argument_0]
        else:
            cell_pair_list = argument_0


        replacement = {}
        replaces = {}

        for cell_0, cell_1 in cell_pair_list:
            while cell_0 not in ["0", "1"]:
                variable_0, negated_0 = variable_from_literal(cell_0)
                if replacement.has_key(variable_0):
                    cell_0 = negate(replacement[variable_0], negated_0)
                else:
                    break
            while cell_1 not in ["0", "1"]:
                variable_1, negated_1 = variable_from_literal(cell_1)
                if replacement.has_key(variable_1):
                    cell_1 = negate(replacement[variable_1], negated_1)
                else:
                    break
            if cell_0 != cell_1:
                if cell_0 == negate(cell_1):
                    raise UnsatInPreprocessing
                elif cell_0 in ["0", "1"]:
                    cell_0, cell_1 = cell_1, cell_0

                variable_0, negated_0 = variable_from_literal(cell_0)
                cell_0, cell_1 = variable_0, negate(cell_1, negated_0)

                if cell_1 not in ["0", "1"]:
                    variable_1, negated_1 = variable_from_literal(cell_1)
                    if not replaces.has_key(variable_1):
                        replaces[variable_1] = []

                if replaces.has_key(variable_0):
                    for variable in replaces[variable_0]:
                        replacement_variable, replacement_negated = variable_from_literal(replacement[variable])
                        replacement[variable] = negate(cell_1, replacement_negated)
                        if cell_1 not in ["0", "1"]:
                            replaces[variable_1].append(variable)
                    del replaces[variable_0]

                replacement[variable_0] = cell_1
                if cell_1 not in ["0", "1"]:
                    replaces[variable_1].append(variable_0)

        for t, generation in enumerate(self.grid):
            for y, row in enumerate(generation):
                for x, cell in enumerate(row):
                    if cell not in ["0", "1"]:
                        variable, negated = variable_from_literal(cell)
                        if replacement.has_key(variable):
                            if replacement[variable] != variable:
                                self.grid[t][y][x] = negate(replacement[variable], negated)

        for t, generation in enumerate(self.background_grid):
            for y, row in enumerate(generation):
                for x, cell in enumerate(row):
                    if cell not in ["0", "1"]:
                        variable, negated = variable_from_literal(cell)
                        if replacement.has_key(variable):
                            if replacement[variable] != variable:
                                self.background_grid[t][y][x] = negate(replacement[variable], negated)

        for transition, literal in self.rule.items():
            if literal not in ["0", "1"]:
                variable, negated = variable_from_literal(literal)
                if replacement.has_key(variable):
                    if replacement[variable] != variable:
                        self.rule[transition] = negate(replacement[variable], negated)

    def force_unequal(self, argument_0, argument_1 = None):
        if argument_1 != None:
            assert isinstance(argument_0, basestring) and isinstance(argument_1, basestring), "force_equal arguments not understood"
            cell_pair_list = [(argument_0, argument_1)]
        elif argument_0 == []:
            return
        elif isinstance(argument_0[0], basestring):
                assert len(argument_0) == 2 and isinstance(argument_0[1], basestring), "force_equal arguments not understood"
                cell_pair_list = [argument_0]
        else:
            cell_pair_list = argument_0

        clause = []
        for cell_pair in cell_pair_list:
                cells_equal = str(cell_pair[0]) + "_equals_" + str(cell_pair[1])
                self.clauses.append(implies(cell_pair, cells_equal))
                self.clauses.append(implies(map(negate, cell_pair), cells_equal))
                clause.append(negate(cells_equal))

        self.clauses.append(clause)


    def make_string(self, pattern_output_format = None, determined = None, show_background = None, indent = 0, verbosity = 0):
        if pattern_output_format == None:
            pattern_output_format = LLS_defaults.pattern_output_format

        print_message('Formatting output...', 3, indent = indent, verbosity = verbosity)

        assert pattern_output_format in ["rle","csv"], "Format not recognised"

        background_grid = copy.deepcopy(self.background_grid)
        LLS_literal_manipulation.offset_background(background_grid,-1,-1,0)
        background_ignore_transition = copy.deepcopy(self.background_ignore_transition)
        LLS_literal_manipulation.offset_background(background_ignore_transition,-1,-1,0)

        if pattern_output_format == "rle":
            output_string = LLS_formatting.make_rle(
                self.grid,
                background_grid = background_grid,
                rule = self.rule,
                determined = determined,
                show_background = show_background,
                indent = indent + 1, verbosity = verbosity
            )
        elif pattern_output_format == "csv":
            output_string = LLS_formatting.make_csv(
                self.grid,
                ignore_transition = self.ignore_transition,
                background_grid = background_grid,
                background_ignore_transition = background_ignore_transition,
                rule = self.rule,
                determined = determined,
                show_background = show_background,
                indent = indent + 1, verbosity = verbosity
            )

        print_message('Done\n', 3, indent = indent, verbosity = verbosity)

        return output_string




    def substitute_solution(self, solution, indent = 0, verbosity = 0):
        """Return a copy of the search_pattern with the solution substituted back into it"""
        grid = copy.deepcopy(self.grid)
        rule = copy.deepcopy(self.rule)
        background_grid = copy.deepcopy(self.background_grid)

        print_message('Substituting solution back into search grid...', 3, indent = indent, verbosity = verbosity)

        # Remove the first line that just says "SAT", and split into a list of literals
        solution = set(solution.split("\n")[1].split())

        for t, generation in enumerate(grid):
            for y, row in enumerate(generation):
                for x, cell in enumerate(row):
                    if cell in ["0","1"]:
                        pass
                    else:
                        (CNF_variable, negated) = variable_from_literal(cell)
                        if self.clauses.DIMACS_literal_from_variable.has_key(CNF_variable):
                            DIMACS_variable = self.clauses.DIMACS_literal_from_variable[CNF_variable]

                            DIMACS_literal = negate(DIMACS_variable, negated)

                            if DIMACS_literal in solution:
                                grid[t][y][x] = "1"
                            else:
                                grid[t][y][x] = "0"
                        else:
                            grid[t][y][x] = "0"

        for t, generation in enumerate(background_grid):
            for y, row in enumerate(generation):
                for x, cell in enumerate(row):
                    if cell in ["0","1"]:
                        pass
                    else:
                        (CNF_variable, negated) = variable_from_literal(cell)
                        if self.clauses.DIMACS_literal_from_variable.has_key(CNF_variable):
                            DIMACS_variable = self.clauses.DIMACS_literal_from_variable[CNF_variable]

                            DIMACS_literal = negate(DIMACS_variable, negated)

                            if DIMACS_literal in solution:
                                background_grid[t][y][x] = "1"
                            else:
                                background_grid[t][y][x] = "0"
                        else:
                            background_grid[t][y][x] = "0"

        for transition, literal in rule.items():
            if literal in ["0","1"]:
                pass
            else:
                (CNF_variable, negated) = variable_from_literal(literal)
                if self.clauses.DIMACS_literal_from_variable.has_key(CNF_variable):
                    DIMACS_variable = self.clauses.DIMACS_literal_from_variable[CNF_variable]

                    DIMACS_literal = negate(DIMACS_variable, negated)

                    if DIMACS_literal in solution:
                        rule[transition] = "1"
                    else:
                        rule[transition] = "0"
                else:
                    rule[transition] = "0"
        width = len(grid[0][0])
        height = len(grid[0])
        duration = len(grid)
        print_message('Done\n', 3, indent = indent, verbosity = verbosity)

        return SearchPattern(grid, background_grid = background_grid, rule = rule, add_border = False)



    def deterministic(self, indent = 0, verbosity = 0):
        print_message("Checking if pattern is deterministic...", 3, indent = indent, verbosity = verbosity)
        determined = [[[False for cell in row] for row in generation] for generation in self.grid]
        determined_variables = set()
        width = len(self.grid[0][0])
        height = len(self.grid[0])

        while True:
            determined_copy = copy.deepcopy(determined)
            for t, generation in enumerate(self.grid):
                for y, row in enumerate(generation):
                    for x, cell in enumerate(row):
                        if not determined[t][y][x]:
                            if cell in ["0", "1"]:
                                determined[t][y][x] = True
                            else:
                                variable, negated = variable_from_literal(cell)
                                if t == 0:
                                    determined[t][y][x] = True
                                    determined_variables.add(variable)
                                elif variable in determined_variables:
                                    determined[t][y][x] = True
                                elif all(determined[t -1][y + y_offset][x + x_offset] for x_offset in range(2) for y_offset in range(2) if x + x_offset in range(width) and y + y_offset in range(height)) and not self.ignore_transition[t][y][x]:
                                    determined[t][y][x] = True
                                    determined_variables.add(variable)
            if determined == determined_copy:
                break

        print_message("Done\n", 3, indent = indent, verbosity = verbosity)
        if all(flag for generation in determined for row in generation for flag in row):
            return True
        else:
            return False

    def background_nontrivial(self):
        return (
            len(self.background_grid[0]) > 1
            and len(self.background_grid[0][0]) > 1
            and any(cell not in ["0","1"] for generation in self.background_grid for row in generation for cell in row)
        )
