"""Define Base CLI, import commands from sub-modules."""

import logging
import click
from src.commands import freesurfer_cli
from rich.logging import RichHandler


@click.group()
def cli():
    """Define main CLI entrypoint."""


if __name__ == "__main__":
    cli.add_command(freesurfer_cli)
    logging.basicConfig(
        level="INFO", handlers=[RichHandler()], format="%(message)s", datefmt="[%X]"
    )
    cli()
