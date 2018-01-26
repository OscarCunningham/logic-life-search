
import LLS_files
import LLS_formatting
from SearchPattern import SearchPattern
from LLS_messages import print_message
import LLS_DIMACS
import LLS_SAT_solvers
from UnsatInPreprocessing import UnsatInPreprocessing
import copy
from LLS_literal_manipulation import negate

def preprocess_solve_and_postprocess(search_pattern,
                  symmetry = "C1",
                  period = None,
                  x_translate = 0,
                  y_translate = 0,
                  force_movement = False,
                  solver = None,
                  parameters = None,
                  timeout = None,
                  save_dimacs = None,
                  method = None,
                  force_at_most = [],
                  force_at_least = [],
                  force_change = [],
                  force_nonempty = False,
                  force_evolution = True,
                  dry_run = False,
                  number_of_solutions = None,
                  pattern_output_format = "rle",
                  output_file_name = None,
                  indent = 0, verbosity = 0):
    (
        solution,
        sat,
        number_of_cells,
        number_of_variables,
        number_of_clauses,
        active_width,
        active_height,
        active_duration,
        time_taken
    ) = preprocess_and_solve(
        search_pattern,
        symmetry = symmetry,
        period = period,
        x_translate = x_translate,
        y_translate = y_translate,
        force_movement = force_movement,
        solver = solver,
        parameters = parameters,
        timeout = timeout,
        save_dimacs = save_dimacs,
        method = method,
        force_at_most = force_at_most,
        force_at_least = force_at_least,
        force_change = force_change,
        force_nonempty = force_nonempty,
        force_evolution = force_evolution,
        dry_run = dry_run,
        indent = indent, verbosity = verbosity
    )
    determined = search_pattern.deterministic()
    solutions = []
    if sat == "SAT":
        solutions.append(solution)
        output_string = solution.make_string(pattern_output_format = pattern_output_format, determined = determined, indent = indent, verbosity = verbosity)
    else:
        output_string = ["Unsatisfiable", "Timed Out","Dry run"][["UNSAT", "TIMEOUT", "DRYRUN"].index(sat)]

    print_message(output_string + "\n", 1, indent = indent, verbosity = verbosity)
    if output_file_name:
        print_message('Writing to output file...', indent = indent, verbosity = verbosity)
        LLS_files.append_to_file_from_string(output_file_name, output_string, indent = indent + 1, verbosity = verbosity)
        print_message('Done\n', indent = indent, verbosity = verbosity)

    if number_of_solutions and sat == "SAT" and not dry_run:
        if number_of_solutions != "Infinity":
            number_of_solutions = int(number_of_solutions)
            enough_solutions = (len(solutions) >= number_of_solutions)
        else:
            enough_solutions = False
        while sat == "SAT" and not enough_solutions:
            search_pattern.force_distinct(solution, determined = determined)
            (solution,
             sat,
             _,
             _,
             _,
             _,
             _,
             _,
             extra_time_taken) = preprocess_and_solve(search_pattern,
                                             solver = solver,
                                             parameters = parameters,
                                             timeout = timeout,
                                             method = method,
                                             force_evolution = False,
                                             indent = indent, verbosity = verbosity)
            time_taken += extra_time_taken
            if sat == "SAT":
                solutions.append(solution)
                output_string = solution.make_string(pattern_output_format = pattern_output_format, determined = determined, indent = indent, verbosity = verbosity)
                if verbosity == 1:
                    print_message("", 1, indent = indent, verbosity = verbosity)
            else:
                output_string = ["Unsatisfiable", "Timed Out","Dry run"][["UNSAT", "TIMEOUT",None].index(sat)]
            print_message(output_string + "\n", 1, indent = indent, verbosity = verbosity)
            if output_file_name:
                print_message('Writing output file...', indent = indent, verbosity = verbosity)
                LLS_files.append_to_file_from_string(output_file_name, output_string, indent = indent + 1, verbosity = verbosity)
                print_message('Done\n', indent = indent, verbosity = verbosity)
            if number_of_solutions != "Infinity":
                enough_solutions = (len(solutions) >= number_of_solutions)
        sat = "SAT"
        print_message('Total solver time: ' + str(time_taken), indent = indent, verbosity = verbosity)

    return solutions, sat, number_of_cells, number_of_variables, number_of_clauses, active_width, active_height, active_duration, time_taken

