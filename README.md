# WhatsApp Analyzer

A tool for analyzing WhatsApp group chat exports. It supports both single group and multiple group analysis, with features for identifying inactive users and analyzing message patterns.

## Features

- Parse WhatsApp chat exports into structured data
- Analyze single or multiple group chats
- Identify inactive users based on configurable criteria
- Track user joining dates and message counts
- Support for excluding contacts (users with names starting with '~')
- Comprehensive logging and progress tracking
- Activity scoring with exponential decay to identify formerly active members
- Web interface for easy analysis
- Command-line interface for batch processing

## Installation

1. Install `uv` if you haven't already:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

2. Clone the repository and install dependencies:
```bash
git clone <repository-url>
cd whatsapp-analyzer
uv venv
source .venv/bin/activate  # On Unix/macOS
# or
.venv\Scripts\activate  # On Windows
uv pip install -e .
```

## Usage

### Command Line Interface

The tool provides a command-line interface for analyzing WhatsApp chats:

```bash
# Analyze a single chat
whatsapp-analyzer analyze-single path/to/chat.txt --output results.csv

# Analyze multiple chats in a directory
whatsapp-analyzer analyze-multiple path/to/groups/ --output combined_results.csv

# Calculate activity scores for inactive users
whatsapp-analyzer score-inactive path/to/chat.txt --output scored_users.csv
```

Options:
- `--output`, `-o`: Save results to a CSV file
- `--window-days`, `-w`: Number of days to consider for inactivity (default: 60)
- `--exclude-contacts`: Exclude contacts (users with names starting with '~')
- `--decay-days`, `-d`: Number of days for score to decay to zero (default: 90)
- `--reference-messages`, `-r`: Number of messages that would give a score of 1.0 (default: 5)

### Web Interface

The tool also provides a web interface for easy analysis:

```bash
# Start the web server
whatsapp-web
```

Then open your browser and navigate to `http://localhost:8000`. The web interface allows you to:
- Upload WhatsApp chat exports
- Configure analysis parameters
- View results in a table format
- Download results as CSV files

## Development

- Format code: `ruff format .`
- Lint code: `ruff check .`
- Fix linting issues: `ruff check . --fix`

## Project Structure

```
whatsapp-analyzer/
├── src/
│   ├── core/           # Core functionality
│   │   ├── analysis.py # WhatsApp group analysis
│   │   ├── models.py   # Data models
│   │   └── utils.py    # Utility functions
│   ├── cli/            # Command-line interface
│   │   └── main.py     # CLI entry point
│   └── web/            # Web interface
│       ├── static/     # Static files (CSS)
│       └── main.py     # Web app entry point
├── tests/              # Test files
├── pyproject.toml      # Project configuration
└── README.md          # This file
```

## TODO

### Repository Reorganization
- [x] Create a central `src` directory for core functionality
- [x] Move core WhatsApp analysis logic to `src/core`
- [x] Create CLI interface in `src/cli`
- [x] Move web app to `src/web`
- [x] Update imports and dependencies
- [x] Update documentation
- [x] Add proper package structure with `__init__.py` files
- [x] Update deployment configurations

### Feature TODOs
- [ ] Add support for more WhatsApp export formats
- [ ] Implement message content analysis
- [ ] Add visualization capabilities
- [ ] Add export to different formats (JSON, Excel)
- [ ] Add support for message reactions analysis
- [ ] Implement user activity patterns
- [ ] Add support for media message analysis