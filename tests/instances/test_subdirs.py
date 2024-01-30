
import os

from simexpal import base

file_dir = os.path.abspath(os.path.dirname(__file__))

def test_experiments_missing_program():
    cfg = base.config_for_dir(file_dir + '/experiments_ymls/subdir/')

    # Make sure that the needed instances are installed.
    for instance in cfg.all_instances():
        assert instance.check_available()
