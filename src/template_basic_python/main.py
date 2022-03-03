from loguru import logger

from .config import settings  # noqa: F401, TC002

# logger.add("example.log", rotation="1 week", level="INFO")


def add_numbers(number1: int, number2: int) -> int:
    """Add two numbers together.

    Args:
        number1 (int): The first number.
        number2 (int): The second number.

    Returns:
        int: The sum of number1 + number2.

    Examples:
        >>> add_numbers(10, 5)
        15
    """
    return number1 + number2


def main() -> None:
    """Print a log message."""
    logger.debug("That's it, beautiful and simple logging!")  # pragma: no cover


if __name__ == "__main__":
    main()
