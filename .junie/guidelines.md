CTEST-PY project development guidelines (advanced)

This repository mixes a C library (curlcrypto) with Python bindings built via CFFI and scikit-build-core. The package import path `ctest_py` loads a compiled extension module (`_curlcrypto`) that must be built and present next to the pure-Python modules at runtime. Keep this in mind when running tests or interactive sessions — many operations require the native artifacts to be built/installed in the active environment first.

1. Build and configuration

- System dependencies (Linux/WSL):
  - Build toolchain: `cmake` (>= 3.28), `gcc`/`clang`, `make`, `pkg-config`.
  - Libraries: `libcurl4-openssl-dev`, `libssl-dev`.
  - Quick install on Ubuntu/WSL:
    - `sudo apt update`
    - `sudo apt install -y build-essential cmake pkg-config libcurl4-openssl-dev libssl-dev`

- System dependencies (macOS):
  - `brew install cmake openssl@3 curl pkg-config`
  - Ensure your compiler and CMake can find OpenSSL and libcurl; for local CMake runs you may need `export PKG_CONFIG_PATH="/opt/homebrew/opt/openssl@3/lib/pkgconfig:/opt/homebrew/opt/curl/lib/pkgconfig:$PKG_CONFIG_PATH"`.

- Windows notes:
  - Easiest route is to build under WSL (Ubuntu) with the Linux instructions above. Native Windows builds are possible but require a working MSVC toolchain and suitable libcurl/OpenSSL development packages (e.g., via vcpkg); that flow isn’t covered here.

- Python build backend: `scikit-build-core` (configured in `pyproject.toml`). CMake source root is `src/`. The build produces:
  - A shared library `libcurlcrypto.*` installed into the Python package directory `ctest_py/`.
  - A CPython extension module `_curlcrypto.*` built from CFFI-emitted C (`ctest_py/_build_cffi.py` → `_curlcrypto.c`) and linked against the `curlcrypto` library.

- Building C and running C tests (standalone CMake):
  - From project root:
    - `cd src`
    - `mkdir -p build && cd build`
    - `cmake .. -DBUILD_TESTING=ON`
    - `cmake --build . -j`  (add `--config Release` on multi-config generators)
    - `ctest -V`            (runs C tests: e.g., `curlcrypto_version_test`)
    - Install native artifacts into the package tree (useful for dev runs):
      - `cmake --install . --prefix ..`
    - This drops `libcurlcrypto.*` under `src/ctest_py/`.

- Building the Python package (and extension) with pip:
  - Create/activate a virtualenv (or use Poetry, see below).
  - `python -m pip install -U pip setuptools wheel`
  - Editable install (dev): `python -m pip install -e .`
    - This will invoke `scikit-build-core` to configure CMake and build both the C library and the `_curlcrypto` extension into your environment. After this, `import ctest_py` will work in that env.
  - Build artifacts: `python -m build` (requires `build` package, already declared in dev deps via Poetry). The wheel contains the compiled artifacts.

- Building/using Poetry:
  - `poetry install` sets up a dev environment with Python deps. It does not by itself run the native build.
  - Inside the Poetry venv, build and install the extension by running pip in that env:
    - `poetry run pip install -e .`
  - Alternatively, build a wheel and install it into the Poetry env:
    - `poetry run python -m build`
    - `poetry run pip install dist/*.whl`

2. Testing

- Test runner: `pytest` (configured in `pyproject.toml`), with `pythonpath = ["src"]` so tests can import the package when running from the repo root.

- Important: tests that import `ctest_py` will trigger import of the compiled `_curlcrypto` extension via `ctest_py/__init__.py`. Ensure the extension is built and installed in the active environment before running the full suite:
  - If you use Poetry: `poetry run pip install -e .` first.
  - If you use a raw venv: `python -m pip install -e .` first.
  - If you only want to run tests that don’t import the package (for quick checks), use `-k` selectors accordingly.

- Typical flows:
  - Quick run (current interpreter, with Poetry env):
    - `poetry run pytest -q`
  - Quick run (raw venv):
    - `pytest -q`
  - Verbose with coverage (uses coverage config in `pyproject.toml`):
    - `coverage run -m pytest -q`
    - `coverage report -m`  (threshold is `fail_under = 50` in config)

