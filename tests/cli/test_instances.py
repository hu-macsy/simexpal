
import os
import pytest
import subprocess

file_dir = os.path.abspath(os.path.dirname(__file__))

@pytest.mark.parametrize('rel_yml_path',
                         ['/../../examples/sorting/'])
def test_simex_i_install(rel_yml_path):
    cwd = file_dir + rel_yml_path
    ret_code = subprocess.check_call(['simex', 'i', 'install'], cwd=cwd)

    assert ret_code == 0
