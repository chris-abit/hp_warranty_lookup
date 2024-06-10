import pytest
import pandas as pd
import numpy as np
from computer import Computer, computers_save


def computer_factory():
    """
    Generate a Computer for testing write functionality.
    """
    d_computer = {
        "serial_number": "0XDEAD",
        "product_number": "0XBEEF",
        "warranty_start": "2024-04-01",
        "warranty_end": "2024-04-02",
        "url": "my_url",
        "error": np.NAN,  # Workaround since pandas read_csv fills missing with nan.
    }
    computer = Computer(d_computer["serial_number"], d_computer["product_number"])
    computer.warranty_start = d_computer["warranty_start"]
    computer.warranty_end = d_computer["warranty_end"]
    computer.url = d_computer["url"]
    computer.error = d_computer["error"]
    return computer, d_computer


def test_computers_save_entries_are_correct(tmp_path):
    fname = tmp_path / "hp_warranty.csv"
    items = 8
    pairs = [computer_factory() for computer in range(items)]
    computers = [c for c, _ in pairs]
    d_computers = [d for _, d in pairs]
    expected = pd.DataFrame(d_computers)
    computers_save(computers, fname)
    result = pd.read_csv(fname)
    print(expected)
    print(result)
    assert expected.equals(result)


def test_computers_save_append_works_as_intended(tmp_path):
    fname = tmp_path / "hp_warranty.csv"
    items = 8
    pairs = [computer_factory() for computer in range(items)]
    computers = [c for c, _ in pairs]
    d_computers = [d for _, d in pairs]
    idx = 4
    expected = pd.DataFrame(d_computers)
    computers_save(computers[:idx], fname)
    computers_save(computers[idx:], fname, append=True)
    result = pd.read_csv(fname)
    print(expected)
    print(result)
    assert expected.equals(result)
