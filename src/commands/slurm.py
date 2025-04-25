"""Module defining Slurm related utility."""

from simple_slurm import Slurm


def get_apptainer_job(
    mem: str, time: str, account: str, output: str, cpus: int = 1
) -> Slurm:
    """Create a Slurm job with apptainer activated.

    Args:
        mem (str): memory to allocate
        time (str): duration of task
        account (str): slurm account for ressources
        output (str): output path
        cpus (int, optional): number of cpu to allocate. Defaults to 1.

    Returns:
        Slurm: job with apptainer module activated
    """
    job = Slurm(
        cpus_per_task=cpus,
        mem=mem,
        account=account,
        time=time,
        output=output,
    )
    job.add_cmd("module load apptainer")

    return job
