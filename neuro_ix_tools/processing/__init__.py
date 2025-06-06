"""Module defining click commands."""

import os

import click

from neuro_ix_tools import config
from neuro_ix_tools.bids import BIDSDirectory, ClinicaDirectory
from neuro_ix_tools.processing.freesurfer import (
    slurm_freesurfer_all_results,
    slurm_freesurfer_cortical_stats,
)


@click.group("freesurfer")
def freesurfer_cli():
    """Freesurfer related commands."""


@freesurfer_cli.command()
@click.option(
    "-b",
    "--bids-dataset",
    help="absolute path to BIDS compliant dataset",
    type=str,
    default=None,
)
@click.option(
    "-c",
    "--clinica-dataset",
    help="absolute path to CLINICA compliant dataset",
    type=str,
    default=None,
)
@click.option(
    "--cortical-stats", help="only keep cortical stats", type=bool, is_flag=True
)
@click.option(
    "--start-from",
    type=int,
    default=0,
    help="Specify at which volume index should the processing start",
)
def recon_all(
    bids_dataset: str, clinica_dataset: str, cortical_stats: bool, start_from: int
):
    """Compute freesurfer recon-all."""
    assert (
        bids_dataset is not None or clinica_dataset is not None
    ), "One dataset path should be specified"
    assert (
        bids_dataset is None or clinica_dataset is None
    ), "Only one dataset path should be specified"

    if not os.path.exists(config.FREESURFER_LOGS):
        os.makedirs(config.FREESURFER_LOGS)

    if bids_dataset is not None:
        ds = BIDSDirectory(bids_dataset)
    else:
        ds = ClinicaDirectory(clinica_dataset)

    if cortical_stats:
        slurm_cmd = slurm_freesurfer_cortical_stats
    else:
        slurm_cmd = slurm_freesurfer_all_results
    sub_ses = list(ds.walk())
    for sub, ses in sub_ses[start_from:1000]:
        slurm_cmd(sub, ses, ds).sbatch()

    if len(sub_ses) > 1000:
        click.secho(
            (
                f"Dataset contain {len(sub_ses)} but only the first 1000 can be processed"
                "due to limits on slurm cluster jobs"
            ),
            color="red",
            bold=True,
        )
        click.secho(
            (
                "Once the jobs are finished, launch the same command with the argument"
                " : --start-from {start_from + 1000}"
            ),
            bold=True,
        )
