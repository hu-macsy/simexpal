
import os
import pytest

from simexpal import base
from simexpal.launch.fork import ForkLauncher

file_dir = os.path.abspath(os.path.dirname(__file__))

yml_dirs = ['/experiments_ymls/missing_program']

@pytest.mark.parametrize('rel_yml_path', yml_dirs)
def test_experiments_missing_program(rel_yml_path):
    cfg = base.config_for_dir(file_dir + rel_yml_path)

    # Make sure that the needed instances are installed.
    # The main test follows afterwards.
    for instance in cfg.all_instances():
        instance.install()

        assert instance.check_available()

    launcher = ForkLauncher()
    for run in cfg.discover_all_runs():
        launcher.submit(cfg, run)

        assert run.get_status() == base.Status.FAILED
        assert os.path.getsize(run.aux_file_path('stderr'))