- Running a single test module or test:
  - `pytest -q tests/test_functions.py`
  - `pytest -q -k version` (by keyword expression)

- Adding new tests:
  - Place files under `tests/` with names `test_*.py`.
  - Prefer importing individual submodules that do not require the native layer when feasible for unit tests of pure-Python code. Anything that needs `_curlcrypto` should run after the native build is present in the environment.
  - Example minimal test file content:
    ```python
    # tests/test_example_minimal.py
    def test_minimal_math() -> None:
        assert 2 + 2 == 4
    ```
  - Run it: `pytest -q tests/test_example_minimal.py`.

- NOX-based multi-session testing (optional):
  - The nox tools `nox` and `nox-poetry` are installed globally and are in the path.
  - List sessions: `nox -l`
  - Run default sessions (pre-commit, mypy, tests, typeguard, xdoctest, docs-build): `nox`
  - Run only tests (in all configured Python versions available on your system): `nox -s tests-3.12`
    - The noxfile expects multiple interpreters (`3.10`–`3.13`) to be discoverable on PATH.
    - Only python 3.12 is installed in the current environment.


3. Additional development information

- Code style and static analysis:
  - Formatter: `black` (profile defaults; configured via Poetry dev deps). Run:
    - `black .` or `poetry run black .`
  - Linter: `ruff` with extensive rule selection; see `[tool.ruff]` in `pyproject.toml`. Run:
    - `ruff check .` (and optionally `--fix`), within the repo root.
  - Type checking: `mypy` is in strict mode (`[tool.mypy]`). Run:
    - `mypy src tests`
  - Import sorting: `ruff isort` rules are enabled; normal `ruff check` enforces them.
  - Dependency hygiene: `deptry` is included; run `deptry .` to detect unused/missing deps.

- Pre-commit hooks:
  - `pre-commit install` to set up Git hooks.
  - `pre-commit run -a` to run all hooks locally.
  - The nox session `pre-commit` can execute hooks in an isolated env.

- Documentation:
  - Sphinx docs live in `docs/`. Build locally with:
    - `poetry run sphinx-build -b html docs docs/_build/html`
    - Or via nox: `nox -s docs-build`

- CMake/scikit-build internals worth knowing:
  - CMake project is defined in `src/CMakeLists.txt`, adds the `c` subdirectory, finds Python (`Interpreter` and `Development.Module` components), emits the CFFI C source using `ctest_py/_build_cffi.py`, and builds the `_curlcrypto` extension with `Python_add_library(... WITH_SOABI ...)`.
  - At install time, both the shared lib and the extension are placed into the `ctest_py` package directory so the dynamic loader can resolve symbols at runtime (`$ORIGIN` rpath is set on UNIX-like systems).
  - If you install the C library separately via the standalone CMake flow, use `cmake --install . --prefix ..` from `src/build` so that artifacts land under `src/ctest_py/` for local development.

- Known pitfalls:
  - Importing `ctest_py` without the extension present will fail: ensure `pip install -e .` (or wheel install) has been done in your active environment.
  - On macOS with Homebrew OpenSSL, ensure `pkg-config` can locate OpenSSL; otherwise CMake will fail to configure.
  - On Windows, prefer WSL for a smoother toolchain setup unless you have a vcpkg/MSVC workflow ready.

4. Verified test invocation (demonstration)

- A minimal demonstration test (pure Python) was created and executed to validate the test process:
  - Content used:
    ```python
    def test_demo_temp() -> None:
        assert 2 + 2 == 4
    ```
  - Command executed: `python -m pytest -q tests/test_demo_temp.py`
  - Result: 1 passed.
  - The temporary file was removed after the run. Use the “Adding new tests” example above for your own tests.

5. Quick command reference

- Native + Python dev install (Poetry env):
  - `poetry install`
  - `poetry run pip install -e .`
  - `poetry run pytest -q`

- Native + Python dev install (raw venv):
  - `python -m pip install -e .`
  - `pytest -q`

- Standalone C build and test:
  - `cd src && cmake -S . -B build -DBUILD_TESTING=ON && cmake --build build -j && ctest --test-dir build -V && cmake --install build --prefix ..`

- Tooling:
  - `ruff check .` | `black .` | `mypy src tests` | `pre-commit run -a`
  - `nox -l` | `nox -s tests` | `nox -s pre-commit`
