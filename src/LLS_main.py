import os
import LLS_files
import LLS_formatting
import LLS_SAT_solvers
import LLS_defaults
from UnsatInPreprocessing import UnsatInPreprocessing
from LLS_messages import print_message
from LLS_literal_manipulation import negate


def LLS(
    search_pattern,
    symmetries=[],
    asymmetries=[],
    population_at_most=[],
    population_at_least=[],
    population_exactly=[],
    force_change=[],
    force_evolution=True,
    solver=None,
    parameters=None,
    timeout=None,
    save_dimacs=None,
    save_state=None,
    method=None,
    dry_run=False,
    number_of_solutions=None,
    pattern_output_format=None,
    output_file_name=None,
    indent=0, verbosity=0
):
    """The central part of LLS. Controls the flow of the program"""

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
        symmetries = symmetries,
        asymmetries = asymmetries,
        population_at_most = population_at_most,
        population_at_least = population_at_least,
        population_exactly = population_exactly,
        force_change = force_change,
        solver = solver,
        parameters = parameters,
        timeout = timeout,
        save_dimacs = save_dimacs,
        save_state = save_state,
        method = method,
        dry_run = dry_run,
        indent = indent, verbosity = verbosity
    )

    # Check if the first generation of pattern determines the others

    solutions = []

    if sat == "SAT":
        determined = search_pattern.deterministic(indent = indent, verbosity = verbosity)
        show_background = search_pattern.background_nontrivial()
        solutions.append(solution)
        output_string = solution.make_string(
            pattern_output_format = pattern_output_format,
            determined = determined,
            show_background = show_background,
            indent = indent, verbosity = verbosity
        )
    else:
        output_string = ["Unsatisfiable", "Timed Out","Dry run"][["UNSAT", "TIMEOUT", "DRYRUN"].index(sat)]
    print_message(output_string + "\n", 1, indent = indent, verbosity = verbosity)
    if output_file_name:
        print_message('Writing to output file...', indent = indent, verbosity = verbosity)
        LLS_files.append_to_file_from_string(output_file_name, output_string, indent = indent + 1, verbosity = verbosity)
        print_message('Done\n', indent = indent, verbosity = verbosity)

    #Deal with the case where we need more than one solution
    if number_of_solutions and sat == "SAT" and not dry_run:
        if number_of_solutions != "Infinity":
            number_of_solutions = int(number_of_solutions)
            enough_solutions = (len(solutions) >= number_of_solutions)
        else:
            enough_solutions = False

        while sat == "SAT" and not enough_solutions:
            #Force the new solution to be different
            search_pattern.force_distinct(solution, determined = determined)
            #No need to apply the constraints again
            (
                solution,
                sat,
                _,
                _,
                _,
                _,
                _,
                _,
                extra_time_taken
            ) = preprocess_and_solve(
                search_pattern,
                solver = solver,
                parameters = parameters,
                timeout = timeout,
                method = method,
                force_evolution = False,
                indent = indent, verbosity = verbosity
            )
            time_taken += extra_time_taken
            if sat == "SAT":
                solutions.append(solution)
                output_string = solution.make_string(pattern_output_format = pattern_output_format, determined = determined, show_background = show_background, indent = indent, verbosity = verbosity)
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
    symmetries=[],
    asymmetries=[],
    population_at_most=[],
    population_at_least=[],
    population_exactly=[],
    force_change=[],
    force_evolution=True,
    solver=None,
    parameters=None,
    timeout=None,
    save_dimacs=None,
    save_state=None,
    method=None,
    dry_run=False,
    indent=0, verbosity=0
):
    """Preprocess and solve the search pattern"""
    try:
        preprocess(
            search_pattern,
            symmetries = symmetries,
            asymmetries = asymmetries,
            population_at_most = population_at_most,
            population_at_least = population_at_least,
            population_exactly = population_exactly,
            force_change = force_change,
            method = method,
            indent = indent, verbosity = verbosity
        )
        if save_state:
            if isinstance(save_state, basestring):
                state_file = save_state
            else:
                state_file = "lls_state.pkl"
                file_number = 0
                while os.path.isfile(state_file):
                    file_number += 1
                    state_file = "lls_state" + str(file_number) + ".pkl"
            print_message("Saving state...", 3, indent = indent + 1, verbosity = verbosity)
            LLS_files.file_from_object(
                state_file,
                (search_pattern.grid, search_pattern.ignore_transition, search_pattern.background_grid, search_pattern.background_ignore_transition, search_pattern.rule, search_pattern.clauses.DIMACS_literal_from_variable),
                indent = indent + 2, verbosity = verbosity
            )
            print_message("Done\n", 3, indent = indent + 1, verbosity = verbosity)
        # Problem statistics
        width = len(search_pattern.grid[0][0])
        height = len(search_pattern.grid[0])
        duration = len(search_pattern.grid)
        active_width = sum(
            any(
            any(
            (search_pattern.grid[t][y][x] not in ["0","1"])
            for y in range(height))
            for t in range(duration))
            for x in range(width)
        )
        active_height = sum(
            any(
            any(
            (search_pattern.grid[t][y][x] not in ["0","1"])
            for t in range(duration))
            for x in range(width))
            for y in range(height)
        )
        active_duration = sum(
            any(
            any(
            (search_pattern.grid[t][y][x] not in ["0","1"])
            for x in range(width))
            for y in range(height))
            for t in range(duration)
        )
        number_of_cells = search_pattern.number_of_cells()
        number_of_variables = search_pattern.clauses.number_of_variables
        number_of_clauses = len(search_pattern.clauses.clause_set)
        print_message('Number of undetermined cells: ' + str(number_of_cells), indent = indent, verbosity = verbosity)
        print_message('Number of variables: ' + str(number_of_variables), indent = indent, verbosity = verbosity)
        print_message('Number of clauses: ' + str(number_of_clauses) + "\n", indent = indent, verbosity = verbosity)
        print_message('Active width: ' + str(active_width), indent = indent, verbosity = verbosity)
        print_message('Active height: ' + str(active_height), indent = indent, verbosity = verbosity)
        print_message('Active duration: ' + str(active_duration) + "\n", indent = indent, verbosity = verbosity)
    except UnsatInPreprocessing:
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
        ) = (
            None,
            "UNSAT",
            None,
            None,
            None,
            None,
            None,
            None,
            0
        )
        print_message("Unsatisfiability proved in preprocessing", indent = indent + 1, verbosity = verbosity)
        print_message('Done\n', indent = indent, verbosity = verbosity)
    else:
        (
            solution,
            sat,
            time_taken
        ) = LLS_SAT_solvers.SAT_solve(
            search_pattern,
            solver = solver,
            parameters = parameters,
            timeout = timeout,
            save_dimacs = save_dimacs,
            dry_run = dry_run,
            indent = indent, verbosity = verbosity
        )
    if not dry_run:
        print_message(
            'Time taken: ' + str(time_taken) + " seconds\n",
            indent = indent, verbosity = verbosity
        )
    return solution, sat, number_of_cells, number_of_variables, number_of_clauses, active_width, active_height, active_duration, time_taken


