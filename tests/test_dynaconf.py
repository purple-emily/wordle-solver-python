import pytest

from wordle_solver.config import settings


def test_dynaconf():
    """Test Dynaconf works.

    `tests_enabled` should not exist before setting the Dynaconf env to 'testing'.

    `tests_enabled` should exist as a bool with the value True after setting the
    Dynaconf env to 'testing'.
    """
    with pytest.raises(
        AttributeError, match="'Settings' object has no attribute 'TESTS_ENABLED'"
    ):
        settings.tests_enabled  # pylint: disable=pointless-statement

    settings.configure(FORCE_ENV_FOR_DYNACONF="testing")
    assert settings.tests_enabled
