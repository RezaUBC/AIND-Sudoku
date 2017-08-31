""" defining Global Variables """
assignments = []

def assign_value(values, box, value):
    """
    Please use this function to update your values dictionary!
    Assigns a value to a given box. If it updates the board record it.
    """

    # Don't waste memory appending actions that don't actually change any values
    if values[box] == value:
        return values

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
    rows = 'ABCDEFGHI'
    cols = '123456789'
    unitlist,peers = preprocessing(rows,cols,False)
    for un in unitlist:
        # Find all instances of naked twins in a unit
        twin_collection=[]
        for ib in un:
            if len(values[ib]) == 2:
                twin_collection.append(ib)
        twinlistlist=[]
        while len(twin_collection)>0:
            elem = twin_collection.pop()
            for el in twin_collection:
                if values[el]==values[elem]:
                    twinlistlist.append([elem,el])
                    twin_collection.remove(el)
        # Eliminate the naked twins as possibilities for their peers
        for tw in twinlistlist:
            for ib in un:
                if len(values[ib])==1 or ib in tw:
                    continue
                for ch in list(values[tw[0]]):
                    if ch in list(values[ib]):
                        al = list(values[ib])
                        al.remove(ch)
                        values[ib]=''.join(al)
    return values
        

def cross(A, B):
    "Cross product of elements in A and elements in B."
    return ([i+j for i in A for j in B])

def preprocessing(rows, cols, Isdiagonal):
    """initalizing the grid with rows and cols
    Args:
        inputs are row and column names of the grid
        if Isdiagonal is true then we have a diagonal Sudoku
        hence we should include in the contraints in the diagonal
        direction as well.
    Returns:
        units: wich should have boxes with unique boxes in tange 1..9
        peers: all the boxes which share a unit with the given box
        unitlist: list of all the units
    """
    boxes = cross(rows, cols)
    row_units = [cross(r, cols) for r in rows]
    column_units = [cross(rows, c) for c in cols]
    square_units = [cross(rs, cs) for rs in ('ABC','DEF','GHI') for cs in ('123','456','789')]
    unitlist = row_units + column_units + square_units
    
    """ Adding the diagonal Constraints:
        1- We have two more units in diagonal directions
        2- All the peers should be updated as well 
    """
    if (Isdiagonal):
        diag_unit = [[i+j for i,j in zip(list(rows),list(cols))]]
        colslist = list(cols)
        colslist.reverse()
        inv_diag_unit = [[i+j for i,j in zip(list(rows),colslist)]]
        unitlist = unitlist + diag_unit + inv_diag_unit
             
    units = dict((s, [u for u in unitlist if s in u]) for s in boxes)
    peers = dict((s, set(sum(units[s],[]))-set([s])) for s in boxes)
    
    return unitlist,peers
    

def grid_values(grid, Isdiagonal):
    """
    Convert grid into a dict of {square: char} with '123456789' for empties.
    Args:
        grid(string) - A grid in string form.
    Returns:
        A grid in dictionary form
            Keys: The boxes, e.g., 'A1'
            Values: The value in each box, e.g., '8'. If the box has no value, then the value will be '123456789'.
        units: wich should have boxes with unique boxes in tange 1..9
        peers: all the boxes which share a unit with the given box
        unitlist: list of all the units
    """
    rows = 'ABCDEFGHI'
    cols = '123456789'
    unitlist,peers = preprocessing(rows,cols,Isdiagonal)
    sudodic = {}
    num = 0
    for key1 in rows:
        for key2 in cols:
            key = key1+key2
            sudodic[key]=grid[num]
            if sudodic[key] == '.':
                sudodic[key] = cols
            num += 1
            
    return sudodic,unitlist,peers

def display(values):
    """
    Display the values as a 2-D grid.
    Args:
        values(dict): The sudoku in dictionary form
    """
    rows = 'ABCDEFGHI'
    cols = '123456789'
    width = 1+max(len(vals) for _,vals in values.items())
    line = '+'.join(['-'*(width*3)]*3)
    for r in rows:
        print(''.join(values[r+c].center(width)+('|' if c in '36' else '')
                      for c in cols))
        if r in 'CF': print(line)
    return

