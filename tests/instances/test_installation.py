
import os
import pytest
from simexpal import base

file_dir = os.path.abspath(os.path.dirname(__file__))

yml_dirs = ['/experiments_ymls/snap/',
            '/experiments_ymls/url/',
            '/experiments_ymls/git/',
            '/experiments_ymls/postprocess/']

@pytest.mark.parametrize('rel_yml_path', yml_dirs)
def test_download(rel_yml_path):
    cfg = base.config_for_dir(file_dir + rel_yml_path)

    for instance in cfg.all_instances():
        instance.install()

        assert instance.check_available()

        if 'postprocess' in instance._inst_yml:
            instance_dir = instance.config.instance_dir()

            assert os.path.isfile(os.path.join(instance_dir, instance.yml_name) + '.postprocessed')

            for file in instance.filenames:
                assert os.path.isfile(os.path.join(instance_dir, file + '.original'))
