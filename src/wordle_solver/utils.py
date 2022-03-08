import collections
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


def calculate_hints(guess: str, secret: str) -> tuple[int, ...]:
    """Compare a guess against a secret word and calculate a hint on how close the
    guess word is to the secret word.

    The hint will be comprised of the following:
        - 2 - the guess <char> is in the secret word and in the correct spot.
        - 1 - the guess <char> is in the secret word but in the wrong spot.
        - 0 - the guess <char> is not in the secret word at all.

    Args:
        guess (str): The guess word
        secret (str): The secret word

    Returns:
        tuple[int, ...]: The hint on how close the guess word is to the secret word.

    Examples:
        >>> calculate_hints("chess", "swiss")
        (0, 0, 0, 2, 2)

        >>> calculate_hints("orate", "oater")
        (2, 1, 1, 1, 1)
    """
    count_of_not_exact_matches = collections.Counter(
        secret for secret, guess in zip(secret, guess) if secret != guess
    )

    hint_pattern: list[int] = []

    for secret_char, guess_char in zip(secret, guess):
        if secret_char == guess_char:
            hint_pattern.append(2)  # green
        elif guess_char in secret and count_of_not_exact_matches[guess_char] > 0:
            hint_pattern.append(1)  # yellow
            count_of_not_exact_matches[guess_char] -= 1
        else:
            hint_pattern.append(0)  # grey

    return tuple(hint_pattern)
