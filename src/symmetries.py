import re

groups = {
    "C1": {'group': ['ro0'], 'generators': []},
    "C2": {'group': ['ro0', "ro2"], 'generators': ["ro2"]},
    "C4": {'group': ['ro0', "ro1", 'ro2', "ro3"], 'generators': ["ro1"]},
    "D2-": {'group': ['ro0', "re-"], 'generators': ["re-"]},
    "D2\\": {'group': ['ro0', "re\\"], 'generators': ["re\\"]},
    "D2|": {'group': ['ro0', "re|"], 'generators': ["re|"]},
    "D2/": {'group': ['ro0', "re/"], 'generators': ["re/"]},
    "D4+": {'group': ['ro0', "re-", "re|", "ro2"], 'generators': ["re-", "re|"]},
    "D4X": {'group': ['ro0', "re/", "re\\", "ro2"], 'generators': ["re/", "re\\"]},
    "D8": {'group': ['ro0', "ro1", 'ro2', "ro3", "re-", "re|", "re/", "re\\"], 'generators': ["re-", "re\\"]}
}

matrices = {
    'ro0': (( 1, 0),
            ( 0, 1)),
    "ro1": (( 0,-1),
            ( 1, 0)),
    'ro2': ((-1, 0),
            ( 0,-1)),
    "ro3": (( 0, 1),
            (-1, 0)),
    "re-": (( 1, 0),
            ( 0,-1)),
    "re|": ((-1, 0),
            ( 0, 1)),
    "re/": (( 0,-1),
            (-1, 0)),
    "re\\":(( 0, 1),
            ( 1, 0))
}

def matmul(matrix0, matrix1):
    width0 = len(matrix0[0])
    assert all(len(row) == width0 for row in matrix0), 'matrix0 not rectangular'
    width1 = len(matrix1[0])
    assert all(len(row) == width1 for row in matrix1), 'matrix1 not rectangular'
    assert width0 == len(matrix1), 'matrices not multipliable'
    return tuple(tuple(sum(row[i]*matrix1[i][j] for i in range(width0)) for j in range(width1)) for row in matrix0)

def parse_transformation(arguments):
    transformation = {
        'matrix': (( 1, 0),
                   ( 0, 1)),
        'x': 0,
        'y': 0,
        't': 0
    }
    for argument in arguments:
        letters, value = re.match('(\A[a-z]*)([^a-z]*\Z)', argument.lower()).groups()
        if letters == 'ro':
            value = str(int(value)%4)
        if letters == 'p':
            letters = 't'

        if letters in ['re','ro']:
            transformation['matrix'] = matmul(matrices[letters+value], transformation['matrix'])
            transformation['x'], transformation['y'], _ = apply_transformation(new_transformation(matrices[letters+value]), transformation['x'], transformation['y'], 0)
        else:
            transformation[letters] += int(value)
    return transformation

def apply_transformation(transformation, x_0, y_0, t_0):
    ((x_1,), (y_1,)) = matmul(transformation['matrix'], ((x_0,), (y_0,)))
    return x_1 + transformation['x'], y_1 + transformation['y'], t_0 + transformation['t']

def new_transformation(matrix=(( 1, 0),( 0, 1)),x=0,y=0,t=0):
    return {
        'matrix': matrix,
        'x': x,
        'y': y,
        't': t
    }

def invert_transformation(transformation):
    inverse_matrix = tuple(zip(*transformation['matrix'])) # Transpose since these are unitary
    ((x_1,), (y_1,)) = matmul(inverse_matrix, ((transformation['x'],), (transformation['y'],)))
    return new_transformation(inverse_matrix,-x_1, -y_1, -transformation['t'])

def transformations_from_group(group, width, height):
    transformations = []
    for generator in groups[group]['generators']:
        matrix = matrices[generator]
        # Far corner
        x_0 = width - 1
        y_0 = height - 1
        x_1, y_1, _ = apply_transformation(new_transformation(matrix), x_0, y_0, 0)
        assert (x_0-x_1)%2 == 0 and (y_0-y_1)%2 == 0, 'Incompatibility between symmetry and parities of height and width'
        transformations.append(new_transformation(matrix, (x_0-x_1)//2, (y_0-y_1)//2)) # Fixes midpoint of grid
    return transformations

