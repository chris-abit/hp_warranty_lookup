from computer import Computer


def test_matching_both_serial_and_product_number_is_valid():
    sn = "Test"
    pn = "Product"
    a = Computer(sn, pn)
    b = Computer(sn, pn)
    assert a == b


def test_matching_only_serial_number_is_invalid():
    sn = "Test"
    pn = "Product"
    a = Computer(sn, pn)
    b = Computer("Garbage", pn)
    assert not a == b


def test_matching_only_product_number_is_invalid():
    sn = "Test"
    pn = "Product"
    a = Computer(sn, pn)
    b = Computer(sn, "Garbage")
    assert not a == b


def test_comparison_only_checks_serial_and_product_number():
    sn = "Test"
    pn = "Product"
    a = Computer(sn, pn)
    b = Computer(sn, pn)
    b.url = "my_url"
    b.warranty_start = "start date"
    b.warranty_end = "end date"
    b.error = "Snake error."
    assert a == b
