# Copilot Instructions for ctest-py

## Project Overview
- **ctest-py** is a Python package providing command-line utilities and functions, with a focus on type safety, documentation, and robust developer workflows. It shows how to integrate with c code from python.
- Main python code is in `src/ctest_py/`. Entry point is `ctest_py.__main__:main` (see `pyproject.toml`).
- Uses [Click](https://click.palletsprojects.com/) for CLI, Google-style docstrings for documentation, and Sphinx for docs generation.
- The c code is in `src/c/` and is built as a shared library that the python code interfaces with.
- The c code is built using CMake.

## Key Workflows
- **Build & Test:**
  - Use [Nox](https://nox.thea.codes/) for automation. Key sessions:
    - `nox -s pre-commit` — run all pre-commit hooks (lint, format, etc.)
    - `nox -s mypy` — type checking
    - `nox -s tests` — run test suite (pytest + coverage)
    - `nox -s typeguard` — runtime type checks
    - `nox -s xdoctest` — run docstring examples
    - `nox -s docs-build` — build documentation
    - `nox -s docs` — serve docs with live reload
- **Manual test:**
  - Run CLI: `python -m ctest_py` or `ctest-py` (if installed)

## Patterns & Conventions
- **Source Layout:**
  - All code in `src/ctest_py/`. Tests in `tests/`. Docs in `docs/`.
  - Functions use Google-style docstrings with doctest examples.
  - CLI defined in `__main__.py` using Click.
- **Type Safety:**
  - All public functions are type-annotated. Type checking via Nox/mypy.
- **Linting & Formatting:**
  - Uses Black and Ruff (see `pyproject.toml` and Nox).
  - Pre-commit hooks managed via Nox and `pre-commit`.
- **Testing:**
  - Pytest for unit tests. Coverage via `coverage` package.
  - Doctest examples in docstrings validated via xdoctest.
- **Documentation:**
  - Sphinx with autodoc, typehints, click, and myst-parser extensions.
  - Build docs: `nox -s docs-build`. Serve docs: `nox -s docs`.

## Integration Points
- **External Dependencies:**
  - Click (CLI), Black/Ruff (lint/format), Sphinx (docs), pytest/coverage (tests), typeguard, xdoctest.
- **Pre-commit:**
  - Hooks are patched to use the Nox virtualenv (see `noxfile.py`).
- **PyPI:**
  - Install via `pip install ctest-py`.

## Examples
- See `src/ctest_py/functions.py` for function patterns and docstring style.
- See `tests/test_functions.py` for test structure.
- See `noxfile.py` for all automation workflows.

## Quickstart for AI Agents
- Use Nox for all dev tasks: lint, type-check, test, docs.
- Follow Google-style docstrings and type hints for new code.
- Place new code in `src/ctest_py/`, tests in `tests/`, docs in `docs/`.
- Reference `noxfile.py` for session details and conventions.

---
If any section is unclear or missing important project-specific details, please provide feedback to improve these instructions.
