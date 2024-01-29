
import os
import pytest

from simexpal import base
from simexpal.launch.fork import ForkLauncher

file_dir = os.path.abspath(os.path.dirname(__file__))

yml_dirs = ['/experiments_ymls/missing_program']

valid_experiments = ['../../examples/sorting',
                     '../../examples/sorting_cpp',
                     '../../examples/sorting_fileless',
                     '../../examples/download_instances'
                     ]

invalid_experiments = [('experiments_ymls/undefined_axes', 'Axis block.size does not exist'),
                       ('experiments_ymls/undefined_variant', 'Variant undefined-variant does not exist')
                       ]

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

@pytest.mark.parametrize('rel_exp_path', valid_experiments)
def test_valid_experiments(rel_exp_path):
    experiments_dir = os.path.join(file_dir, rel_exp_path)
    cfg = base.config_for_dir(experiments_dir)

    assert isinstance(cfg, base.Config)

@pytest.mark.parametrize('rel_exp_path, error_message', invalid_experiments)
def test_invalid_experiments(rel_exp_path, error_message):
    experiments_dir = os.path.join(file_dir, rel_exp_path)
    cfg = base.config_for_dir(experiments_dir)

    assert isinstance(cfg, base.Config)

    with pytest.raises(RuntimeError) as error:
        a = list(cfg.discover_all_runs())

    assert error_message == str(error.value)
