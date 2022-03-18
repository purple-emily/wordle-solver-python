import collections
import pickle
from math import log2
from pathlib import Path

from wordle_solver.utils import DEFAULT_WORDLIST_PATH, calculate_hints

# from tqdm import tqdm  # type: ignore


def map_all_hints(
    guesses: list[str], solutions: list[str]
) -> dict[str, dict[tuple[int, ...], set[str]]]:
    # TODO: finish docstring
    """_summary_.

    Args:
        guesses (list[str]): _description_
        solutions (list[str]): _description_

    Returns:
        dict[str, dict[tuple[int, ...], set[str]]]: _description_
    """
    # all_hints[word][hint] = answers
    all_hints: dict[str, dict[tuple[int, ...], set[str]]] = collections.defaultdict(
        lambda: collections.defaultdict(set)
    )

    # for guess in tqdm(guesses):
    for guess in guesses:
        for secret in solutions:
            hint = calculate_hints(guess, secret)
            all_hints[guess][hint].add(secret)

    return dict(all_hints)


def get_initial_hints_dict(
    guesses: list[str],
    solutions: list[str],
    directory: Path = DEFAULT_WORDLIST_PATH,
) -> dict[str, dict[tuple[int, ...], set[str]]]:
    # TODO: finish docstring
    """_summary_.

    Args:
        guesses (list[str]): _description_
        solutions (list[str]): _description_
        directory (Path): _description_. Defaults to DEFAULT_WORDLIST_PATH.

    Returns:
        dict[str, dict[tuple[int, ...], set[str]]]: _description_
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


# def main() -> None:
# _, guesses, solutions = load_word_list()
# initial_hints = get_initial_hints_dict(guesses, solutions)


# if __name__ == "__main__":
#     main()
