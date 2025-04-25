import os
import re
import shutil

import pytest
from simple_slurm import Slurm

from src.bids import BIDSDirectory
from src.commands.freesurfer import (
    ApptainerFreesurfer,
    FreeSurferReconAll,
    cpy_all,
    cpy_cortical_stats_only,
    create_subject_directories,
    slurm_freesurfer_all_results,
    slurm_freesurfer_cortical_stats,
)


def test_freesurfer_recon_all():
    recon_all = FreeSurferReconAll(
        subject="sub-111", path="path/to/sub-111", subject_dir="/output/for/sub"
    )
    command = recon_all.compile()
    assert command == "recon-all -all -s sub-111 -i path/to/sub-111 -sd /output/for/sub"

    recon_all = FreeSurferReconAll(subject="sub-111", path="path/to/sub-111")
    command = recon_all.compile()
    assert command == "recon-all -all -s sub-111 -i path/to/sub-111"


@pytest.fixture()
def apptainer_fs():
    return ApptainerFreesurfer(
        "sub-000103",
        "ses-standard",
        BIDSDirectory("tests/data/bids_sub_ses"),
        "test_outputs",
    )


@pytest.fixture()
def ds():
    return BIDSDirectory("tests/data/bids_sub_ses")


def test_apptainer_freesurfer_compile(apptainer_fs: ApptainerFreesurfer):
    command = apptainer_fs.compile()
    fs_command = apptainer_fs.freesurfer_cmd.compile()
    assert fs_command in command
    assert (
        "--bind tests/data/bids_sub_ses/sub-000103/ses-standard/anat:/data" in command
    )
    assert "--bind test_outputs:/tmp" in command


def test_apptainer_freesurfer_to_slurm(apptainer_fs: ApptainerFreesurfer):
    job = apptainer_fs.to_slurm()
    command = apptainer_fs.compile()

    assert isinstance(job, Slurm)
    assert command in str(job)


def test_create_subject_directories(ds):
    sub_dir = create_subject_directories("sub-000103", "ses-standard", ds)

    assert os.path.exists("tests/data/bids_sub_ses/derivatives")
    assert os.path.exists("tests/data/bids_sub_ses/derivatives/sub-000103")
    assert os.path.exists("tests/data/bids_sub_ses/derivatives/sub-000103/ses-standard")
    assert sub_dir == "tests/data/bids_sub_ses/derivatives/sub-000103/ses-standard"

    shutil.rmtree("tests/data/bids_sub_ses/derivatives")


def test_cpy_cortical_stats_only(apptainer_fs: ApptainerFreesurfer, ds):
    job = apptainer_fs.to_slurm()
    create_subject_directories("sub-000103", "ses-standard", ds)

    cpy_cortical_stats_only(
        "tests/data/bids_sub_ses/derivatives/sub-000103/ses-standard", "test_fsdir", job
    )

    assert os.path.exists(
        "tests/data/bids_sub_ses/derivatives/sub-000103/ses-standard/stats"
    )
    match = re.search(
        r"mv \\\$SLURM_TMPDIR\/test_fsdir\/stats\/rh\.aparc\.stats.*tests\/data\/bids_sub_ses\/derivatives\/sub-000103\/ses-standard\/stats\/rh\.aparc\.stats",
        str(job),
    )
    assert match is not None

    shutil.rmtree("tests/data/bids_sub_ses/derivatives")


def test_cpy_cortical_stats_only_auto_rm(apptainer_fs: ApptainerFreesurfer, ds):
    job = apptainer_fs.to_slurm()
    create_subject_directories("sub-000103", "ses-standard", ds)

    os.makedirs("tests/data/bids_sub_ses/derivatives/sub-000103/ses-standard/stats")
    cpy_cortical_stats_only(
        "tests/data/bids_sub_ses/derivatives/sub-000103/ses-standard", "test_fsdir", job
    )

    assert os.path.exists(
        "tests/data/bids_sub_ses/derivatives/sub-000103/ses-standard/stats"
    )
    match = re.search(
        r"mv \\\$SLURM_TMPDIR\/test_fsdir\/stats\/rh\.aparc\.stats.*tests\/data\/bids_sub_ses\/derivatives\/sub-000103\/ses-standard\/stats\/rh\.aparc\.stats",
        str(job),
    )
    assert match is not None

    shutil.rmtree("tests/data/bids_sub_ses/derivatives")


def test_cpy_all(apptainer_fs: ApptainerFreesurfer, ds):
    job = apptainer_fs.to_slurm()
    create_subject_directories("sub-000103", "ses-standard", ds)

    cpy_all(
        "tests/data/bids_sub_ses/derivatives/sub-000103/ses-standard", "test_fsdir", job
    )

    match = re.search(
        r"mv \\\$SLURM_TMPDIR\/test_fsdir.*tests\/data\/bids_sub_ses\/derivatives\/sub-000103\/ses-standard\/",
        str(job),
    )
    assert match is not None

    shutil.rmtree("tests/data/bids_sub_ses/derivatives")


def test_slurm_freesurfer_cortical_stats(ds):
    job = slurm_freesurfer_cortical_stats("sub-000103", "ses-standard", ds)
    assert isinstance(job, Slurm)


def test_slurm_freesurfer_all_results(ds):
    job = slurm_freesurfer_all_results("sub-000103", "ses-standard", ds)
    assert isinstance(job, Slurm)
