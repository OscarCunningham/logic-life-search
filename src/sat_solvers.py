import time
import subprocess
import sys
import enum
import settings
import src.formatting
from src.logging import log


class Status(enum.Enum):
    SAT = 'Satisfiable'
    UNSAT = 'Unsatisfiable'
    TIMEOUT = 'Timed out'
    DRYRUN = 'Dry run'
    ERROR = 'Error'


def sat_solve(dimacs_string, solver=None, parameters=None, timeout=None):
    """Solve the given DIMACS problem, using the specified SAT solver"""

    log('Solving...', 1, 2)

    if solver is None:
        solver = settings.solver

    parameter_list = parameters.strip(" ").split(" ") if parameters is not None else []
    solver_path = sys.path[0] + "/solvers/" + solver
    command = [solver_path] + parameter_list

    log('Solving with "' + solver + '" ... (Start time: ' + time.ctime() + ")", 1)

    try:
        start_time = time.time()
        sat_solver_process = subprocess.run(
            command,
            input=dimacs_string,
            capture_output=True,
            timeout=timeout,
            encoding="utf-8"
        )
        end_time = time.time()
    except subprocess.TimeoutExpired as error:
        end_time = time.time()
        log('Timed out\n', -1)
        log("SAT solver output:", 1)
        log(error.stdout.decode("utf-8"))
        log('Done\n', -1)
        log('Done\n', -1,2)
        return Status.TIMEOUT, None, end_time - start_time

    log('Done\n', -1)
    time_taken = end_time - start_time
    log('Time taken: ' + str(time_taken))

    if sat_solver_process.stderr:
        log('Error: "' + sat_solver_process.stderr + '"')
        return Status.ERROR, None, None

    out = sat_solver_process.stdout
    log("SAT solver output:", 1)
    log(out)
    log('Done\n', -1)
    log('Parsing SAT solver output...', 1)
    status, solution = src.formatting.format_dimacs_output(out)
    log('Done\n', -1)

    log('Done\n', -1,2)
    return status, solution, time_taken
