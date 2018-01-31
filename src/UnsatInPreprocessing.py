class UnsatInPreprocessing(Exception):
    """
    Unsatisfiability proved before SAT solver is run

    Can be called because it's impossible to continue preprocessing
    with an unsatifiable instance (for example
    "search_pattern.force_equal('0', '1')") or just to complete more quickly.

    """
    pass
