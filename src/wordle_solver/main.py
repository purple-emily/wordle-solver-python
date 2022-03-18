from pathlib import Path
from random import choice
from statistics import mean
from typing import Any, Counter

import typer
from click import Choice as click_Choice
from tqdm import tqdm  # type: ignore
from typer import echo as typer_echo
from typer import prompt as typer_prompt
from typer import secho as typer_secho
from typer import style as typer_style

from wordle_solver.solver import (
    calculate_entropies,
    get_initial_hints_dict,
    map_all_hints,
)
from wordle_solver.utils import DEFAULT_WORDLIST_PATH, calculate_hints, load_word_list

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


@app.command()  # pragma: no cover
def stats(
    word_list: Path = typer.Option(
        DEFAULT_WORDLIST_PATH,
        "--word-list",
        "-w",
        help="The directory location containing the word list files.",
    ),
) -> None:
    _, all_guesses, all_solutions = load_word_list(word_list)
    initial_hint_dict = get_initial_hints_dict(all_guesses, all_solutions)

    guesses_to_completion: list[int] = []

    for secret in tqdm(all_solutions):
        # typer.echo(f"{secret=}")
        solved = False
        local_solutions = all_solutions[:]
        iteration_count = 0
        local_hint_dict = initial_hint_dict.copy()

        while not solved:
            iteration_count += 1
            total_remaining_solutions = len(local_solutions)

            if total_remaining_solutions == 1:
                chosen_guess = local_solutions[0]
            elif total_remaining_solutions == 2:
                chosen_guess = choice(local_solutions)
            else:
                entropies = calculate_entropies(
                    all_guesses, local_solutions, local_hint_dict
                )
                chosen_guess = list(entropies.keys())[0]

            # typer.echo(f"{chosen_guess=}")
            hint = calculate_hints(chosen_guess, secret)
            if hint == (2, 2, 2, 2, 2):
                solved = True
                guesses_to_completion.append(iteration_count)
                break

            local_solutions = [
                word
                for word in local_solutions
                if calculate_hints(chosen_guess, word) == hint
            ]

            local_hint_dict = map_all_hints(all_guesses, local_solutions)

    typer_echo(f"Total words solved: {len(guesses_to_completion)}")
    typer_echo(f"Average guess: {round(mean(guesses_to_completion), 3)}")
    typer_echo(f"Total counts: {Counter(guesses_to_completion)}")


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
    _, guesses, solutions = load_word_list(word_list)
    hint_dict = get_initial_hints_dict(guesses, solutions)

    for _ in range(6):
        total_remaining_solutions = len(solutions)
        if total_remaining_solutions == 0:
            # TODO: Error out
            pass
        elif total_remaining_solutions == 1:
            typer_echo("There is only 1 reamining possible answer:")
            typer_echo(typer_style(solutions, bg="magenta"))

            chosen_word = solutions[0]
        elif total_remaining_solutions == 2:
            typer_echo("There are 2 remaining possible answers:")
            typer_echo(typer_style(solutions, bg="magenta"))

            chosen_word = typer_prompt(
                "Please select a guess word:",
                type=click_Choice(solutions),
            )
        else:
            entropies = calculate_entropies(guesses, solutions, hint_dict)
            # TODO: Possible error here?
            top_8_entropies = dict(list(entropies.items())[0:8])

            typer_echo(
                f"There are {total_remaining_solutions} remaining possible answers."
            )
            if total_remaining_solutions < 8:
                typer_echo(typer_style(solutions, bg="magenta"))

            typer_echo("The top 8 guesses are:")
            typer_echo(typer_style(top_8_entropies, bg="blue"))

            chosen_word = typer_prompt(
                "Please select a guess word:",
                type=click_Choice(list(top_8_entropies.keys())),
            )

        hint_feedback = get_hint_feedback(chosen_word)
        if hint_feedback == (2, 2, 2, 2, 2):
            typer_secho("Victory!", fg="bright_green")
            return

        solutions = [
            word
            for word in solutions
            if calculate_hints(chosen_word, word) == hint_feedback
        ]

        hint_dict = map_all_hints(guesses, solutions)


@app.callback()  # pragma: no cover
def main() -> None:
    # """
    # Manage users in the awesome CLI app.
    # """
    pass


if __name__ == "__main__":
    app()
