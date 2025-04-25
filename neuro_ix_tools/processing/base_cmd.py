"""Module defining abstract command class."""

import abc


class Command(abc.ABC):
    """Basic Command wrapper definition."""

    cmd: str

    def compile(self) -> str:
        """Create the final command to execute.

        Returns:
            str: Final command
        """
        return self.cmd
