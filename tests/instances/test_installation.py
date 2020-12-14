
import os
import pytest
from simexpal import base

file_dir = os.path.abspath(os.path.dirname(__file__))

yml_dirs = ['/experiments_ymls/snap/',
            '/experiments_ymls/url/',
            '/experiments_ymls/git/']

@pytest.mark.parametrize('rel_yml_path', yml_dirs)
def test_download(rel_yml_path):
    cfg = base.config_for_dir(file_dir + rel_yml_path)

    for instance in cfg.all_instances():
        instance.install()

        assert instance.check_available()
        assert os.path.getsize(instance.fullpath) > 0
