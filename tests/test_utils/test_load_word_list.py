from pathlib import Path

import pytest

from wordle_solver.utils import load_word_list


@pytest.fixture()
def guesses_text():
    return "amaze\nanvil\nbison\nchoco\nfraud\nquilt\nrotor\nseven"


@pytest.fixture()
def solutions_text():
    return "amaze\nanvil\nbison\nchoco\nfraud"


def test_dir_does_not_exist_raises_exception(tmp_path: Path) -> None:
    assert not Path(tmp_path / "does_not_exist").exists()

    with pytest.raises(FileNotFoundError) as exc_info:
        load_word_list(tmp_path / "does_not_exist")

    assert "does_not_exist does not exist" in str(exc_info.value)


def test_guesses_file_does_not_exist_raises_exception(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError) as exc_info:
        load_word_list(tmp_path)

    assert "guesses.txt does not exist" in str(exc_info.value)


def test_solutions_file_does_not_exist_raises_exception(
    tmp_path: Path,
    guesses_text: str,  # pylint: disable=redefined-outer-name
) -> None:
    guesses_file = Path(tmp_path / "guesses.txt")
    guesses_file.touch()
    guesses_file.write_text(guesses_text)  # pylint: disable=unspecified-encoding

    with pytest.raises(FileNotFoundError) as exc_info:
        load_word_list(tmp_path)

    assert "solutions.txt does not exist" in str(exc_info.value)


def test_success(
    tmp_path: Path,
    guesses_text: str,  # pylint: disable=redefined-outer-name
    solutions_text: str,  # pylint: disable=redefined-outer-name
) -> None:
    guesses_f = Path(tmp_path / "guesses.txt")
    guesses_f.touch()
    guesses_f.write_text(guesses_text)  # pylint: disable=unspecified-encoding

    solutions_f = Path(tmp_path / "solutions.txt")
    solutions_f.touch()
    solutions_f.write_text(solutions_text)  # pylint: disable=unspecified-encoding

    guesses, solutions = load_word_list(tmp_path)

    for word in guesses_text.split("\n"):
        assert word in guesses
    assert "a" not in guesses

    for word in solutions_text.split("\n"):
        assert word in solutions
    assert "rotor" not in solutions
