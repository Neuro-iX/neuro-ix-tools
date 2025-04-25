"""Module containing the logic to automate freesurfer jobs on Narval."""

import logging
import os
import shutil

from simple_slurm import Slurm

from src import config
from src.bids import BIDSDirectory
from src.commands.apptainer import ApptainerEnv
from src.commands.base_cmd import Command
from src.commands.slurm import get_apptainer_job


class FreeSurferReconAll(Command):
    """Object to wrap FreeSurfer's recon-all command."""

    def __init__(self, subject: str, path: str, subject_dir: str | None = None):
        """Initialize FreeSurfer recon-all command.

        Args:
        subject (str): Subject directory output name
        path (str): Path to the subject T1w volume
        subject_dir (str, optional): Directory for outputs. Defaults to None.
        """
        self.cmd = f"recon-all -all -s {subject} -i {path}"
        if subject_dir:
            self.cmd += f" -sd {subject_dir}"


class ApptainerFreesurfer(Command):
    """Object to control a freesurfer command inside an apptainer container."""

    def __init__(
        self, sub_id: str, ses_id: str, dataset: BIDSDirectory, subject_output: str
    ):
        """Initialize a Freesurfer command in an Apptainer container.

        Args:
            sub_id (str): subject to process
            ses_id (str): session to process
            dataset (BIDSDirectory): dataset containing the volume
            subject_output (str): final folder to store freesurfer outputs
        """
        # the directory where freesurfer will store results(needs to be unique)
        self.fs_dir = sub_id + ses_id
        self.sub_id = sub_id
        self.ses_id = ses_id

        t1_for_sub = dataset.get_all_t1w(sub_id, ses_id)
        assert len(t1_for_sub) == 1, (
            f"Wrong number of volumes for subject {sub_id} at session {ses_id}."
            f" Expected 1, found {len(t1_for_sub)}"
        )
        orig_volume_path = t1_for_sub[0]

        self.input_root = os.path.dirname(orig_volume_path)
        self.env_volume_path = os.path.join("/data", os.path.basename(orig_volume_path))
        # Creating an Apptainer Command to use freesurfer with apptainer
        self.apptainer_env = ApptainerEnv.freesurfer()
        self.apptainer_env.bind(subject_output, "/tmp")
        self.apptainer_env.bind(self.input_root, "/data")

        self.freesurfer_cmd = FreeSurferReconAll(
            self.fs_dir, self.env_volume_path, subject_dir="/tmp"
        )
        self.apptainer_env.add_command(self.freesurfer_cmd.compile())

    def compile(self) -> str:
        """Return command to execute as a string."""
        return self.apptainer_env.compile()

    def to_slurm(self) -> Slurm:
        """Wrap command in a Slurm job.

        Returns:
            Slurm: Ready to use Slurm job
        """
        output_slurm = os.path.join(
            config.FREESURFER_LOGS, f"freesurfer_{self.sub_id}_{self.ses_id}.%j.out"
        )

        assert config.DEFAULT_SLURM_ACCOUNT is not None, (
            "Missing default Slurm account (define env variable $DEFAULT_SLURM_ACCOUNT)"
        )
        job = get_apptainer_job(
            mem="30G",
            time="10:00:00",
            account=config.DEFAULT_SLURM_ACCOUNT,
            cpus=1,
            output=output_slurm,
        )

        job.add_cmd(self.compile())
        return job


def create_subject_directories(sub_id: str, ses_id: str, dataset: BIDSDirectory) -> str:
    """Create necessary output sub-folder structure in a `derivatives` folder.

    Args:
        sub_id (str): subject id
        ses_id (str): session id
        dataset (BIDSDirectory): dataset containing the volume

    Returns:
        str: path to the output dir
    """
    derivative_dir = os.path.join(dataset.dataset_path, "derivatives")
    os.makedirs(derivative_dir, exist_ok=True)
    sub_dir = os.path.join(derivative_dir, sub_id, ses_id)
    os.makedirs(sub_dir, exist_ok=True)
    return sub_dir


def cpy_cortical_stats_only(sub_dir: str, fs_dir: str, job: Slurm):
    """Modify job to only store freesurfer's stats files.

    It also creates a `stats` folder in the process
    Args:
        sub_dir (str): subject derivative output directory
        fs_dir (str): freesurfer output directory
            (Contains subject stats files)
        job (Slurm): job to modify
    """
    stat_dir = os.path.join(sub_dir, "stats")
    if os.path.exists(stat_dir):
        shutil.rmtree(stat_dir)
    os.makedirs(stat_dir)

    job.add_cmd(
        f"mv $SLURM_TMPDIR/{fs_dir}/stats/rh.aparc.stats \
              {os.path.join(stat_dir, 'rh.aparc.stats')}"
    )
    job.add_cmd(
        f"mv $SLURM_TMPDIR/{fs_dir}/stats/lh.aparc.stats \
              {os.path.join(stat_dir, 'lh.aparc.stats')}"
    )


def cpy_all(sub_dir: str, fs_dir: str, job: Slurm):
    """Modify job to copy freesurfer's output files.

    Args:
        sub_dir (str): subject derivative output directory
        fs_dir (str): freesurfer output directory
            (Contains subject stats files)
        job (Slurm): job to modify
    """
    job.add_cmd(
        f"mv $SLURM_TMPDIR/{fs_dir} \
              {sub_dir}/"
    )


def slurm_freesurfer_cortical_stats(
    sub_id: str, ses_id: str, dataset: BIDSDirectory
) -> Slurm:
    """Launch Slurm job to process one subject with freesurfer.

    Only keep cortical thickness stats.

    Args:
        sub_id (str): identifier of subject (with 'sub-')
        ses_id (str): identifier of session (with 'ses-')
        dataset (BIDSDirectoryDataset) : dataset object to retrieve pathes

    Returns:
        int: sbatch launch code
    """
    logging.info("Processing subject : %s", sub_id)

    # Creating an Apptainer Command to use freesurfer with apptainer
    apptainer_env = ApptainerFreesurfer(sub_id, ses_id, dataset, "$SLURM_TMPDIR")

    job = apptainer_env.to_slurm()

    # Create necessary directories
    sub_dir = create_subject_directories(sub_id, ses_id, dataset)

    # Copy cortical stats only
    cpy_cortical_stats_only(sub_dir, apptainer_env.fs_dir, job)

    return job


def slurm_freesurfer_all_results(
    sub_id: str, ses_id: str, dataset: BIDSDirectory
) -> Slurm:
    """Launch Slurm job to process one subject with freesurfer.

    Store every output files.

    Args:
        sub_id (str): identifier of subject (with 'sub-')
        ses_id (str): identifier of session (with 'ses-')
        dataset (BIDSDirectoryDataset) : dataset object to retrieve pathes

    Returns:
        int: sbatch launch code
    """
    logging.info("Processing subject : %s, session : %s", sub_id, ses_id)

    # Creating an Apptainer Command to use freesurfer with apptainer
    apptainer_env = ApptainerFreesurfer(sub_id, ses_id, dataset, "$SLURM_TMPDIR")

    job = apptainer_env.to_slurm()

    # Create necessary directories
    sub_dir = create_subject_directories(sub_id, ses_id, dataset)

    # Copy cortical stats only
    cpy_all(sub_dir, apptainer_env.fs_dir, job)

    return job
