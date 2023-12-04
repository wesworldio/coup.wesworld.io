.PHONY = install-poetry install run lint
.DEFAULT_GOAL = run


###################################################################################################################
# certificate specific commands

install-poetry:
	@echo "Installing Poetry..."
	@curl -sSL https://install.python-poetry.org | POETRY_VERSION=1.4.0 python3 -
	# @curl -sSL https://install.python-poetry.org | python3 -

install:
	poetry install

run:
	poetry run python cli.py

lint:
	poetry run isort .
	poetry run black .
	poetry run autopep8 --in-place --aggressive --aggressive -r .
	poetry run flake8 .
