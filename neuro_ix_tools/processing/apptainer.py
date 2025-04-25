"""Module to use Apptainer containers."""

import logging

from neuro_ix_tools import config
from neuro_ix_tools.processing.base_cmd import Command


class ApptainerEnv(Command):
    """Command object to use apptainer wrapped commands."""

    def __init__(self, sif_file: str):
        """Initialize an Apptainer environment.

        Args:
        sif_file (str): Path to SIF container
        """
        self.sif_file = sif_file
        self.bind_pairs: list[tuple[str, str]] = []
        self.commands: list[str] = []
        self.cmd = "apptainer run "

    def bind(self, orig: str, mnt: str):
        """Bind folders to apptainer env.

        Args:
            orig (str): Directory path in normal environment
            mnt (str): Directory path to use in apptainer
        """
        self.bind_pairs.append((orig, mnt))

    def add_command(self, command: str):
        """Add a command to run in apptainer (FIFO).

        Args:
            command (str): commands to add
        """
        self.commands.append(command)

    def compile(self) -> str:
        """Create the final command to execute.

        Returns:
            str: Final command
        """
        cmd = self.cmd
        for pair in self.bind_pairs:
            cmd += f"--bind {pair[0]}:{pair[1]} "
        cmd += self.sif_file
        cmd += ' bash -c "'
        for command in self.commands:
            cmd += f"{command};"
        cmd += '"'
        logging.info(cmd)
        return cmd

    @staticmethod
    def freesurfer() -> "ApptainerEnv":
        """Use config.PATH_FREESURFER_SIF.

        Returns:
            ApptainerEnv: Environement for free surfer container
        """
        assert config.PATH_FREESURFER_SIF is not None, "No path to freesurfer defined"
        return ApptainerEnv(config.PATH_FREESURFER_SIF)