def preprocess_and_solve(search_pattern,
                  symmetry = "C1",
                  period = None,
                  x_translate = 0,
                  y_translate = 0,
                  force_movement = False,
                  solver = None,
                  parameters = None,
                  timeout = None,
                  save_dimacs = None,
                  method = None,
                  force_at_most = [],
                  force_at_least = [],
                  force_change = [],
                  force_nonempty = False,
                  force_evolution = True,
                  dry_run = False,
                  indent = 0, verbosity = 0):
    try:
        DIMACS_string, DIMACS_variables_from_CNF_list_variables, number_of_variables, number_of_clauses, number_of_cells = preprocess(search_pattern,
                          symmetry = symmetry,
                          period = period,
                          x_translate = x_translate,
                          y_translate = y_translate,
                          force_movement = force_movement,
                          method = method,
                          force_at_most = force_at_most,
                          force_at_least = force_at_least,
                          force_change = force_change,
                          force_nonempty = force_nonempty,
                          force_evolution = force_evolution,
                          indent = indent, verbosity = verbosity)
        width = len(search_pattern.grid[0][0])
        height = len(search_pattern.grid[0])
        duration = len(search_pattern.grid)
        active_width = sum(any(any((search_pattern.grid[z][y][x] not in ["0","1"]) for y in range(height)) for z in range(duration)) for x in range(width))
        active_height = sum(any(any((search_pattern.grid[z][y][x] not in ["0","1"]) for z in range(duration)) for x in range(width)) for y in range(height))
        active_duration = sum(any(any((search_pattern.grid[z][y][x] not in ["0","1"]) for x in range(width)) for y in range(height)) for z in range(duration))
        print_message('Number of undetermined cells: ' + str(number_of_cells), indent = indent, verbosity = verbosity)
        print_message('Number of variables: ' + str(number_of_variables), indent = indent, verbosity = verbosity)
        print_message('Number of clauses: ' + str(number_of_clauses) + "\n", indent = indent, verbosity = verbosity)
        print_message('Active width: ' + str(active_width), indent = indent, verbosity = verbosity)
        print_message('Active height: ' + str(active_height), indent = indent, verbosity = verbosity)
        print_message('Active duration: ' + str(active_duration) + "\n", indent = indent, verbosity = verbosity)
    except UnsatInPreprocessing:
            solution, sat, number_of_cells, number_of_variables, number_of_clauses, active_width, active_height, active_duration, time_taken = None, "UNSAT", None, None, None, None, None, None, 0
            print_message("Unsatisfiability proved in preprocessing", indent = indent + 1, verbosity = verbosity)
            print_message('Done\n', indent = indent, verbosity = verbosity)
    else:
        solution, sat, time_taken = solve(search_pattern, DIMACS_string, DIMACS_variables_from_CNF_list_variables,
            solver = solver,
            parameters = parameters,
            timeout = timeout,
            save_dimacs = save_dimacs,
            dry_run = dry_run,
            indent = indent, verbosity = verbosity)
    if not dry_run:
        print_message('Time taken: ' + str(time_taken) + " seconds\n", indent = indent, verbosity = verbosity)
    return solution, sat, number_of_cells, number_of_variables, number_of_clauses, active_width, active_height, active_duration, time_taken


