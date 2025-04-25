"""Helper classes and function to iterate through BIDS and Clinica dataset."""

import glob
import os
import re
from typing import Generator


class BIDSDirectory:
    """Utility to query BIDS directories."""

    has_session: bool = False
    has_sites: bool = False
    sites: list[str] | None = None

    def __init__(self, dataset_path: str):
        """Initialize a directory.

        Args:
        dataset (str): Dataset directory name
        root_dir (str): Root directory for all datasets
        """
        self.dataset_path = dataset_path

        self.has_session = len(glob.glob("sub-*/ses-*", root_dir=self.dataset_path)) > 0

    def get_subjects(self) -> list[str]:
        """Retrieve list of all subjects.

        Returns:
            list[str]: list of all subjects
        """
        return glob.glob("sub-*", root_dir=self.dataset_path)

    def get_sessions(self, sub_id: str) -> list[str]:
        """Retrieve list of sessions.

        Args:
            sub_id (str): Subject id (sub-???)
        Returns:
            list[str]: list of sessions
        """
        return glob.glob("ses-*", root_dir=os.path.join(self.dataset_path, sub_id))

    def walk(self) -> Generator[tuple[str, ...], None, None]:
        """Iterate over every subjects, session and generation of the dataset.

        Yields:
            Generator[tuple[str, ...], None, None]: sub_id, ses_id
        """
        for sub in self.get_subjects():
            if self.has_session:
                for ses in self.get_sessions(sub):
                    yield sub, ses
            else:
                yield (sub,)

    def get_all_t1w(self, sub_id: str, ses_id: str | None = None) -> list[str]:
        """Return path to all T1w volumes.

        Args:
            sub_id (str): Subject id (sub-???)
            ses_id (str, optional): Session id (ses-???). Defaults to None.

        Returns:
            list[str] : Path to all T1w
        """
        if ses_id is not None:
            return glob.glob(
                os.path.join(self.dataset_path, sub_id, ses_id, "anat", "*T1w.nii.gz")
            )
        return glob.glob(os.path.join(self.dataset_path, sub_id, "anat", "*T1w.nii.gz"))

    def extract_sub_ses(self, path: str) -> tuple[str | None, str | None]:
        """Extract subject and session identifier from path.

        Args:
            path (str): path to NifTi file

        Returns:
            tuple[str | None, str | None]: sub-id, ses-id
        """
        sub = None
        ses = None

        req_sub = r".*(sub-[\dA-Za-z]*).*"
        req_ses = r".*(ses-[\dA-Za-z]*).*"
        match_sub = re.match(req_sub, path)
        match_ses = re.match(req_ses, path)

        if match_sub is not None:
            groups = match_sub.groups()
            sub = groups[0]

        if match_ses is not None:
            groups = match_ses.groups()
            ses = groups[0]
        return sub, ses

    def __len__(self):
        """Return len of available T1w volumes."""
        return len(list(self.walk()))


class ClinicaDirectory(BIDSDirectory):
    """Utility class to query Clinica processed directory."""

    def __init__(self, dataset_path: str):
        """Initialize a Clinica directory.

        Args:
        dataset (str): Dataset directory name
        root_dir (str): Root directory for all datasets
        """
        super().__init__(dataset_path)
        self.base_path = os.path.join(self.dataset_path, "subjects")

        # Clinica datasets necessarily have session because clinica will not process
        # a bids datset without it
        self.has_session = len(glob.glob("sub-*/ses-*", root_dir=self.dataset_path)) > 0
        assert self.has_session, "Clinica datasets should have sessions"

    def get_all_t1w(self, sub_id: str, ses_id: str = "ses-1") -> list[str]:
        """Return path to T1w volume.

        Args:
            sub_id (str): Subject id (sub-???)
            ses_id (str, optional): Session id (ses-???). Defaults to "ses-1".
            gen_id : Ignores
        Returns:
            str: Path to T1w
        """
        return glob.glob(
            os.path.join(
                self.dataset_path,
                sub_id,
                ses_id,
                "t1_linear",
                "*space-MNI152NLin2009cSym_res-1x1x1_T1w.nii.gz",
            )
        )
