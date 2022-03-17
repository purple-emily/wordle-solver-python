# The use of variables is like so:
#
# PYTHONPATH=Hello
# echo ${PYTHONPATH}

.PHONY: lint
lint:
	@echo "🚨 Linting code"
	poetry run isort --diff --check-only --settings-path pyproject.toml ./src tests
	poetry run black --diff --check --config pyproject.toml ./src tests
	poetry run mypy --config-file pyproject.toml ./src
	poetry run flake8 --config=.flake8 ./src tests
	poetry run pylint --rcfile=.pylintrc ./src tests
	poetry check
	poetry run safety check --full-report


.PHONY: format
format:
	@echo "🎨 Formatting code"
	poetry run isort --settings-path pyproject.toml ./src tests
	poetry run black --config pyproject.toml ./src tests


.PHONY: test
test:
	@echo "🍜 Running pytest"
	poetry run pytest -c pyproject.toml
	poetry run coverage-badge -o assets/images/coverage.svg -f


.PHONY: all
all: format lint test
