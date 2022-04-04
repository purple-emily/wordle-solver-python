from collections import Counter
from multiprocessing import Pool
from pathlib import Path
from random import choice
from statistics import mean
from typing import Any

import typer
from click import Choice as click_Choice
from typer import echo as typer_echo
from typer import prompt as typer_prompt
from typer import secho as typer_secho
from typer import style as typer_style

from wordle_solver.utils import (
    DEFAULT_WORDLIST_PATH,
    calculate_entropies,
    calculate_wordle_hint,
    get_hint_tree,
    load_word_list,
)

app = typer.Typer(add_completion=False)  # pragma: no cover
state: dict[Any, Any] = {}  # pragma: no cover


def get_hint_feedback(chosen_word: str) -> tuple[int, ...]:  # pragma: no cover
    while True:
        typer_echo("b = black (grey) / y = yellow / g = green")

        hint_input = typer_prompt(
            "Please provide the result for '"
            + typer_style(chosen_word, fg="bright_magenta")
            + "'"
        )

        if not all(char in set("byg") for char in hint_input):
            typer_secho(
                "Invalid input. Please only use the characters 'b', 'y', or 'g'",
                fg="red",
            )
            typer_echo("Try again...")
            continue

        if len(hint_input) != 5:
            typer_secho("Invalid input. Input must be 5 characters long.", fg="red")
            typer_echo("Try again...")
            continue

        break

    input_to_output: dict[str, int] = {"g": 2, "y": 1, "b": 0}

    return tuple(input_to_output[input_char] for input_char in hint_input)


def calculate_iterations(data: dict[Any, Any]) -> int:
    initial_guess = data["initial_guess"]
    secret = data["secret"]
    hint_dictionary = data["hint_dictionary"]
    all_guesses = data["all_guesses"]
    total_solutions = data["total_solutions"]

    iteration_count = 1

    hint = calculate_wordle_hint(initial_guess, secret)
    local_solutions = set(hint_dictionary[initial_guess][hint])

    while True:
        iteration_count += 1
        total_remaining_solutions = len(local_solutions)

        if total_remaining_solutions == 1:
            chosen_guess = list(local_solutions)[0]
        elif total_remaining_solutions == 2:
            chosen_guess = choice(list(local_solutions))
        else:
            entropies = calculate_entropies(
                all_guesses, local_solutions, total_solutions, hint_dictionary
            )
            chosen_guess = list(entropies.keys())[0]

        hint = calculate_wordle_hint(chosen_guess, secret)
        if hint == (2, 2, 2, 2, 2):
            return iteration_count

        local_solutions = set(local_solutions).intersection(
            hint_dictionary[chosen_guess][hint]
        )


@app.command()  # pragma: no cover
def stats(
    word_list: Path = typer.Option(
        DEFAULT_WORDLIST_PATH,
        "--word-list",
        "-w",
        help="The directory location containing the word list files.",
    ),
) -> None:
    all_guesses, all_solutions = load_word_list(word_list)
    max_solutions = len(all_solutions)
    hint_tree = get_hint_tree(word_list, all_guesses, all_solutions)

    initial_entropies = calculate_entropies(
        all_guesses, all_solutions, max_solutions, hint_tree
    )
    top_initial_guesses: list[str] = list(initial_entropies.keys())[0:10]

    for initial_guess in top_initial_guesses:
        list_of_data_dicts: list[dict[Any, Any]] = []

        for secret in all_solutions:
            data_dict: dict[Any, Any] = {}
            data_dict["initial_guess"] = initial_guess
            data_dict["secret"] = secret
            data_dict["hint_dictionary"] = hint_tree
            data_dict["all_guesses"] = all_guesses
            data_dict["total_solutions"] = max_solutions

            list_of_data_dicts.append(data_dict)

        with Pool(10) as pool:
            iteration_counts = pool.map(calculate_iterations, list_of_data_dicts)

        # for d in list_of_data_dicts:
        #     print(calculate_iterations(d))

        typer_echo(f"Using guess: {initial_guess}")
        typer_echo(f"Total words solved: {len(iteration_counts)}")
        typer_echo(f"Average guess: {round(mean(iteration_counts), 3)}")
        typer_echo(f"Total counts: {Counter(iteration_counts)}")


@app.command()  # pragma: no cover
def solver(
    word_list: Path = typer.Option(
        DEFAULT_WORDLIST_PATH,
        "--word-list",
        "-w",
        help="The directory location containing the word list files.",
    ),
) -> None:
    """Solve a word on Wordle."""
    guesses, solutions = load_word_list(word_list)
    max_solutions = len(solutions)
    hint_dictionary = get_hint_tree(word_list, guesses, solutions)

    for _ in range(6):
        len_solutions = len(solutions)
        if len_solutions == 0:
            # TODO: Error out?
            pass
        elif len_solutions == 1:
            typer_echo("There is only 1 reamining possible answer:")
            typer_echo(typer_style(solutions, bg="magenta"))

            chosen_guess = list(solutions)[0]
        elif len_solutions == 2:
            typer_echo("There are 2 remaining possible answers:")
            typer_echo(typer_style(solutions, bg="magenta"))

            chosen_guess = typer_prompt(
                "Please select a guess word:",
                type=click_Choice(list(solutions)),
            )
        else:
            entropies = calculate_entropies(
                guesses, solutions, max_solutions, hint_dictionary
            )
            top_8_entropies = dict(list(entropies.items())[0:8])

            typer_echo(f"There are {len_solutions} remaining possible answers.")
            if len_solutions < 8:
                typer_echo(typer_style(solutions, bg="magenta"))

            typer_echo("The top 8 guesses are:")
            typer_echo(typer_style(top_8_entropies, bg="blue"))

            chosen_guess = typer_prompt(
                "Please select a guess word:",
                type=click_Choice(list(top_8_entropies.keys())),
            )

        hint_feedback = get_hint_feedback(chosen_guess)
        if hint_feedback == (2, 2, 2, 2, 2):
            typer_secho("Victory!", fg="bright_green")
            return

        solutions = set(solutions).intersection(
            hint_dictionary[chosen_guess][hint_feedback]
        )


@app.callback()  # pragma: no cover
def main() -> None:
    # """
    # Manage users in the awesome CLI app.
    # """
    pass


if __name__ == "__main__":
    app()
