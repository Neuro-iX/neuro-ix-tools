"""Module retrieving necessary env variable and storing them as constants."""

import logging
import os

import dotenv
from platformdirs import user_config_dir

dotenv.load_dotenv()

CONFIG_FILE = os.path.join(user_config_dir("neuro-ix-tools"), "config.env")

if os.path.exists(".env"):
    dotenv.load_dotenv()
else:
    if os.path.exists(CONFIG_FILE):
        dotenv.load_dotenv(CONFIG_FILE)
    else:
        logging.warning("No config found at %s",CONFIG_FILE)

PATH_FREESURFER_SIF = os.getenv("PATH_FREESURFER_SIF")
DEFAULT_SLURM_ACCOUNT = os.getenv("DEFAULT_SLURM_ACCOUNT")
FREESURFER_LOGS = os.getenv("FREESURFER_LOGS", "~/freesurfer_pipeline/logs/")
