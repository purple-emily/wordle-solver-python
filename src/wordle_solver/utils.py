from collections import Counter
from math import log2
from pathlib import Path
from pickle import dump, load

from wordle_solver.config import settings

DEFAULT_WORDLIST_PATH = (
    Path(__file__).parent.parent.parent / "data" / f"{settings.default_wordlist}"
)


def load_word_list(directory: Path) -> tuple[set[str], set[str]]:
    """Load a word list from a directory.

    The directory must have a `guesses.txt` and `solutions.txt`. The files containing
    valid guesses and possible solutions, respectively.

    Args:
        directory (Path):
            The directory with the word list files.
            Defaults to the `data` folder, and the variable `default_wordlist`
            in `settings.toml`.

    Raises:
        FileNotFoundError: The directory does not exist.
        FileNotFoundError: The file `guesses.txt` does not exist.
        FileNotFoundError: The file `solutions.txt` does not exist.

    Returns:
        tuple[str, set[str], set[str]]:
            The name of the word list, the valid guesses, and the possible solutions.
    """
    if not directory.exists():
        raise FileNotFoundError(f"{directory} does not exist")

    guesses_file = directory / "guesses.txt"

    if not guesses_file.exists():
        raise FileNotFoundError(f"{guesses_file} does not exist")

    solutions_file = directory / "solutions.txt"

    if not solutions_file.exists():
        raise FileNotFoundError(f"{solutions_file} does not exist")

    guesses = set(guesses_file.read_text().splitlines())
    solutions = set(solutions_file.read_text().splitlines())

    return guesses, solutions


def calculate_wordle_hint(guess: str, secret: str) -> tuple[int, ...]:
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
    non_matches_count = Counter(
        secret for secret, guess in zip(secret, guess) if secret != guess
    )

    the_hint: list[int] = []

    for guess_char, secret_char in zip(  # pylint: disable=use-list-comprehension
        guess, secret
    ):
        if guess_char == secret_char:
            the_hint.append(2)
        elif guess_char in secret and non_matches_count[guess_char] > 0:
            the_hint.append(1)
            non_matches_count[guess_char] -= 1
        else:
            the_hint.append(0)

    return tuple(the_hint)


def create_hint_tree(
    guesses: set[str], solutions: set[str]
) -> dict[str, dict[tuple[int, ...], set[str]]]:
    """_summary_. # TODO: summary

    Args:
        guesses (set[str]): _description_ # TODO: description
        solutions (set[str]): _description_ # TODO: description

    Returns:
        dict[str, dict[tuple[int, ...], set[str]]]: _description_ # TODO: description
    """
    hint_tree: dict[str, dict[tuple[int, ...], set[str]]] = {}

    for guess in guesses:
        for secret in solutions:
            hint = calculate_wordle_hint(guess, secret)
            hint_tree.setdefault(guess, {}).setdefault(hint, set()).add(secret)

    return hint_tree


def get_hint_tree(
    directory: Path,
    guesses: set[str],
    solutions: set[str],
) -> dict[str, dict[tuple[int, ...], set[str]]]:
    """_summary_. # TODO: summary

    Args:
        directory (Path): _description_ # TODO: description
        guesses (set[str]): _description_ # TODO: description
        solutions (set[str]): _description_ # TODO: description

    Raises:
        FileNotFoundError: _description_ # TODO: description

    Returns:
        dict[str, dict[tuple[int, ...], set[str]]]: _description_ # TODO: description
    """
    if not directory.exists():
        raise FileNotFoundError(f"{directory} does not exist")

    hint_tree_file = directory / "hint_tree.pickle"

    if not hint_tree_file.exists():
        hint_tree = create_hint_tree(guesses, solutions)
        dump(hint_tree, hint_tree_file.open("wb"))
    else:
        hint_tree = load(hint_tree_file.open("rb"))

    return hint_tree


def calculate_entropies(
    guesses: set[str],  # pylint: disable=unused-argument
    solutions: set[str],
    max_solutions: int,
    hint_tree: dict[str, dict[tuple[int, ...], set[str]]],
) -> dict[str, float]:
    """This function calculates the entropy of each word in left in solutions.

    The entropy is the level of information we expect to receive if we select the word
    as the guess word. The higher the entropy the more information we expect to receive.

    Args:
        guesses (set[str]):
            the list of valid guesses
        solutions (set[str]):
            the list of remaining solutions
        max_solutions (int):
            the maximum number of solutions to consider
        hint_tree (dict[str, dict[tuple[int, ...], set[str]]]):
            the hint dictionary

    Returns:
        dict[str, float]:
            a dictionary with the word as the key and entropy as value
    """
    total_remaining_solutions = len(solutions)
    entropies: dict[str, float] = {}

    for word in guesses:
        # Calculate the entropy of the word
        entropy: float = 0
        for hint in hint_tree[word]:
            if len(solutions) == max_solutions:
                # If we are calculating the entropy of the entire solutions set f
                probability = len(hint_tree[word][hint]) / total_remaining_solutions
            else:
                len_new_solutions = len(
                    set(solutions).intersection(hint_tree[word][hint])
                )
                if len_new_solutions == 0:
                    continue
                probability = len_new_solutions / total_remaining_solutions
            entropy += -probability * log2(probability)

        entropies[word] = round(entropy, 2)

    sorted_entropies = sorted(entropies.items(), key=lambda x: x[1], reverse=True)
    return dict(sorted_entropies)
