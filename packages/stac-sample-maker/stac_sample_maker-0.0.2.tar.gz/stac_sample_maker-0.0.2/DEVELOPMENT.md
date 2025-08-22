# Development Guide

This project uses [uv](https://docs.astral.sh/uv/) for dependency management and Python tooling.

## Getting Started

1. **Install uv** (if not already installed):
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. **Clone and setup the project**:
   ```bash
   git clone <repo-url>
   cd stac-sample-maker
   uv sync --all-extras --dev
   ```

3. **Install pre-commit hooks**:
   ```bash
   uv run pre-commit install
   ```

## Development Commands

### Running Tests
```bash
# Run all tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=stac_sample_maker --cov-report=term-missing

# Run specific test file
uv run pytest tests/test_generator.py -v
```

### Code Quality
```bash
# Format code
uv run ruff format .

# Lint and fix issues
uv run ruff check . --fix

# Type checking
uv run mypy stac_sample_maker --ignore-missing-imports

# Run all pre-commit hooks
uv run pre-commit run --all-files
```

### CLI Development
```bash
# Run the CLI
uv run stac-sample-maker --help
uv run stac-sample-maker --num-items 5 --seed 42

# Test CLI with different options
uv run stac-sample-maker --num-items 10 --bbox -122.5 37.7 -122.3 37.8 --output test.ndjson
```

### Building and Publishing
```bash
# Build the package
uv build

# Install locally for testing
uv pip install -e .

# Install from built wheel
uv pip install dist/stac_sample_maker-*.whl
```

## Project Structure

```
stac-sample-maker/
├── .github/workflows/    # CI/CD workflows
├── stac_sample_maker/    # Main package
│   ├── providers/        # Faker providers for STAC extensions
│   ├── __init__.py
│   ├── cli.py           # Command-line interface
│   └── generator.py     # Core generation logic
├── tests/               # Test suite
├── pyproject.toml       # Project configuration
├── README.md           # Project documentation
└── .pre-commit-config.yaml  # Pre-commit hooks
```

## Adding Dependencies

```bash
# Add runtime dependency
uv add faker

# Add development dependency
uv add --dev pytest

# Add optional dependency
uv add --optional validation stac-validator
```

## Working with Virtual Environments

uv automatically manages virtual environments. All `uv run` commands use the project's virtual environment.

```bash
# Activate the virtual environment manually (if needed)
source .venv/bin/activate

# Or run commands through uv (recommended)
uv run python -c "import stac_sample_maker; print('OK')"
```

## Release Process

1. Update version in `pyproject.toml`
2. Create and push a git tag:
   ```bash
   git tag v0.1.1
   git push origin v0.1.1
   ```
3. GitHub Actions will automatically build and publish to PyPI

## Debugging

```bash
# Run Python REPL with package installed
uv run python

# Run specific test with debugging
uv run pytest tests/test_generator.py::TestGenerateStacItems::test_generate_single_item -v -s
```
