# ManAISys Python Style Guide

This tool is designed to help you maintain a consistent coding style in your Python projects. It checks for common style issues and enforces best practices.

## Tools Used
- **Ruff**: A fast Python linter and formatter.
- **Black**: The uncompromising Python code formatter.
- **isort**: A Python utility for sorting imports.
- **mypy**: An optional static type checker for Python.
- **pydocstyle**: A documentation style checker for Python docstrings.
- **darglint**: A docstring style checker for Python.
- **docformatter**: A tool to format docstrings in Python.

## Installation

Run the following command to install the required tools:

## Using pip

```bash
pip install manaisys-style-guide
```

## Using Poetry

```bash
poetry add manaisys-style-guide
```

## Usage
You can run the style checks and formatting tools using the following commands:
(with Poetry use `poetry run style-guide <command>`)

```bash
style-guide format
style-guide format_docs
style-guide typecheck
style-guide lint
style-guide lint_docs
style-guide all
```