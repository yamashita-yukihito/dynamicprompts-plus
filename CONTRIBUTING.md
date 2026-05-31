# Contributing to dynamicprompts-plus

Thank you for your interest in contributing! This fork extends [adieyal/dynamicprompts](https://github.com/adieyal/dynamicprompts) with conditional prompt evaluation. Contributions that improve the `%if{}` command, fix bugs, or improve documentation are especially welcome.

## Development setup

**Requirements:** Python 3.8+

```bash
git clone https://github.com/yamashita-yukihito/dynamicprompts-plus.git
cd dynamicprompts-plus
pip install -e ".[dev,attentiongrabber,feelinglucky,yaml]"
```

## Running tests

```bash
pytest
```

To run only the `%if{}` command tests:

```bash
pytest tests/parser/test_parser_if.py -v
```

To run with coverage:

```bash
pytest --cov=src --cov-report=term-missing
```

## Code style

This project uses [ruff](https://github.com/astral-sh/ruff) for linting and formatting, and [mypy](https://mypy-lang.org/) for type checking.

```bash
pip install pre-commit
pre-commit install
pre-commit run --all-files
```

## Project structure

```
src/dynamicprompts/
  commands/
    if_command.py     # IfCommand and Predicate dataclasses
  parser/
    parse.py          # Parser entry point (handles %if{} syntax)
  samplers/
    ...               # Sampling logic that evaluates IfCommand
tests/
  parser/
    test_parser_if.py # Tests for %if{} parsing and evaluation
```

## Submitting a pull request

1. Fork the repo and create a branch from `main`.
2. Add tests for any new behaviour.
3. Make sure `pytest` and `pre-commit run --all-files` both pass.
4. Open a PR with a clear description of what changed and why.

## Reporting bugs

Please use the [bug report template](.github/ISSUE_TEMPLATE/bug_report.yml) when filing issues. Include the prompt template that caused the problem and the output you expected vs. what you got.

## Feature requests

Open a [feature request](.github/ISSUE_TEMPLATE/feature_request.yml) describing the use case. New operators for `%if{}` (e.g., `lt`, `gt`, `contains`) and improved error messages are good candidates.
