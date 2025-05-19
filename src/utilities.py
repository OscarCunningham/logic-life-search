import re
import copy


def format_carriage_returns(input_string):
    # Convert any newline format (\r, \n, \n\r, \r\n) to just \n
    if '\r' in input_string and '\n' not in input_string:
        return re.sub('\r', '\n', input_string)
    else:
        return re.sub('\r', '', input_string)


def make_grid(default_cell, *dimensions, template=None):
    if template is not None:
        assert not dimensions, 'Two sets of parameters given to make_grid'
        dimensions = []
        while isinstance(template, list):
            dimensions.insert(0,len(template))
            if template:
                template = template[0]
            else:
                break

    grid = default_cell
    for dimension in dimensions:
        grid = [copy.deepcopy(grid) for _ in range(dimension)]
    return grid


def make_layers(width, height, layer_shape, center):
    """Returns a list of layers used for some constraints. Each layer is a list of grid coordinates."""
    layer_shape = layer_shape.lower()
    layers = []
    for x in range(width):
        for y in range(height):
            if layer_shape == "column" or layer_shape == "columns" or layer_shape == "vertical":
                layer_number = x
            elif layer_shape == "row" or layer_shape == "rows" or layer_shape == "horizontal":
                layer_number = y
            elif layer_shape == "diagonal" or layer_shape == "diagonals":
                layer_number = x + y
            elif layer_shape == "back_diagonal" or layer_shape == "back_diagonals" or layer_shape == "back-diagonal" or layer_shape == "back-diagonals":
                layer_number = x - y + height - 1
            elif layer_shape == "box" or layer_shape == "boxes":
                layer_number = max(abs(x - center[0]), abs(y - center[1]))
            elif layer_shape == "diamond" or layer_shape == "diamonds":
                layer_number = abs(x - center[0]) + abs(y - center[1])
            elif layer_shape == "circle" or layer_shape == "circles":
                layer_number = round(((x - center[0]) ** 2 + (y - center[1]) ** 2) ** 0.5)
            else:
                raise ValueError("Invalid layer shape.")
            if layer_number >= len(layers):
                layers.extend([] for _ in range(layer_number - len(layers) + 1))
            layers[layer_number].append([x,y])
    return layers
