assignments = []

ROWS = 'ABCDEFGHI'
COLS = '123456789'


def cross(A, B):
    """
    Cross product of elements in A and elements in B.
    """
    return [x + y for x in A for y in B]


def join(A, B):
    """
    Zip with concatenation
    """
    return list(map("".join, zip(A, B)))


BOXES = cross(ROWS, COLS)
ROW_UNITS = [cross(r, COLS) for r in ROWS]
COLUMN_UNITS = [cross(ROWS, c) for c in COLS]
SQUARE_UNITS = [cross(rs, cs) for rs in ('ABC', 'DEF', 'GHI') for cs in ('123', '456', '789')]
DIAGONAL_UNITS = [join(ROWS, COLS), join(ROWS, COLS[::-1])]
UNITLIST = ROW_UNITS + COLUMN_UNITS + SQUARE_UNITS + DIAGONAL_UNITS
UNITS = dict((s, [u for u in UNITLIST if s in u]) for s in BOXES)
PEERS = dict((s, set(sum(UNITS[s], [])) - {s}) for s in BOXES)


def assign_value(values, box, value):
    """
    Please use this function to update your values dictionary!
    Assigns a value to a given box. If it updates the board record it.
    """
    values[box] = value
    if len(value) == 1:
        assignments.append(values.copy())
    return values


def naked_twins(values):
    """Eliminate values using the naked twins strategy.
    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}

    Returns:
        the values dictionary with the naked twins eliminated from peers.
    """
    # Getting elements that has 2 possible digits
    twins = filter(lambda v: len(v[1]) == 2, values.items())
    for twin in twins:
        pair = twin[1]
        units = UNITS[twin[0]]
        # For each unit of this element - check if there is a same pair
        for unit in units:
            if list(map(values.get, unit)).count(pair) > 1:
                # Is there is a pair then we can remove digits of this pair from this unit's possibilities
                for num in pair:
                    # Iterate over elements that have digits from naked pair and remove them
                    for peer in filter(lambda x: num in values[x] and len(values[x]) > 1 and values[x] != pair, unit):
                        assign_value(values, peer, values[peer].replace(num, ''))
    return values


def grid_values(grid):
    """
    Convert grid into a dict of {square: char} with '123456789' for empties.
    Args:
        grid(string) - A grid in string form.
    Returns:
        A grid in dictionary form
            Keys: The boxes, e.g., 'A1'
            Values: The value in each box, e.g., '8'. If the box has no value, then the value will be '123456789'.
    """
    grid_dict = dict(zip(BOXES, grid))
    return {k: "".join(COLS if v == '.' else v) for k, v in grid_dict.items()}


def display(values):
    """
    Display the values as a 2-D grid.
    Args:
        values(dict): The sudoku in dictionary form
    """
    width = 1 + max(len(values[s]) for s in BOXES)
    line = '+'.join(['-' * (width * 3)] * 3)
    for r in ROWS:
        print(''.join(values[r + c].center(width) + ('|' if c in '36' else '') for c in COLS))
        if r in 'CF':
            print(line)

def eliminate(values):
    """
    For every found solution - eliminate this values from all peer's values
    """
    for k in values.keys():
        if len(values[k]) == 1:
            for k2 in PEERS[k]:
                v2 = values[k2]
                assign_value(values, k2, v2.replace(values[k], ''))
    return values


def only_choice(values):
    """
    For every unit check if there is single value that could
    be propagated as solution
    """
    new_values = values.copy()
    for unit in UNITLIST:
        for n in range(1, 10):
            res = [(x, str(n)) for x in unit if str(n) in str(values[x])]
            if len(res) == 1:
                assign_value(new_values, res[0][0], res[0][1])
    return new_values


def reduce_puzzle(values):
    """
    Trying to solve puzzle given state and using strategies
    implemented above, solution could stall or not exist at all

    This function is used by search
    """
    stalled = False
    while not stalled:
        # Check how many boxes have a determined value
        solved_values_before = len([box for box in values.keys() if len(values[box]) == 1])

        # Use the Eliminate Strategy
        values = eliminate(values)

        # Use the Naked Twin Strategy
        values = naked_twins(values)

        # Use the Only Choice Strategy
        values = only_choice(values)

        # Check how many boxes have a determined value, to compare
        solved_values_after = len([box for box in values.keys() if len(values[box]) == 1])
        # If no new values were added, stop the loop.
        stalled = solved_values_before == solved_values_after
        # Sanity check, return False if there is a box with zero available values:
        if len([box for box in values.keys() if len(values[box]) == 0]):
            return False

    return values


def search(values):
    """
    Recursively check all possible combinations of some optimal position
    in case current puzzle cannot be solved only using constraint propagation
    strategies
    """
    # Try to find solution using constraint propagation
    values = reduce_puzzle(values)

    # Solution doesn't exist - exit
    if values is False:
        return False

    # Solution was found
    if all(map(lambda x: len(x) == 1, values.values())):
        return values

    # Choose one of the unfilled squares with the fewest possibilities
    candidate = min(filter(lambda f: len(f[1]) > 1, values.items()), key=lambda x: len(x[1]))

    # Choose one of the possible values for candidate and try to solve this
    # sub-task recursively
    for i in values[candidate[0]]:
        values_copy = values.copy()
        values_copy[candidate[0]] = i
        result = search(values_copy)
        # If solution was found - interrupt current loop and exit
        if result:
            return result

    # If there is no solution - return false
    return False


def solve(grid):
    """
    Find the solution to a Sudoku grid.
    Args:
        grid(string): a string representing a sudoku grid.
            Example: '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    Returns:
        The dictionary representation of the final sudoku grid. False if no solution exists.
    """
    return search(grid_values(grid))


if __name__ == '__main__':
    diag_sudoku_grid = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    display(solve(diag_sudoku_grid))

    try:
        from visualize import visualize_assignments

        visualize_assignments(assignments)

    except SystemExit:
        pass
    except:
        print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')
