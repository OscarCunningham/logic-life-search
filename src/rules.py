import re
import ast
from src.literal_manipulation import variable_from_literal, standard_form_literal
from src.logging import log

possible_transitions = {"0": sorted("c"),
                        "1": sorted("ce"),
                        "2": sorted("cekain"),
                        "3": sorted("cekainyqjr"),
                        "4": sorted("cekainyqjrtwz"),
                        "5": sorted("cekainyqjr"),
                        "6": sorted("cekain"),
                        "7": sorted("ce"),
                        "8": sorted("c")}

transition_lookup = {
    "00000000": "0c",
    "01000000": "1c",
    "10000000": "1e",
    "01010000": "2c",
    "10100000": "2e",
    "10010000": "2k",
    "11000000": "2a",
    "10001000": "2i",
    "01000100": "2n",
    "01010100": "3c",
    "10101000": "3e",
    "10100100": "3k",
    "11100000": "3a",
    "11000001": "3i",
    "11010000": "3n",
    "10010100": "3y",
    "11000100": "3q",
    "11000010": "3j",
    "11001000": "3r",
    "01010101": "4c",
    "10101010": "4e",
    "11010010": "4k",
    "11110000": "4a",
    "11011000": "4i",
    "11010001": "4n",
    "11010100": "4y",
    "11100100": "4q",
    "11001010": "4j",
    "11101000": "4r",
    "11001001": "4t",
    "11000110": "4w",
    "11001100": "4z",
    "11101010": "5c",
    "11010101": "5e",
    "11010110": "5k",
    "11110001": "5a",
    "11111000": "5i",
    "11110010": "5n",
    "11011010": "5y",
    "11101100": "5q",
    "11110100": "5j",
    "11011100": "5r",
    "11111010": "6c",
    "11110101": "6e",
    "11110110": "6k",
    "11111100": "6a",
    "11011101": "6i",
    "11101110": "6n",
    "11111110": "7c",
    "11111101": "7e",
    "11111111": "8c"}


def rule_from_rulestring(rulestring):
    if rulestring is None:
        return None
    else:

        rule = {}

        rulestring = rulestring.strip()
        original_rulestring = rulestring

        partial_flag = False

        if rulestring[0] == "{":
            rule_unsanitized = ast.literal_eval(rulestring)
            for BS_letter in "BS":
                for number_of_neighbours in "012345678":
                    for character in possible_transitions[number_of_neighbours]:
                        literal = standard_form_literal(
                            str(rule_unsanitized[BS_letter + number_of_neighbours + character]))
                        assert literal[-1] not in ['\xe2\x80\x99', "'"], "Can't ignore transition in rule"
                        rule[BS_letter + number_of_neighbours + character] = literal
            return rule
        elif rulestring[0] in ["p", "P"]:
            partial_flag = True
            if len(rulestring) == 1:
                rulestring = "B012345678/S012345678"
            else:
                rulestring = rulestring[1:]

        rulestring = re.sub(' ', '', rulestring.upper())

        rulestrings = re.split("/", rulestring)

        if len(rulestrings) == 1:
            assert "B" in rulestring or "S" in rulestring, 'Rule sting not recognised (no "B" or "S")'
            b_position = rulestring.find("B")
            s_position = rulestring.find("S")
            rulestring = rulestring.strip("BS")
            rulestrings = re.split("[BS]*", rulestring)
            assert len(rulestrings) < 3, "Rule sting not recognised"
            if b_position > s_position:
                birth_string = rulestrings[1] if len(rulestrings) == 2 else ""
                survival_string = rulestrings[0]
            else:
                birth_string = rulestrings[0]
                survival_string = rulestrings[1] if len(rulestrings) == 2 else ""
        else:
            assert len(rulestrings) == 2, 'Rule sting not recognised (too many "/"s)'
            if "S" in rulestrings[0] or "B" in rulestrings[1]:
                birth_string = rulestrings[1]
                survival_string = rulestrings[0]
            else:
                birth_string = rulestrings[0]
                survival_string = rulestrings[1]

        assert "S" not in birth_string and "B" not in survival_string, "Rule sting not recognised"

        birth_string = re.sub('B', '', birth_string).lower()
        survival_string = re.sub('S', '', survival_string).lower()

        assert (birth_string == "" or birth_string[0] in "012345678") and (
                    survival_string == "" or survival_string[0] in "012345678"), "Rule sting not recognised"

        if partial_flag:
            variable_number = 0

        for BS_letter, rulestring in zip(["B", "S"], [birth_string, survival_string]):
            transitions = []
            previous_number = 0

            if rulestring != "":
                for position in range(1, len(rulestring)):
                    if rulestring[position] in "012345678":
                        transitions.append(rulestring[previous_number:position])
                        previous_number = position
                transitions.append(rulestring[previous_number:])

            for transition in transitions:
                number_of_neighbours = transition[0]
                if not partial_flag:
                    if len(transition) == 1:
                        for character in possible_transitions[number_of_neighbours]:
                            rule[BS_letter + number_of_neighbours + character] = "1"
                    elif transition[1] == "-":
                        banned_characters = transition[2:]
                        assert all(character in possible_transitions[number_of_neighbours] for character in
                                   banned_characters), "Unrecognized character"
                        for character in possible_transitions[number_of_neighbours]:
                            if character in banned_characters:
                                rule[BS_letter + number_of_neighbours + character] = "0"
                            else:
                                rule[BS_letter + number_of_neighbours + character] = "1"
                    else:
                        characters = transition[1:]
                        assert all(character in possible_transitions[number_of_neighbours] for character in
                                   characters), "Unrecognized character"
                        for character in possible_transitions[number_of_neighbours]:
                            if character in characters:
                                rule[BS_letter + number_of_neighbours + character] = "1"
                            else:
                                rule[BS_letter + number_of_neighbours + character] = "0"
                else:
                    if len(transition) == 1:
                        for character in possible_transitions[number_of_neighbours]:
                            rule[BS_letter + number_of_neighbours + character] = "rule_variable_" + str(variable_number)
                            variable_number += 1
                    else:
                        characters = transition[1:]
                        if "-" in characters:
                            characters, banned_characters = re.split("-", characters)
                        else:
                            banned_characters = ""

                        for character in possible_transitions[number_of_neighbours]:
                            if character in characters:
                                rule[BS_letter + number_of_neighbours + character] = "1"
                            elif character in banned_characters:
                                rule[BS_letter + number_of_neighbours + character] = "0"
                            else:
                                rule[BS_letter + number_of_neighbours + character] = "rule_variable_" + str(
                                    variable_number)
                                variable_number += 1

            for number_of_neighbours in "012345678":
                if BS_letter + number_of_neighbours + "c" not in rule:
                    for character in possible_transitions[number_of_neighbours]:
                        rule[BS_letter + number_of_neighbours + character] = "0"

        new_rulestring = rulestring_from_rule(rule)
        if original_rulestring != new_rulestring:
            log("Rulestring parsed as: " + new_rulestring)

        return rule


