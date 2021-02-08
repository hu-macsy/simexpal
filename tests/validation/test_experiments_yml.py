
import os
import pytest

from simexpal import util

file_dir = os.path.abspath(os.path.dirname(__file__))

valid_experiments_ymls = ['../../examples/sorting/experiments.yml',
                          '../../examples/sorting_cpp/experiments.yml',
                          '../../examples/download_instances/experiments.yml',
                          'experiments_ymls/valid/instances/extra_args.yml',
                          'experiments_ymls/valid/variants/enum.yml',
                          'experiments_ymls/valid/variants/range.yml']

invalid_experiments_ymls = ['experiments_ymls/invalid/top_level-additional_property.yml',
                            'experiments_ymls/invalid/instances/repo-invalid_value.yml',
                            'experiments_ymls/invalid/variants/enum_additional_property.yml',
                            'experiments_ymls/invalid/variants/range_additional_property.yml',
                            'experiments_ymls/invalid/variants/range_str_list.yml',
                            'experiments_ymls/invalid/variants/steps_str_value.yml'
                            ]

@pytest.mark.parametrize('rel_yml_path', valid_experiments_ymls)
def test_valid_experiments_yml(rel_yml_path):
    rel_yml_dir = os.path.dirname(rel_yml_path)
    yml_dir = os.path.join(file_dir, rel_yml_dir)
    filename = os.path.basename(rel_yml_path)

    ret_val = util.validate_setup_file(yml_dir, filename, 'experiments.json')

    assert isinstance(ret_val, dict)

@pytest.mark.parametrize('rel_yml_path', invalid_experiments_ymls)
def test_invalid_experiments_yml(rel_yml_path):
    rel_yml_dir = os.path.dirname(rel_yml_path)
    yml_dir = os.path.join(file_dir, rel_yml_dir)
    filename = os.path.basename(rel_yml_path)

    with pytest.raises(SystemExit) as info:
        util.validate_setup_file(yml_dir, filename, 'experiments.json')

    assert info.value.code == 1
