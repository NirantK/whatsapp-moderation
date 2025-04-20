# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Build & Development Commands
- **Install dependencies**: `uv sync --all-extras`
- **Lint**: `ruff check . --fix`
- **Format**: `ruff format .`
- **Combined fix**: `make fix`
- **Run tests**: `uv run pytest --cov=src`
- **Run single test**: `uv run pytest tests/path_to_test.py::test_function_name -v`

## Code Style Guidelines
- **Imports**: Standard library first, third-party second, local imports last
- **Formatting**: 
  - Double quotes for strings
  - Line length: 120 characters
  - Use type annotations for all functions
- **Naming**: snake_case for variables/functions, PascalCase for classes
- **Logging**: Use `loguru` for logging, `tqdm` for progress bars
- **Path handling**: Use `pathlib.Path` instead of string paths or os.path
- **Error handling**: Use specific exception types, log errors with loguru

## Version Control
- Make small, reversible commits with clear descriptions
- Start with broad TODO sections in README.md for new features