def preprocess(
    search_pattern,
    symmetries=[],
    asymmetries=[],
    population_at_most=[],
    population_at_least=[],
    population_exactly=[],
    force_change=[],
    force_evolution=True,
    method=None,
    indent=0, verbosity=0
):
    """Apply constraints and create SAT problem"""
    print_message('Preprocessing...', indent = indent, verbosity = verbosity)

    # Constraints that change the grid
    search_pattern.standardise_varaibles_names(indent = indent + 1, verbosity = verbosity)
    for symmetry in symmetries:
        search_pattern.force_symmetry(symmetry, indent = indent + 1, verbosity = verbosity)

    search_pattern.remove_redundancies(indent = indent + 1, verbosity = verbosity)
    search_pattern.standardise_varaibles_names(indent = indent + 1, verbosity = verbosity)

    print_message(
        "Search grid:\n",
        3,
        indent = indent + 1, verbosity = verbosity)
    print_message(
        search_pattern.make_string(pattern_output_format = "csv", show_background = True),
        3,
        indent = indent + 2, verbosity = verbosity)

    #Constraints that are enforced by clauses
    for asymmetry in asymmetries:
        search_pattern.force_asymmetry(asymmetry, indent = indent + 1, verbosity = verbosity)
    for constraint in population_at_most:
        search_pattern.force_population_at_most(constraint, indent = indent + 1, verbosity = verbosity)
    for constraint in population_at_least:
        search_pattern.force_population_at_least(constraint, indent = indent + 1, verbosity = verbosity)
    for constraint in population_exactly:
        search_pattern.force_population_exactly(constraint, indent = indent + 1, verbosity = verbosity)
    for times in force_change:
        search_pattern.force_change(times, indent = indent + 1, verbosity = verbosity)


    if force_evolution:
        # The most important bit. Enforces the evolution rules
        search_pattern.force_evolution(method=method, indent = indent + 1, verbosity = verbosity)
    print_message('Done\n', indent = indent, verbosity = verbosity)