def rulestring_from_rule(rule):
    variables = [variable_from_literal(value)[0] for value in rule.values() if value not in ["0", "1"]]

    if len(variables) != len(set(variables)):
        return "{" + ", ".join(
            ("'" + transition + "': '" + literal + "'") for transition, literal in sorted(rule.items())) + "}"
    elif len(variables) == 0:
        partial_flag = False
    else:
        partial_flag = True

    rulestring = ""
    if partial_flag:
        rulestring += "p"

    for BS_letter in ["B", "S"]:
        rulestring += BS_letter
        for number_of_neighbours in "012345678":
            if not partial_flag:
                possible_number_of_transitions = len(possible_transitions[number_of_neighbours])
                number_of_transitions = sum((rule[BS_letter + number_of_neighbours + character] == "1")
                                            for character in possible_transitions[number_of_neighbours])
                if number_of_transitions == possible_number_of_transitions:
                    rulestring += number_of_neighbours
                elif 0 < number_of_transitions <= possible_number_of_transitions / 2:
                    rulestring += number_of_neighbours
                    for character in possible_transitions[number_of_neighbours]:
                        if rule[BS_letter + number_of_neighbours + character] == "1":
                            rulestring += character
                elif number_of_transitions != 0:
                    rulestring += number_of_neighbours
                    rulestring += "-"
                    for character in possible_transitions[number_of_neighbours]:
                        if rule[BS_letter + number_of_neighbours + character] == "0":
                            rulestring += character
            else:
                characters = ""
                banned_characters = ""
                for character in possible_transitions[number_of_neighbours]:
                    literal = rule[BS_letter + number_of_neighbours + character]
                    if literal == "0":
                        banned_characters += character
                    elif literal == "1":
                        characters += character
                if characters == "" and banned_characters == "":
                    rulestring += number_of_neighbours
                elif len(banned_characters) < len(possible_transitions[number_of_neighbours]):
                    rulestring += number_of_neighbours
                    rulestring += characters
                    if len(banned_characters) > 0:
                        rulestring += "-"
                        rulestring += banned_characters

        if BS_letter == "B":
            rulestring += "/"

    return rulestring


def transition_from_cells(cell_0,
                          cell_1=None,
                          cell_2=None,
                          cell_3=None,
                          cell_4=None,
                          cell_5=None,
                          cell_6=None,
                          cell_7=None):
    if cell_1 is None:
        assert len(cell_0) == 8, "Wrong number of cells"
        cells = cell_0
    else:
        cells = [cell_0, cell_1, cell_2, cell_3, cell_4, cell_5, cell_6, cell_7]

    if all(isinstance(cell, bool) for cell in cells):
        cells = ["1" if cell else "0" for cell in cells]

    cell_string = "".join(sort_neighbours(cells))

    return transition_lookup[cell_string]


def sort_neighbours(neighbours):
    return max((neighbours[0], neighbours[1], neighbours[2], neighbours[3], neighbours[4], neighbours[5], neighbours[6],
                neighbours[7]),
               (neighbours[6], neighbours[7], neighbours[0], neighbours[1], neighbours[2], neighbours[3], neighbours[4],
                neighbours[5]),
               (neighbours[4], neighbours[5], neighbours[6], neighbours[7], neighbours[0], neighbours[1], neighbours[2],
                neighbours[3]),
               (neighbours[2], neighbours[3], neighbours[4], neighbours[5], neighbours[6], neighbours[7], neighbours[0],
                neighbours[1]),
               (neighbours[6], neighbours[5], neighbours[4], neighbours[3], neighbours[2], neighbours[1], neighbours[0],
                neighbours[7]),
               (neighbours[0], neighbours[7], neighbours[6], neighbours[5], neighbours[4], neighbours[3], neighbours[2],
                neighbours[1]),
               (neighbours[2], neighbours[1], neighbours[0], neighbours[7], neighbours[6], neighbours[5], neighbours[4],
                neighbours[3]),
               (neighbours[4], neighbours[3], neighbours[2], neighbours[1], neighbours[0], neighbours[7], neighbours[6],
                neighbours[5]))
