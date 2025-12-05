# CTest Py

[![PyPI](https://img.shields.io/pypi/v/ctest-py.svg)][pypi status]
[![Status](https://img.shields.io/pypi/status/ctest-py.svg)][pypi status]
[![Python Version](https://img.shields.io/pypi/pyversions/ctest-py)][pypi status]
[![License](https://img.shields.io/pypi/l/ctest-py)][license]

[![Documentation](https://github.com/arneso-ssb/ctest-py/actions/workflows/docs.yml/badge.svg)][documentation]
[![Tests](https://github.com/arneso-ssb/ctest-py/actions/workflows/tests.yml/badge.svg)][tests]
[![Coverage](https://sonarcloud.io/api/project_badges/measure?project=arneso-ssb_ctest-py&metric=coverage)][sonarcov]
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=arneso-ssb_ctest-py&metric=alert_status)][sonarquality]

[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)][pre-commit]
[![Black](https://img.shields.io/badge/code%20style-black-000000.svg)][black]
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Poetry](https://img.shields.io/endpoint?url=https://python-poetry.org/badge/v0.json)][poetry]

[pypi status]: https://pypi.org/project/ctest-py/
[documentation]: https://arneso-ssb.github.io/ctest-py
[tests]: https://github.com/arneso-ssb/ctest-py/actions?workflow=Tests
[sonarcov]: https://sonarcloud.io/summary/overall?id=arneso-ssb_ctest-py
[sonarquality]: https://sonarcloud.io/summary/overall?id=arneso-ssb_ctest-py
[pre-commit]: https://github.com/pre-commit/pre-commit
[black]: https://github.com/psf/black
[poetry]: https://python-poetry.org/

## Features

- TODO

## Requirements

- Curl and openssh libraries must be installed.

## Installation

You can install _CTest Py_ via [pip] from [PyPI]:

```console
pip install ctest-py
```

## Usage

Please see the [Reference Guide] for details.

## Contributing

Contributions are very welcome.
To learn more, see the [Contributor Guide].

## License

Distributed under the terms of the [MIT license][license],
_CTest Py_ is free and open source software.

## Issues

If you encounter any problems,
please [file an issue] along with a detailed description.

## Developer

Use the following commands to build, run and test the c-part of the library:

```shell
cd src
mkdir build && cd build
cmake .. -DBUILD_TESTING=ON
cmake --build .
ctest -V
cmake --install . --prefix ..
```

If you geet errors about missing developement libraries for curl and openssh, you can
install them like this:

```shell
sudo apt install libcurl4-openssl-dev
sudo apt install libssl-dev
```

## Credits

This project was generated from [Statistics Norway]'s [SSB PyPI Template].

[statistics norway]: https://www.ssb.no/en
[pypi]: https://pypi.org/
[ssb pypi template]: https://github.com/statisticsnorway/ssb-pypitemplate
[file an issue]: https://github.com/arneso-ssb/ctest-py/issues
[pip]: https://pip.pypa.io/

<!-- github-only -->

[license]: https://github.com/arneso-ssb/ctest-py/blob/main/LICENSE
[contributor guide]: https://github.com/arneso-ssb/ctest-py/blob/main/CONTRIBUTING.md
[reference guide]: https://arneso-ssb.github.io/ctest-py/reference.html
