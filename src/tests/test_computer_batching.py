import pandas as pd
import numpy as np
from utility import computers_batched


def test_computerss_batched_last_batch_is_atleast_two():
    """
    Test that when batching computers the last batch has
    atleast two entries. F.ex [0, 1, ..., 13], [14, 15]
    """
    max_items = 15 + 1
    computers = list(range(max_items))
    df = pd.DataFrame(computers)
    first = df[0:14]
    second = df[14:16]
    expected_batches = [first, second]
    result_batches = computers_batched(df)
    for expected, result in zip(expected_batches, result_batches):
        assert expected.equals(result)


def test_computers_batched_small_batch_is_not_padded():
    max_items = 12
    computers = list(range(max_items))
    df = pd.DataFrame(computers)
    expected_batches = [df[0:max_items]]
    result_batches = computers_batched(df)
    for expected, result in zip(expected_batches, result_batches):
        assert expected.equals(result)
    assert len(result_batches) == 1