def preprocess(search_pattern,
                  symmetry = "C1",
                  period = None,
                  x_translate = 0,
                  y_translate = 0,
                  force_movement = False,
                  method = None,
                  force_at_most = False,
                  force_at_least = False,
                  force_change = [],
                  force_nonempty = False,
                  force_evolution = True,
                  indent = 0, verbosity = 0):
    print_message('Preprocessing...', indent = indent, verbosity = verbosity)
    search_pattern.force_symmetry(symmetry, indent = indent + 1, verbosity = verbosity)
    search_pattern.force_period(period, x_translate, y_translate, indent = indent + 1, verbosity = verbosity)
    if force_nonempty:
        search_pattern.force_nonempty(indent = indent + 1, verbosity = verbosity)
    if force_movement:
        search_pattern.force_movement(indent = indent + 1, verbosity = verbosity)
    for t_0, t_1 in force_change:
        search_pattern.force_change(t_0, t_1, indent = indent + 1, verbosity = verbosity)
    for arguments in force_at_least:
        amount, ts = arguments[0], arguments[1:]
        if ts == []:
            ts = [0]
        if len(ts) == 1:
            print_message('Enforcing at least ' + str(amount) + ' cells in generation ' + str(ts[0]) + ' ...', 3, indent = indent+1, verbosity = verbosity)
        else:
            print_message('Enforcing at least ' + str(amount) + ' cells in generations ' + str(ts) + ' ...', 3, indent = indent+1, verbosity = verbosity)
        literals = []
        literals = [literal for t in ts for row in search_pattern.grid[t] for literal in row]
        search_pattern.force_at_least(literals, amount, indent = indent+1, verbosity = verbosity)
        print_message('Done\n', 3, indent = indent+1, verbosity = verbosity)
    for arguments in force_at_most:
        amount, ts = arguments[0], arguments[1:]
        if ts == []:
            ts = [0]
        if len(ts) == 1:
            print_message('Enforcing at most ' + str(amount) + ' cells in generation ' + str(ts[0]) + ' ...', 3, indent = indent+1, verbosity = verbosity)
        else:
            print_message('Enforcing at most ' + str(amount) + ' cells in generations ' + str(ts) + ' ...', 3, indent = indent+1, verbosity = verbosity)
        literals = [literal for t in ts for row in search_pattern.grid[t] for literal in row]
        search_pattern.force_at_most(literals, amount, indent = indent+1, verbosity = verbosity)
        print_message('Done\n', 3, indent = indent+1, verbosity = verbosity)
    search_pattern.optimise(indent = indent + 1, verbosity = verbosity)
    if force_evolution:
        search_pattern.force_evolution(method=method, indent = indent + 1, verbosity = verbosity)
        search_pattern.optimise(grid_changed = False, clauses_changed = True, indent = indent + 1, verbosity = verbosity)
    print_message("Search pattern optimised to:\n" + search_pattern.make_string(pattern_output_format = "csv") + "\n", 3, indent = indent + 1, verbosity = verbosity)
    DIMACS_string, DIMACS_variables_from_CNF_list_variables, number_of_variables, number_of_clauses = LLS_DIMACS.DIMACS_from_CNF_list(search_pattern.clauses, indent = indent + 1, verbosity = verbosity)
    number_of_cells = search_pattern.number_of_cells()
    print_message('Done\n', indent = indent, verbosity = verbosity)
    return DIMACS_string, DIMACS_variables_from_CNF_list_variables, number_of_variables, number_of_clauses, number_of_cells


def solve(search_pattern, DIMACS_string, DIMACS_variables_from_CNF_list_variables,
    solver = None,
    parameters = None,
    timeout = None,
    save_dimacs = None,
    dry_run = None,
    indent = 0, verbosity = 0):
    print_message('Solving...', indent = indent, verbosity = verbosity)
    DIMACS_solution, time_taken = LLS_SAT_solvers.SAT_solve(
        DIMACS_string, solver=solver, parameters=parameters, timeout=timeout, save_dimacs = save_dimacs, dry_run = dry_run, indent = indent + 1, verbosity = verbosity)
    if DIMACS_solution not in ["UNSAT\n", "TIMEOUT\n", "DRYRUN\n"]:
        sat = "SAT"
        solution = search_pattern.substitute_solution(DIMACS_solution, DIMACS_variables_from_CNF_list_variables, indent = indent + 1, verbosity = verbosity)
    else:
        sat = DIMACS_solution[:-1]
        solution = None
    print_message('Done\n', indent = indent, verbosity = verbosity)
    return solution, sat, time_taken
