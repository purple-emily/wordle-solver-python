import collections
import pickle
from math import log2
from pathlib import Path

from wordle_solver.utils import DEFAULT_WORDLIST_PATH, calculate_hints

# from tqdm import tqdm  # type: ignore


def map_all_hints(
    guesses: list[str], solutions: list[str]
) -> dict[str, dict[tuple[int, ...], set[str]]]:
    """Create a dictionary of all guesses applied to all solutions.

    The dictionary will be in the following format:
    dict_variable[guess][hint] = matching_answers

    Args:
        guesses (list[str]): the guesses list
        solutions (list[str]): the remaining answers list

    Returns:
        dict[str, dict[tuple[int, ...], set[str]]]:
            dict_variable[guess][hint] = matching_answers
    """
    all_hints: dict[str, dict[tuple[int, ...], set[str]]] = collections.defaultdict(
        lambda: collections.defaultdict(set)
    )

    for guess in guesses:  # tqdm(guesses)
        for secret in solutions:
            hint = calculate_hints(guess, secret)
            all_hints[guess][hint].add(secret)

    return dict(all_hints)


def get_initial_hints_dict(
    guesses: list[str],
    solutions: list[str],
    directory: Path = DEFAULT_WORDLIST_PATH,
) -> dict[str, dict[tuple[int, ...], set[str]]]:
    """A wrapper around `map_all_hints` that pickles and unpickles the data for faster
    loading.

    Args:
        guesses (list[str]):
            the guesses list
        solutions (list[str]):
            the remaining answers list
        directory (Path):
            the directory where the pickled file will be stored. Defaults to DEFAULT_WORDLIST_PATH.

    Returns:
        dict[str, dict[tuple[int, ...], set[str]]]:
            dict_variable[guess][hint] = matching_answers
    """
    hint_file = Path(directory / "initial_hints.pkl")

    if hint_file.exists():
        all_hints = pickle.load(
            open(hint_file, "rb")  # pylint: disable=consider-using-with
        )
    else:
        all_hints = map_all_hints(guesses, solutions)
        pickle.dump(
            all_hints, open(hint_file, "wb+")  # pylint: disable=consider-using-with
        )

    return dict(all_hints)


def calculate_entropies(
    guesses: list[str],  # pylint: disable=unused-argument
    solutions: list[str],
    hints_dict: dict[str, dict[tuple[int, ...], set[str]]],
) -> dict[str, float]:
    """This function calculates the entropy of each word in left in solutions.

    The entropy is the level of information we expect to receive if we select the word
    as the guess word. The higher the entropy the more information we expect to receive.

    Args:
        guesses (list[str]):
            the list of valid guesses
        solutions (list[str]):
            the list of remaining solutions
        hints_dict (dict[str, dict[tuple[int, ...], set[str]]]):
            the hint dictionary

    Returns:
        dict[str, float]:
            a dictionary with the word as the key and entropy as value
    """
    total_remaining_solutions = len(solutions)
    entropies: dict[str, float] = {}

    for word, inner_dict in hints_dict.items():
        word_expected_info: list[float] = []

        for answers in inner_dict.values():
            probability = len(answers) / total_remaining_solutions
            shannon_information = -log2(probability)
            expected_info = probability * shannon_information

            word_expected_info.append(expected_info)

        entropy = round(sum(word_expected_info), 2)
        entropies[word] = entropy

    entropies_sorted = sorted(entropies.items(), key=lambda x: x[1], reverse=True)

    return dict(entropies_sorted)
