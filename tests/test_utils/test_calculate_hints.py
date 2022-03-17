import pytest

from wordle_solver.utils import calculate_hints


class TestCalculateHints:
    @pytest.mark.parametrize(
        ("guess", "secret", "expected_output"),
        [
            ("chess", "swiss", (0, 0, 0, 2, 2)),
            ("orate", "oater", (2, 1, 1, 1, 1)),
            ("slate", "gator", (0, 0, 1, 1, 0)),
            ("prion", "gator", (0, 1, 0, 2, 0)),
            ("rotor", "gator", (0, 0, 2, 2, 2)),
            ("gator", "gator", (2, 2, 2, 2, 2)),
        ],
    )
    def test_success(
        self, guess: str, secret: str, expected_output: tuple[int, ...]
    ) -> None:
        assert calculate_hints(guess, secret) == expected_output

    @pytest.mark.parametrize(
        ("guess", "secret", "expected_output"),
        [
            ("chess", "swiss", (1, 1, 1, 2, 2)),
            ("orate", "oater", (2, 0, 1, 0, 1)),
            ("slate", "gator", (10, 0, 1, 1, 0)),
            ("prion", "gator", (0, 1, 4, 2, 0)),
            ("rotor", "gator", (-10, 0, 2, 2, 2)),
            ("gator", "gator", (2, 0, 2, 2, 2)),
        ],
    )
    def test_failure(
        self, guess: str, secret: str, expected_output: tuple[int, ...]
    ) -> None:
        assert calculate_hints(guess, secret) != expected_output
