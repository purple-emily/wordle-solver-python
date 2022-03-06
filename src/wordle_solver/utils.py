from pathlib import Path

from wordle_solver.config import settings


def load_word_list(
    directory: Path = (
        Path(__file__).parent.parent.parent / "data" / f"{settings.default_wordlist}"
    ),
) -> tuple[str, list[str], list[str]]:
    """Load a word list from a directory.

    The directory must have a `guesses.txt` and `solutions.txt`. The files containing
    valid guesses and possible solutions, respectively.

    Args:
        directory (Path):
            The path of the directory containing the `guesses.txt` and `solutions.txt`
            files. Defaults to data/<settings.default_wordlist>.

    Raises:
        FileNotFoundError: The supplied directory does not exist.
        FileNotFoundError: The file `guesses.txt` does not exist.
        FileNotFoundError: The file `solutions.txt` does not exist.

    Returns:
        tuple[str, list[str], list[str]]:
            The name of the word list, the valid guesses, and the possible solutions.
    """
    if not directory.exists():
        raise FileNotFoundError("Directory does not exist.")

    guesses_path: Path = Path(directory / "guesses.txt")

    if not guesses_path.exists():
        raise FileNotFoundError("Guesses file does not exist in directory.")

    solutions_path: Path = Path(directory / "solutions.txt")

    if not solutions_path.exists():
        raise FileNotFoundError("Solutions file does not exist in directory.")

    word_list: str = directory.name

    with open(guesses_path, encoding="utf-8") as guesses_stream:
        guesses = [word.strip() for word in guesses_stream.readlines()]

    with open(solutions_path, encoding="utf-8") as solutions_stream:
        solutions = [word.strip() for word in solutions_stream.readlines()]

    return (word_list, guesses, solutions)
