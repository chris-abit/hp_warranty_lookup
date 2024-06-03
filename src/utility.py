

def computers_batched(computers):
    max_items = 15
    n_items = len(computers)
    slizes = [[i, i + max_items] for i in range(0, n_items, max_items)]
    print(f"{slizes=}")
    if n_items % max_items < 2:
        last_slize = slizes[-1]
        second_last = slizes[-2]
        second_last[1] -= 1
        last_slize[0] -= 1
    print(f"{slizes=}")
    computer_batches = [computers[start:stop] for start, stop in slizes]
    return computer_batches
