from src.LLS_messages import print_message
from src.LLS_literal_manipulation import negate, variable_from_literal

class ClauseList:


    def __init__(self):
        self.clause_set = set()
        self.number_of_variables = 0
        self.DIMACS_literal_from_variable = {}


    def __eq__(self, other):
        if other == None:
            return False
        else:
            return (self.clause_set == other.clause_set and self.number_of_variables == other.number_of_variables and self.DIMACS_literal_from_variable == other.DIMACS_literal_from_variable)


    def __ne__(self, other):
        return not __eq__(self, other)


    def append(self, clause):
        DIMACS_clause = []
        clause = set(clause)
        if "1" in clause:
            return
        for literal in clause:
            if literal == "0":
                pass
            else:
                (variable, negated) = variable_from_literal(literal)
                # If we haven't seen it before then add it to the dictionary
                if variable not in self.DIMACS_literal_from_variable:
                    self.DIMACS_literal_from_variable[variable] = str(self.number_of_variables + 1)
                    self.number_of_variables += 1
                elif negate(literal) in clause:
                     return
                DIMACS_clause.append(negate(self.DIMACS_literal_from_variable[variable], negated, DIMACS = True))
        DIMACS_clause.sort()
        DIMACS_clause.append("0\n")
        self.clause_set.add(" ".join(DIMACS_clause))


    def make_file(self, file_name, indent=0, verbosity=0):
            print_message('Writing file "' + file_name + '" ...', 3, indent = indent, verbosity = verbosity)
            with open(file_name, "w") as output_file:
                output_file.write("p cnf " + str(self.number_of_variables) + " " + str(len(self.clause_set)) + "\n")
                output_file.write("".join(self.clause_set))
            print_message('Done\n', 3, indent = indent, verbosity = verbosity)
