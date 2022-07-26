import re
from src.literal_manipulation import variable_from_literal
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
    (-1, -1, -1, -1, -1, -1, -1, -1): "1c",
    (-1, 1, -1, -1, -1, -1, -1, -1): "1c",
    (1, -1, -1, -1, -1, -1, -1, -1): "1e",
    (-1, 1, -1, 1, -1, -1, -1, -1): "2c",
    (1, -1, 1, -1, -1, -1, -1, -1): "2e",
    (1, -1, -1, 1, -1, -1, -1, -1): "2k",
    (1, 1, -1, -1, -1, -1, -1, -1): "2a",
    (1, -1, -1, -1, 1, -1, -1, -1): "2i",
    (-1, 1, -1, -1, -1, 1, -1, -1): "2n",
    (-1, 1, -1, 1, -1, 1, -1, -1): "3c",
    (1, -1, 1, -1, 1, -1, -1, -1): "3e",
    (1, -1, 1, -1, -1, 1, -1, -1): "3k",
    (1, 1, 1, -1, -1, -1, -1, -1): "3a",
    (1, 1, -1, -1, -1, -1, -1, 1): "3i",
    (1, 1, -1, 1, -1, -1, -1, -1): "3n",
    (1, -1, -1, 1, -1, 1, -1, -1): "3y",
    (1, 1, -1, -1, -1, 1, -1, -1): "3q",
    (1, 1, -1, -1, -1, -1, 1, -1): "3j",
    (1, 1, -1, -1, 1, -1, -1, -1): "3r",
    (-1, 1, -1, 1, -1, 1, -1, 1): "4c",
    (1, -1, 1, -1, 1, -1, 1, -1): "4e",
    (1, 1, -1, 1, -1, -1, 1, -1): "4k",
    (1, 1, 1, 1, -1, -1, -1, -1): "4a",
    (1, 1, -1, 1, 1, -1, -1, -1): "4i",
    (1, 1, -1, 1, -1, -1, -1, 1): "4n",
    (1, 1, -1, 1, -1, 1, -1, -1): "4y",
    (1, 1, 1, -1, -1, 1, -1, -1): "4q",
    (1, 1, -1, -1, 1, -1, 1, -1): "4j",
    (1, 1, 1, -1, 1, -1, -1, -1): "4r",
    (1, 1, -1, -1, 1, -1, -1, 1): "4t",
    (1, 1, -1, -1, -1, 1, 1, -1): "4w",
    (1, 1, -1, -1, 1, 1, -1, -1): "4z",
    (1, 1, 1, -1, 1, -1, 1, -1): "5c",
    (1, 1, -1, 1, -1, 1, -1, 1): "5e",
    (1, 1, -1, 1, -1, 1, 1, -1): "5k",
    (1, 1, 1, 1, -1, -1, -1, 1): "5a",
    (1, 1, 1, 1, 1, -1, -1, -1): "5i",
    (1, 1, 1, 1, -1, -1, 1, -1): "5n",
    (1, 1, -1, 1, 1, -1, 1, -1): "5y",
    (1, 1, 1, -1, 1, 1, -1, -1): "5q",
    (1, 1, 1, 1, -1, 1, -1, -1): "5j",
    (1, 1, -1, 1, 1, 1, -1, -1): "5r",
    (1, 1, 1, 1, 1, -1, 1, -1): "6c",
    (1, 1, 1, 1, -1, 1, -1, 1): "6e",
    (1, 1, 1, 1, -1, 1, 1, -1): "6k",
    (1, 1, 1, 1, 1, 1, -1, -1): "6a",
    (1, 1, -1, 1, 1, 1, -1, 1): "6i",
    (1, 1, 1, -1, 1, 1, 1, -1): "6n",
    (1, 1, 1, 1, 1, 1, 1, -1): "7c",
    (1, 1, 1, 1, 1, 1, -1, 1): "7e",
    (1, 1, 1, 1, 1, 1, 1, 1): "8c"
}


def rule_from_rulestring(rulestring, number_of_variables):
    rule = {}

    original_rulestring = rulestring

    partial_flag = False

    if rulestring[0] in ["p", "P"]:
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
                        rule[BS_letter + number_of_neighbours + character] = 1
                elif transition[1] == "-":
                    banned_characters = transition[2:]
                    assert all(character in possible_transitions[number_of_neighbours] for character in
                               banned_characters), "Unrecognized character"
                    for character in possible_transitions[number_of_neighbours]:
                        if character in banned_characters:
                            rule[BS_letter + number_of_neighbours + character] = -1
                        else:
                            rule[BS_letter + number_of_neighbours + character] = 1
                else:
                    characters = transition[1:]
                    assert all(character in possible_transitions[number_of_neighbours] for character in
                               characters), "Unrecognized character"
                    for character in possible_transitions[number_of_neighbours]:
                        if character in characters:
                            rule[BS_letter + number_of_neighbours + character] = 1
                        else:
                            rule[BS_letter + number_of_neighbours + character] = -1
            else:
                if len(transition) == 1:
                    for character in possible_transitions[number_of_neighbours]:
                        number_of_variables += 1
                        rule[BS_letter + number_of_neighbours + character] = number_of_variables
                else:
                    characters = transition[1:]
                    if "-" in characters:
                        characters, banned_characters = re.split("-", characters)
                    else:
                        banned_characters = ""

                    for character in possible_transitions[number_of_neighbours]:
                        if character in characters:
                            rule[BS_letter + number_of_neighbours + character] = 1
                        elif character in banned_characters:
                            rule[BS_letter + number_of_neighbours + character] = -1
                        else:
                            number_of_variables += 1
                            rule[BS_letter + number_of_neighbours + character] = number_of_variables

        for number_of_neighbours in "012345678":
            if BS_letter + number_of_neighbours + "c" not in rule:
                for character in possible_transitions[number_of_neighbours]:
                    rule[BS_letter + number_of_neighbours + character] = -1

    new_rulestring = rulestring_from_rule(rule)
    if original_rulestring != new_rulestring:
        log("Rulestring parsed as: " + new_rulestring)

    return rule, number_of_variables


def rulestring_from_rule(rule):
    variables = [variable_from_literal(value)[0] for value in rule.values() if value not in [-1, 1]]

    if len(variables) != len(set(variables)):
        return "{" + ", ".join(
            ("'" + transition + "': '" + str(literal) + "'") for transition, literal in sorted(rule.items())) + "}"
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
                number_of_transitions = sum((rule[BS_letter + number_of_neighbours + character] == 1)
                                            for character in possible_transitions[number_of_neighbours])
                if number_of_transitions == possible_number_of_transitions:
                    rulestring += number_of_neighbours
                elif 0 < number_of_transitions <= possible_number_of_transitions / 2:
                    rulestring += number_of_neighbours
                    for character in possible_transitions[number_of_neighbours]:
                        if rule[BS_letter + number_of_neighbours + character] == 1:
                            rulestring += character
                elif number_of_transitions != 0:
                    rulestring += number_of_neighbours
                    rulestring += "-"
                    for character in possible_transitions[number_of_neighbours]:
                        if rule[BS_letter + number_of_neighbours + character] == -1:
                            rulestring += character
            else:
                characters = ""
                banned_characters = ""
                for character in possible_transitions[number_of_neighbours]:
                    literal = rule[BS_letter + number_of_neighbours + character]
                    if literal == -1:
                        banned_characters += character
                    elif literal == 1:
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


def transition_from_cells(neighbours):
    return transition_lookup[sort_neighbours(neighbours)]


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
