import pytest
from computer import computers_batched


def test_batching_single_entry_raises_value_error():
    entries = ["hi"]
    with pytest.raises(ValueError):
        computers_batched(entries)


def test_computers_batched_less_than_15_entries_is_not_padded():
    n_items = 12
    entries = [f"comp:{i}" for i in range(n_items)]
    result = computers_batched(entries)
    assert len(result) == 1
    assert entries == result[0]


def test_computers_batched_16_entries_ensures_that_last_has_two_entries():
    n_items = 16
    entries = [f"comp:{i}" for i in range(n_items)]
    expected_batches = [entries[:14], entries[14:]]
    result_batches = computers_batched(entries)
    for expected, result in zip(expected_batches, result_batches):
        assert expected == result


def test_computers_batched_15_entries_is_valid():
    n_items = 15
    entries = [f"comp:{i}" for i in range(n_items)]
    result_batches = computers_batched(entries)
    assert len(result_batches) == 1
    assert entries == result_batches[0]
