
import os

from simexpal import base
from simexpal import build

file_dir = os.path.abspath(os.path.dirname(__file__))

def test_simex_d_vcs_less():
    cfg = base.config_for_dir(file_dir + '/experiments_ymls/vcs_less/')

    revision = cfg.get_revision('main')
    vcs_less_build = cfg.get_build('vcs-less', revision)

    # Passing None for args is fine since it's properties are not used for vcs-less builds
    build.make_builds(None, cfg, revision, [vcs_less_build.info], ['vcs-less'], [build.Phase.INSTALL])

    def check_files_in_dir(files, dir):
        for file_name in files:
            assert os.path.isfile(dir + file_name)

    source_dir_files = ['/regenerated',
                        '/regenerated.simexpal']
    check_files_in_dir(source_dir_files, vcs_less_build.source_dir)

    compile_dir_files = ['/configured',
                         '/configured.simexpal',
                         '/compiled',
                         '/compiled.simexpal',
                         '/installed']
    check_files_in_dir(compile_dir_files, vcs_less_build.compile_dir)

    prefix_dir_files = ['/installed.simexpal']
    check_files_in_dir(prefix_dir_files, vcs_less_build.prefix_dir)
