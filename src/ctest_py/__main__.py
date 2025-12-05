"""Command-line interface."""

import click


@click.command()
@click.version_option()
def main() -> None:
    """CTest Py."""


if __name__ == "__main__":
    main(prog_name="ctest-py")  # pragma: no cover
