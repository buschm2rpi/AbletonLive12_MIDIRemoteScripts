---
name: python-check
description: Run Python code quality checks including syntax validation, mypy type checking, ruff linting, and ruff formatting. Use before committing Python code or when running the project's CI checks.
---

# Python Code Quality Check

## Overview

Runs the full suite of Python code quality checks defined in the project.

## Usage

1. **Syntax check** — `python3 -m py_compile Launchpad95_typed/*.py`
2. **Type check** — `mypy --no-error-summary --show-error-codes --show-column-numbers --ignore-missing-imports --allow-untyped-calls --exclude '_Framework' Launchpad95_typed/*.py`
3. **Lint** — `uv run ruff check Launchpad95_typed/*.py`
4. **Format** — `uv run ruff format Launchpad95_typed/*.py`

## Notes

- The script targets all `.py` files in the `Launchpad95_typed/` directory.
