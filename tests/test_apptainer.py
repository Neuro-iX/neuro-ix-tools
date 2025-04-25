import subprocess

import pytest

from neuro_ix_tools.processing.apptainer import ApptainerEnv


@pytest.fixture()
def fs_container():
    return ApptainerEnv.freesurfer()


def test_apptainer_bind(fs_container):
    fs_container.bind("origin_dir/ds", "destination_dir/ds/mnt")
    command = fs_container.compile()

    assert "--bind origin_dir/ds:destination_dir/ds/mnt" in command


def test_apptainer_add_command(fs_container):
    fs_container.add_command("echo 'here'")
    command = fs_container.compile()

    assert "echo 'here'" in command


def test_apptainer_run(fs_container):
    fs_container.bind("tests/data/apptainer_test/", "/mnt/test_dir")
    fs_container.add_command("cat /mnt/test_dir/test_file.txt")
    command = fs_container.compile()

    out = subprocess.check_output(command, shell=True)
    out_str = out.decode("utf-8")
    assert out_str == "Check Apptainer bind and command"
