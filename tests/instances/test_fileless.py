
import os
import pytest

from simexpal import util
from simexpal.base import Config
from simexpal.launch import common

file_dir = os.path.abspath(os.path.dirname(__file__))

valid_experiments_ymls = [('experiments_ymls/fileless/instance_filename.yml', ['fileless-instance'])
                          ]

invalid_experiments_ymls = [('experiments_ymls/fileless/instance.yml', "The instance 'fileless-instance' is fileless. Did you forget to remove the @INSTANCE@ variable in the argument list of the experiment?")
                            ]

@pytest.mark.parametrize('rel_yml_path, expected_output', valid_experiments_ymls)
def test_valid_fileless_experiments_yml(rel_yml_path, expected_output):
    rel_yml_dir = os.path.dirname(rel_yml_path)
    yml_dir = os.path.join(file_dir, rel_yml_dir)
    filename = os.path.basename(rel_yml_path)

    yml = util.validate_setup_file(yml_dir, filename, 'experiments.json')
    cfg = Config(yml_dir, yml)

    for run in cfg.discover_all_runs():
        if not common.lock_run(run):
            return
        common.create_run_file(run)

        manifest = common.compile_manifest(run)
        common.invoke_run(manifest)

        with open(run.output_file_path('out'), 'r') as output:
            actual_output = output.read().splitlines()
            assert expected_output == actual_output

@pytest.mark.parametrize('rel_yml_path, error_message', invalid_experiments_ymls)
def test_invalid_fileless_experiments_yml(rel_yml_path, error_message):
    rel_yml_dir = os.path.dirname(rel_yml_path)
    yml_dir = os.path.join(file_dir, rel_yml_dir)
    filename = os.path.basename(rel_yml_path)

    yml = util.validate_setup_file(yml_dir, filename, 'experiments.json')
    cfg = Config(yml_dir, yml)

    for run in cfg.discover_all_runs():
        if not common.lock_run(run):
            return
        common.create_run_file(run)

        manifest = common.compile_manifest(run)

        with pytest.raises(RuntimeError) as error:
            common.invoke_run(manifest)

        assert error_message == str(error.value)
