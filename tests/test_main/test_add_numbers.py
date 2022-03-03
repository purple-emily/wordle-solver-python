import pytest

from template_basic_python.main import add_numbers


@pytest.mark.parametrize(
    ("number_one", "number_two", "result"),
    [
        (2, 4, 6),
        (5, 5, 10),
    ],
)
def test_add_numbers(number_one, number_two, result):
    assert add_numbers(number_one, number_two) == result
