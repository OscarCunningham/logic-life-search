from LLS_literal_manipulation import variable_from_literal, negate
from LLS_messages import print_message

def DIMACS_from_CNF_list(clauses, indent = 0, verbosity = 0):
    """Convert CNF list-of-lists to DIMACS format"""

    print_message("Converting to DIMACS format...", 3, indent = indent, verbosity = verbosity)

    DIMACS_string = ""

    # In DIMACS format variables are called "1", "2", ... . So we will rename
    # all our variables. This keeps track of which numbers we've used
    number_of_variables = 0

    number_of_clauses = 0

    # We'll also build a dictionary of which of our old variables recieves
    # which new name
    DIMACS_variables_from_CNF_list_variables = {}
    for clause_number, clause in enumerate(clauses):
        DIMACS_clause = []
        for literal_number, literal in enumerate(clause):
            if literal == "0":
                pass
            elif literal == "1":
                break
            else:
                (variable, negated) = variable_from_literal(literal, DIMACS = True)

                # If we haven't seen it before then add it to the dictionary
                if not DIMACS_variables_from_CNF_list_variables.has_key(variable):
                    DIMACS_variables_from_CNF_list_variables[variable] = str(
                        number_of_variables + 1)
                    number_of_variables += 1  # We've used another number, so increment the counter

                DIMACS_clause.append(negate(DIMACS_variables_from_CNF_list_variables[variable], negated, DIMACS = True))
        else:
            DIMACS_string += "\n" + " ".join(DIMACS_clause) + " 0"
            number_of_clauses +=1


    # From our list of clauses create a string according to the DIMACS format
    DIMACS_string = "p cnf " + str(number_of_variables) + " " + str(number_of_clauses) + DIMACS_string
    print_message("Done\n", 3, indent = indent, verbosity = verbosity)

    return DIMACS_string, DIMACS_variables_from_CNF_list_variables, number_of_variables, number_of_clauses
