install:
	uv sync --all-extras
fix:
	ruff format . 
	ruff check . --fix

test:
	uv run pytest --cov=PACKAGE --cov-report=term-missing
