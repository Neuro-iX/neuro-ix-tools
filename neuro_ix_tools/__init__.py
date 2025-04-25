"""Define Base CLI, import commands from sub-modules."""

import logging
import os

import click
from rich.logging import RichHandler

from neuro_ix_tools import config
from neuro_ix_tools.processing import freesurfer_cli


@click.group()
def cli():
    """Define main CLI entrypoint."""
    logging.basicConfig(
        level="INFO", handlers=[RichHandler()], format="%(message)s", datefmt="[%X]"
    )


@cli.command()
def init():
    """Initialize environment variables"""
    click.echo(f"This is going to create a configuration file at {config.CONFIG_FILE}")
    if os.path.exists(config.CONFIG_FILE):
        click.secho(
            "This file already exists, it will be overridden. ", bold=True, fg="red"
        )
    click.confirm("Do you want to continue?", abort=True)

    path_to_freesurfer = click.prompt(
        "Enter path to freesurfer Apptainer file",
        default="~/projects/def-sbouix/software/Freesurfer7.4.1_container/fs741.sif",
    )
    default_slurm = click.prompt("Enter slurm account", default="ctb-sbouix")
    path_to_logs_freesurfer = click.prompt(
        "Enter path to freesurfer SLURM logs", default="~/freesurfer_pipeline/logs/"
    )

    os.makedirs(os.path.dirname(config.CONFIG_FILE), exist_ok=True)
    with open(config.CONFIG_FILE, "w+", encoding="utf-8") as file:
        file.write(
            f""" 
PATH_FREESURFER_SIF={path_to_freesurfer}
DEFAULT_SLURM_ACCOUNT={default_slurm}
FREESURFER_LOGS=~{path_to_logs_freesurfer}
"""
        )
    click.secho("Done !", bold=True, fg="green")


cli.add_command(freesurfer_cli)
