import os
import pytest
import subprocess

file_dir = os.path.abspath(os.path.dirname(__file__))
yml_dirs = ['/../../examples/sorting/']  # List of directories that should be tested.


@pytest.mark.parametrize("launcher", ["fork", "slurm"])
@pytest.mark.parametrize("rel_yml_path", yml_dirs)
def test_simex_e_launch(launcher, rel_yml_path):
    # Make sure that the needed instances are installed.
    # The main test follows afterwards.
    cwd = file_dir + rel_yml_path
    ret_code = subprocess.check_call(["simex", "i", "install"], cwd=cwd)
    assert ret_code == 0

    ret_code = subprocess.check_call(
        ["simex", "e", "launch", f"--launch-through={launcher}"], cwd=cwd
    )

    assert ret_code == 0


@pytest.mark.parametrize("rel_yml_path", yml_dirs)
def test_simex_e_purge_all(rel_yml_path):
    cwd = file_dir + rel_yml_path
    ret_code = subprocess.check_call(['simex', 'e', 'purge', '--all', '-f'], cwd=cwd)

    assert ret_code == 0