def eliminate(values,unitlist,peers):
    """Eliminate values from peers of each box with a single value.

    Go through all the boxes, and whenever there is a box with a single value,
    eliminate this value from the set of values of all its peers.

    Args:
        values: Sudoku in dictionary form.
        peers: all the boxes which share a unit with the given box
    Returns:
        Resulting Sudoku in dictionary form after eliminating values.
    """
    for key,val in values.items():
        lval = list(val)
        if len(val)>1:
            continue
        for keyP in peers[key]:
            lvalp = list(values[keyP])
            lvalp = [item for item in lvalp if item not in lval]
            values = assign_value(values,keyP,''.join(lvalp))
            #values[keyP] = ''.join(lvalp)
    return values

def only_choice(values,unitlist,peers):
    """Finalize all values that are the only choice for a unit.

    Go through all the units, and whenever there is a unit with a value
    that only fits in one box, assign the value to this box.

    Input:
        Sudoku in dictionary form.
        unitlist with the list of all the units
    Output: Resulting Sudoku in dictionary form after filling in only choices.
    """
    for un in unitlist:
        cumcullist = []
        for ib in un:
            cumcullist = cumcullist + list(values[ib])
        cumculdic = {num:cumcullist.count(num) for num in cumcullist}
        for chr,cnt in cumculdic.items():
            if cnt == 1:
                for ib in un:
                    if chr in list(values[ib]):
                        values = assign_value(values,ib,chr)
                        #values[ib] = chr
                        break;
    
    return values

def reduce_puzzle(values,unitlist,peers):
    """
    Applying the constraints on the grid
    Args:
        values: the grid
        Isdiagonal: a boolean to activate diagonal sudoku
        peers: all the boxes which share a unit with the given box
        unitlist with the list of all the units
    Return:
        the grid gone through elimination, only_choice, naked_twins
    """
    stalled = False
    while not stalled:
        # Check how many boxes have a determined value
        solved_values_before = len([box for box in values.keys() if len(values[box]) == 1])

        # Use the Eliminate Strategy
        values = eliminate(values,unitlist,peers)
        # Use the Only Choice Strategy
        values = only_choice(values,unitlist,peers)
        # Use naked twins to get rid of twin values
        #values = naked_twins(values)
        # Check how many boxes have a determined value, to compare
        solved_values_after = len([box for box in values.keys() if len(values[box]) == 1])
        # If no new values were added, stop the loop.
        stalled = solved_values_before == solved_values_after
        # Sanity check, return False if there is a box with zero available values:
        if len([box for box in values.keys() if len(values[box]) == 0]):
            return False
    return values
    

def search(values,unitlist,peers):
    """Using depth-first search and propagation, try all possible values.
        Args:
            values: the grid
            Isdiagonal: a boolean to activate diagonal sudoku
            peers: all the boxes which share a unit with the given box
            unitlist with the list of all the units
    Return:
        the grid gone through recursive depth first search
    """
    rows = 'ABCDEFGHI'
    cols = '123456789'
    boxes = cross(rows, cols)
    # First, reduce the puzzle using the previous function
    values = reduce_puzzle(values,unitlist,peers)
    if values is False:
        return False ## Failed earlier
    if all(len(values[s]) == 1 for s in boxes): 
        return values ## Solved!
    # Choose one of the unfilled squares with the fewest possibilities
    n,s = min((len(values[s]), s) for s in boxes if len(values[s]) > 1)
    # Now use recurrence to solve each one of the resulting sudokus, and 
    for value in values[s]:
        new_sudoku = values.copy()
        new_sudoku[s] = value
        attempt = search(new_sudoku,unitlist,peers)
        if attempt:
            return attempt

def solve(grid, Isdiagonal = True):
    """
    Find the solution to a Sudoku grid.
    Args:
        grid(string): a string representing a sudoku grid.
            Example: '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    Returns:
        The dictionary representation of the final sudoku grid. False if no solution exists.
    """
    sudodic,unitlist,peers= grid_values(grid, Isdiagonal)
    return search(sudodic,unitlist,peers)
    

if __name__ == '__main__':
    diag_sudoku_grid = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    display(solve(diag_sudoku_grid, True))

    try:
        from visualize import visualize_assignments
        visualize_assignments(assignments)

    except SystemExit:
        pass
    except:
        print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')
