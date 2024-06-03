

def computers_batched(computers):
    """
    Creates batches of computers.
    Guarantees that the last batch is atleast two computers, such
    that hp warranty lookup of a batch is possible.
    """
    max_items = 15
    n_items = len(computers)
    if n_items < 2:
        raise ValueError("A minimum of two computers is required.")
    slizes = [[i, i + max_items] for i in range(0, n_items, max_items)]
    if n_items % max_items == 1:
        last_slize = slizes[-1]
        second_last = slizes[-2]
        second_last[1] -= 1
        last_slize[0] -= 1
    computer_batches = [computers[start:stop] for start, stop in slizes]
    return computer_batches


def write_results(fname, computers, file_create):
    """
    Write results from warranty lookup to file.
    Will create a truncated file if append is false.
    """
    if file_create:
        computers.to_csv(fname, header=False, index=False, mode="a")
    else:
        computers.to_csv(fname, index=False)
