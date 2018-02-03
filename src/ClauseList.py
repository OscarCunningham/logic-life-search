from LLS_messages import print_message
from LLS_literal_manipulation import negate, variable_from_literal

class ClauseList:


    def __init__(self):
        self.clause_list = []
        self.number_of_variables = 0
        self.number_of_clauses = 0
        self.DIMACS_literal_from_variable = {}


    def __eq__(self, other):
        if other == None:
            return False
        else:
            return (self.clause_list == other.clause_list and self.number_of_variables == other.number_of_variables and self.number_of_clauses == other.number_of_clauses and self.DIMACS_literal_from_variable == other.DIMACS_literal_from_variable)


    def __ne__(self, other):
        return not __eq__(self, other)


    def prepare_clause(self, clause):
        DIMACS_clause = []
        for literal_number, literal in enumerate(clause):
            if literal == "0":
                pass
            elif literal == "1":
                return ""
            else:
                (variable, negated) = variable_from_literal(literal)

                # If we haven't seen it before then add it to the dictionary
                if not self.DIMACS_literal_from_variable.has_key(variable):
                    self.DIMACS_literal_from_variable[variable] = str(self.number_of_variables + 1)
                    self.number_of_variables += 1

                DIMACS_clause.append(negate(self.DIMACS_literal_from_variable[variable], negated, DIMACS = True))
        self.number_of_clauses +=1
        DIMACS_clause.append("0\n")
        return " ".join(DIMACS_clause)


    def append(self, clause):
        self.clause_list.append(self.prepare_clause(clause))


    def extend(self, clauses):
        self.clause_list += (self.prepare_clause(clause) for clause in clauses)


    def make_file(self, file_name, indent=0, verbosity=0):
            print_message('Writing file "' + file_name + '" ...', 3, indent = indent, verbosity = verbosity)
            with open(file_name, "w") as output_file:
                output_file.write("p cnf " + str(self.number_of_variables) + " " + str(self.number_of_clauses) + "\n")
                output_file.write("".join(self.clause_list))
            print_message('Done\n', 3, indent = indent, verbosity = verbosity)
