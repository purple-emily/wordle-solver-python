from pathlib import Path

import pytest

from wordle_solver.utils import load_word_list


@pytest.fixture()
def guesses_text():
    return "amaze\nanvil\nbison\nchoco\nfraud\nquilt\nrotor\nseven"


@pytest.fixture()
def solutions_text():
    return "amaze\nanvil\nbison\nchoco\nfraud"


class TestLoadWordList:
    def test_dir_does_not_exist_raises_exception(self, tmp_path: Path) -> None:
        assert not Path(tmp_path / "does_not_exist").exists()

        with pytest.raises(FileNotFoundError) as exc_info:
            load_word_list(tmp_path / "does_not_exist")

        assert "Directory does not exist." in str(exc_info.value)

    def test_guesses_file_does_not_exist_raises_exception(self, tmp_path: Path) -> None:
        with pytest.raises(FileNotFoundError) as exc_info:
            load_word_list(tmp_path)

        assert "Guesses file does not exist in directory." in str(exc_info.value)

    def test_solutions_file_does_not_exist_raises_exception(
        self,
        tmp_path: Path,
        guesses_text: str,  # pylint: disable=redefined-outer-name
    ) -> None:
        guesses_file = Path(tmp_path / "guesses.txt")
        guesses_file.touch()
        guesses_file.write_text(guesses_text)  # pylint: disable=unspecified-encoding

        with pytest.raises(FileNotFoundError) as exc_info:
            load_word_list(tmp_path)

        assert "Solutions file does not exist in directory." in str(exc_info.value)

    def test_success(
        self,
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

        name, guesses, solutions = load_word_list(tmp_path)

        assert name == tmp_path.name

        for word in guesses_text.split("\n"):
            assert word in guesses
        assert "a" not in guesses

        for word in solutions_text.split("\n"):
            assert word in solutions
        assert "rotor" not in solutions
