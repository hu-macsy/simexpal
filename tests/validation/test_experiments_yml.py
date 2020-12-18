
import os
import pytest

from simexpal import util

file_dir = os.path.abspath(os.path.dirname(__file__))
valid_experiments_ymls = ['/../../examples/sorting/experiments.yml',
                          '/../../examples/sorting_cpp/experiments.yml',
                          '/../../examples/download_instances/experiments.yml',
                          '/experiments_ymls/valid/instances/extra_args.yml']

invalid_experiments_ymls = ['/experiments_ymls/invalid/top_level-additional_property.yml',
                            '/experiments_ymls/invalid/repo-invalid_value.yml']

@pytest.mark.parametrize('rel_yml_path', valid_experiments_ymls)
def test_valid_experiments_yml(rel_yml_path):
    ret_val = util.validate_setup_file(file_dir + rel_yml_path)

    assert isinstance(ret_val, dict)
    assert 'instdir' in ret_val

@pytest.mark.parametrize('rel_yml_path', invalid_experiments_ymls)
def test_invalid_experiments_yml(rel_yml_path):
    with pytest.raises(SystemExit) as info:
        util.validate_setup_file(file_dir + rel_yml_path)

    assert info.value.code == 1
