import pytest
import pandas as pd
import numpy as np
from computer import Computer, computers_read


@pytest.fixture
def tmp_computers(tmp_path):
    def _tmp_computers(serial_numbers, product_numbers):
        columns = ["serial_number", "product_number"]
        computers = {
            columns[0] : serial_numbers,
            columns[1] : product_numbers,
        }
        df = pd.DataFrame(computers)
        fname = "hp_products.csv"
        fpath = tmp_path / fname
        df.to_csv(fpath, index=False)
        return fpath
    return _tmp_computers


def test_computers_read_returns_a_list_of_computers(tmp_computers):
    sns = ["aba", "caba"]
    pns = ["123E4", "456E6"]
    computers = [Computer(s, p) for s, p in zip(sns, pns)]
    fpath = tmp_computers(sns, pns)
    results = computers_read(fpath)
    for expected, result in zip(computers, results):
        assert expected.serial_number == result.serial_number
        assert expected.product_number == result.product_number
    assert len(computers) == len(results)


def test_computers_read_fills_missing_product_numbers_with_empty_string(tmp_computers):
    sns = ["aba"]
    pns = [""]
    computers = [Computer(s, p) for s, p in zip(sns, pns)]
    fpath = tmp_computers(sns, pns)
    results = computers_read(fpath)
    computer = results[0]
    assert not pd.isna(computer.product_number)
    assert computer.serial_number == sns[0]
    assert computer.product_number == pns[0]


def test_computers_read_ignores_missing_serial_number(tmp_computers):
    sns = ["", "caba"]
    pns = ["123E4", "456E6"]
    computers = [Computer(sns[1], pns[1])]
    fpath = tmp_computers(sns, pns)
    results = computers_read(fpath)
    for expected, result in zip(computers, results):
        assert expected.serial_number == result.serial_number
        assert expected.product_number == result.product_number
    assert len(computers) == len(results)


def test_computers_read_missing_product_number_is_preserved(tmp_computers):
    sns = ["abac", "caba"]
    pns = ["", "456E6"]
    computers = [Computer(s, p) for s, p in zip(sns, pns)]
    fpath = tmp_computers(sns, pns)
    results = computers_read(fpath)
    print(results)
    for expected, result in zip(computers, results):
        assert expected.serial_number == result.serial_number
        assert expected.product_number == result.product_number
    assert len(computers) == len(results)


def test_computers_read_raises_value_error_with_invalid_column_names(tmp_path):
    fname = "hp_products.csv"
    fpath = tmp_path / fname
    computers = {
        "my_serial": ["aba", "caba"],
        "my_product": ["123E4", "456E6"],
        "my_garbage": ["something", "in the air"],
    }
    df = pd.DataFrame(computers)
    df.to_csv(fpath, index=False)
    with pytest.raises(ValueError):
        computers_read(fpath)
