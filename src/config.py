"""Module retrieving necessary env variable and storing them as constants."""

import os

import dotenv

dotenv.load_dotenv()

PATH_FREESURFER_SIF = os.getenv("PATH_FREESURFER_SIF")
DEFAULT_SLURM_ACCOUNT = os.getenv("DEFAULT_SLURM_ACCOUNT")
FREESURFER_LOGS = os.getenv("FREESURFER_LOGS", "~/freesurfer_pipeline/logs/")
