# ManAISys Python Style Guide

This tool is designed to help you maintain a consistent coding style in your Python projects. It checks for common style issues and enforces best practices.

## Tools Used
- **Ruff**: A fast Python linter and formatter.
- **Black**: The uncompromising Python code formatter.
- **isort**: A Python utility for sorting imports.
- **mypy**: An optional static type checker for Python.

## Installation

Run the following command to install the required tools:

```bash
poetry install
```

## Usage
You can run the style checks and formatting tools using the following commands:

```bash
poetry run style-guide typecheck
poetry run style-guide lint
poetry run style-guide format
poetry run style-guide all
```