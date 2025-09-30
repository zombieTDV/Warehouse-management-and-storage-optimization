from casey.menu import sum, subtract

# from casey.cli.menu import *'


def test_sample():
    pass


# Unit tests
def test_sum_positive_numbers():
    assert sum(2, 3) == 5, "sum(2, 3) phải bằng 5"


def test_sum_negative_numbers():
    assert sum(-1, -4) == -5, "sum(-1, -4) phải bằng -5"


def test_sum_mixed_numbers():
    assert sum(-2, 5) == 3, "sum(-2, 5) phải bằng 3"


def test_subtract_positive_numbers():
    assert subtract(10, 4) == 6, "subtract(10, 4) phải bằng 6"


def test_subtract_result_negative():
    assert subtract(3, 5) == -2, "subtract(3, 5) phải bằng -2"


def test_subtract_with_zero():
    assert subtract(7, 0) == 7, "subtract(7, 0) phải bằng 7"
