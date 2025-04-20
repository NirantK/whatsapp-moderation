# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Build & Development Commands
- **Install dependencies**: `uv sync --all-extras`
- **Lint**: `ruff check . --fix`
- **Format**: `ruff format .`
- **Combined fix**: `make fix`
- **Run tests**: `uv run pytest --cov=src`
- **Run single test**: `uv run pytest tests/path_to_test.py::test_function_name -v`
- **Run WhatsApp analyzer**: `python -m src.cli.main analyze-single /path/to/chat.txt --window-days 90`
- **Save inactive users**: `python -m src.cli.main analyze-single /path/to/chat.txt --window-days 90 --output output.csv`

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

## Project Notes
- The WhatsApp analyzer provides tools for identifying inactive users in WhatsApp groups
- WhatsApp chat export files should be placed in `data/chat_text_files/` directory
- Analysis supports various window sizes (e.g., 30, 60, 90 days) for inactivity detection
- Output files use pipe-separated values format (CSV with `|` delimiter)