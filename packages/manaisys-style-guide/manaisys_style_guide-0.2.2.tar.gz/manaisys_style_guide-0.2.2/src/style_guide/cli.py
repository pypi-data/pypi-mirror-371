import subprocess

import typer

app = typer.Typer(help="MyCompany Python code style tools")


@app.command()
def format():
    """Run Black + isort on the codebase."""
    subprocess.run(["black", "."])
    subprocess.run(["isort", "."])
    subprocess.run(["ruff", "check", ".", "--fix"])


@app.command()
def lint():
    """Run Ruff linting."""
    subprocess.run(["ruff", "check", "."])


@app.command()
def typecheck():
    """Run mypy type checking."""
    subprocess.run(["mypy", "."])

@app.command()
def lint_docs():
    """Check docstring style (pydocstyle + darglint)."""
    subprocess.run(["pydocstyle", "src"], check=False)
    subprocess.run(["darglint", "src"], check=False)

@app.command()
def format_docs():
    """Format all docstrings with docformatter."""
    subprocess.run(["docformatter", "-r", "-i", "src"], check=False)


@app.command()
def all():
    """Run all checks (format, lint, typecheck)."""
    format()
    format_docs()
    typecheck()
    lint()
    lint_docs()


if __name__ == "__main__":
    app()
