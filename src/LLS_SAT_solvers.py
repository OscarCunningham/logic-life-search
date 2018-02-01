import time
import subprocess
import threading
import os
import errno
import sys
import re
import LLS_files
import LLS_defaults
from LLS_messages import print_message


def SAT_solve(DIMACS_string, solver=None, parameters=None, timeout=None, save_dimacs = None, dry_run = None, indent = 0, verbosity = 0):
    """Solve the given DIMACS problem, using the specified SAT solver"""
    print_message('Preparing SAT solver input...', 3, indent = indent, verbosity = verbosity)
    solvers = [
        "minisat",
        "MapleCOMSPS",
        "MapleCOMSPS_LRB",
        "riss",
        "glucose",
        "glucose-syrup",
        "lingeling",
        "plingeling",
        "treengeling"]
    try:
        if solver is None:
            solver = LLS_defaults.solver
        elif int(solver) in range(len(solvers)):
            solver = solvers[solver] # Allow solver to be specified by number
    except ValueError:
        pass

    assert solver in solvers, "Solver not found"

    if isinstance(save_dimacs, basestring):
        dimacs_file = save_dimacs
    else:
        dimacs_file = "lls_dimacs.cnf"
        file_number = 0
        while os.path.isfile(dimacs_file):
            file_number += 1
            dimacs_file = "lls_dimacs" + str(file_number) + ".cnf"

    # The solvers prefer their input as a file, so write it out
    LLS_files.file_from_string(dimacs_file, DIMACS_string, indent = indent + 1, verbosity = verbosity)

    print_message('Done\n', 3, indent = indent, verbosity = verbosity)
    if not dry_run:
        solution, time_taken = use_solver(solver, dimacs_file, parameters = parameters, timeout = timeout, indent = indent, verbosity = verbosity)
    else:
        solution = "DRYRUN\n"
        time_taken = None

    if save_dimacs == None:
        print_message('Removing DIMACS file...', 3, indent = indent, verbosity = verbosity)
        try:
            os.remove(dimacs_file)
        except OSError as e:
            if e.errno == errno.ENOENT:
                print_message('DIMACS file "' + dimacs_file + '" not found', 3, indent = indent + 1, verbosity = verbosity)
            else:
                raise
        print_message('Done\n', 3, indent = indent, verbosity = verbosity)

    return solution, time_taken

def use_solver(solver, file_name, parameters = None, timeout = None, indent = 0, verbosity = 0):

    if parameters != None:
        parameter_list = parameters.strip(" ").split(" ")
    else:
        parameter_list = []

    solver_path = sys.path[0] + "/solvers/" + solver

    if solver in ["minisat","MapleCOMSPS","MapleCOMSPS_LRB","riss"]:
        command = [solver_path, file_name, "temp_SAT_solver_output"] + parameter_list
    elif solver in ["lingeling","plingeling","treengeling"]:
        command = [solver_path, file_name] + parameter_list
    elif solver in ["glucose", "glucose-syrup"]:
        command = [solver_path, file_name, "-model"] + parameter_list
    else:
        assert False, "Solver not recognised"

    solver_process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE)

    timeout_flag = [False] #We want the flag to be mutable, so we put it into a little box.

    def timeout_function(solver_process, timeout_flag):
        solver_process.kill()
        timeout_flag[0] = "TIMEOUT"

    timeout_timer = threading.Timer(timeout, timeout_function, [solver_process, timeout_flag])

    print_message('Solving with "' + solver + '" ... (Start time: ' + time.ctime() + ")", 3, indent = indent, verbosity = verbosity)

    try:
        start_time = time.time()
        timeout_timer.start()
        out, error = solver_process.communicate()
    except KeyboardInterrupt:
        solver_process.kill()
        timeout_flag[0] = "SIGINT"
    finally:
        timeout_timer.cancel()
        time_taken = time.time() - start_time

    if not timeout_flag[0]:
        print_message('Done\n', 3,  indent = indent, verbosity = verbosity)

        print_message('Formatting SAT solver output...', 3, indent = indent, verbosity = verbosity)

        if solver in ["minisat","MapleCOMSPS","MapleCOMSPS_LRB","riss"]:
            solution = LLS_files.string_from_file("temp_SAT_solver_output", indent = indent + 1, verbosity = verbosity)
            print_message('Removing SAT solver output file...', 3, indent = indent+1, verbosity = verbosity)
            os.remove("temp_SAT_solver_output")
            print_message('Done\n', 3, indent = indent + 1, verbosity = verbosity)
        elif solver in ["lingeling","plingeling","treengeling"]:
            solution = out.split("\ns ")[1].split("\nc")[0].split("\nv ")
            solution = solution[0] + "\n" + " ".join(solution[1:])
        elif solver in ["glucose", "glucose-syrup"]:
            try:
                solution = out.split("\ns ")[1]
                solution = re.sub("s ", "", solution)
                solution = re.sub("v ", "", solution)
            except IndexError:
                solution = "UNSAT\n"

        if solver == "MapleCOMSPS_LRB":
            if solution == "":
                solution = "UNSAT\n"
        if solver == "riss":
            solution = re.sub("s ", "", solution)
            solution = re.sub("v ", "", solution)
        if "UNSAT" in solution.upper():
            solution = "UNSAT\n"

        print_message("SAT solver output:", 3, indent = indent + 1, verbosity = verbosity)
        print_message(out, 3, indent = indent + 2, verbosity = verbosity)
        print_message('Error (if any): "' + error + '"', 3, indent = indent + 1, verbosity = verbosity)
        print_message('Time taken: ' + str(time_taken), 3, indent = indent + 1, verbosity = verbosity)
        print_message('Done\n', 3, indent = indent, verbosity = verbosity)

    else:
        print_message('Timed out\n', 3, indent = indent, verbosity = verbosity) #TODO: How to capture output from SAT solver after killing it?
        solution = "TIMEOUT\n"

    return solution, time_taken
