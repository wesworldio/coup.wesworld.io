.PHONY = install-poetry install-poetry install-parallel install run lint run-bots run-games run-group run-parallel file-descriptor-limit

.DEFAULT_GOAL = run


###################################################################################################################
# certificate specific commands

install-poetry:
	@echo "Installing Poetry..."
	@curl -sSL https://install.python-poetry.org | POETRY_VERSION=1.4.0 python3 -
	# @curl -sSL https://install.python-poetry.org | python3 -

install-parallel:
	@echo "Installing GNU Parallel..."
	@brew install parallel

install:
	poetry install

run:
	GAME_COUNT=1 poetry run python cli.py

run-bots:
	PLAYER_TYPE=bot BOT_THINK_TIME=0 GAME_COUNT=1 poetry run python cli.py

run-games:
	PLAYER_TYPE=bot BOT_THINK_TIME=0 GAME_COUNT=$(games) poetry run python cli.py

run-group:
	make run-games games=$(games)
	
lint:
	poetry run isort .
	poetry run black .
	poetry run autopep8 --in-place --aggressive --aggressive -r .
	poetry run flake8 .

run-parallel:
	# Run groups in parallel using GNU Parallel
	parallel -j $(groups) 'make run-group games={}' ::: $(shell seq 1 $(groups))

file-descriptor-limit:
	# Increase the file descriptor limit
	ulimit -n 4096