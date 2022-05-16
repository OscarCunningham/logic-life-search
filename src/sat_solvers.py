import time
import subprocess
import threading
import sys
import enum
import settings
from src.logging import log

class Status(enum.Enum):
    SAT = 'Satisfiable'
    UNSAT = 'Unsatisfiable'
    TIMEOUT = 'Timed out'
    DRYRUN = 'Dry run'
    INTERRUPT = 'Keyboard interrupt'
    ERROR = 'Error'

def sat_solve(search_pattern, solver=None, parameters=None, timeout=None):
    """Solve the given DIMACS problem, using the specified SAT solver"""

    log('Solving...', 1)

    if solver is None:
        solver = settings.solver

    dimacs_string = search_pattern.clauses.make_string()

    status, solution, time_taken = use_solver(solver, dimacs_string, parameters=parameters, timeout=timeout)

    if status == Status.SAT:
        solution = search_pattern.substitute_solution(solution)

    log('Done\n', -1)
    return status, solution, time_taken


def use_solver(solver, dimacs_string, parameters=None, timeout=None):
    parameter_list = parameters.strip(" ").split(" ") if parameters is not None else[]
    solver_path = sys.path[0] + "/solvers/" + solver
    command = [solver_path] + parameter_list

    solver_process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stdin=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    def kill(process):
        process.kill()

    timeout_timer = threading.Timer(timeout, kill, [solver_process])

    log('Solving with "' + solver + '" ... (Start time: ' + time.ctime() + ")", 1)

    keyboard_interrupt_flag = False
    start_time = time.time()
    timeout_timer.start()
    try:
        out, error = solver_process.communicate(dimacs_string.encode())
    except KeyboardInterrupt:
        solver_process.kill()
        keyboard_interrupt_flag = True
    end_time = time.time()
    timeout_flag = not timeout_timer.is_alive()
    timeout_timer.cancel()
    log('Done\n', -1)

    solution = None
    time_taken = end_time - start_time
    log('Time taken: ' + str(time_taken))

    if keyboard_interrupt_flag:
        status = Status.INTERRUPT
    elif timeout_flag:
        status = Status.TIMEOUT
    elif error:
        log('Error: "' + error.decode("utf-8") + '"')
        status = Status.ERROR
    else:
        out = out.decode("utf-8")
        log("SAT solver output:", 1)
        log(out)
        log('Done\n', -1)
        log('Parsing SAT solver output...', 1)
        status, solution = format_dimacs_output(out)
        log('Done\n', -1)

    return status, solution, time_taken


def format_dimacs_output(dimacs_output):

    lines = dimacs_output.strip('\n').split('\n')

    statuses = [line[2:] for line in lines if line[0] == 's']
    variable_lines = [line[2:] for line in lines if line[0] == 'v']

    if len(statuses) != 1:
        raise Exception('Wrong number of status lines')
    if statuses[0] == 'UNSATISFIABLE':
        return Status.UNSAT, None
    elif statuses[0] == 'SATISFIABLE':
        solution = set(literal for line in variable_lines for literal in line.split() if literal != '0')
        return Status.SAT, solution
