
import os
import shutil
import json
import pytest

from simexpal import base
from simexpal import build
from simexpal import util

file_dir = os.path.abspath(os.path.dirname(__file__))
wanted_phases = [build.Phase.CHECKOUT, build.Phase.REGENERATE, build.Phase.COMPILE, build.Phase.CONFIGURE, build.Phase.INSTALL]
wanted_cache_entries = [util.REGENERATED, util.COMPILED, util.CONFIGURED, util.INSTALLED]

def test_simex_d_vcs_less():
    cfg = base.config_for_dir(file_dir + '/experiments_ymls/vcs_less/')

    revision = cfg.get_revision('main')
    vcs_less_build = cfg.get_build('vcs-less', revision)

    build.make_builds(cfg, revision, [vcs_less_build.info], ['main'], wanted_phases)

    def check_cache_containment(cache_entries, dir, build_name):
        assert os.path.isfile(os.path.join(dir, util.SIMEX_CACHE))
        with open(os.path.join(dir, util.SIMEX_CACHE), "r") as cachefile:
            cache = json.load(cachefile)
            for cache_entry in cache_entries:
                assert cache_entry in cache[build_name]

    check_cache_containment(wanted_cache_entries, vcs_less_build._cfg.basedir, 'vcs-less')

def test_simex_builds():
    cfg = base.config_for_dir(file_dir + '/experiments_ymls/build_examples/')
    
    def check_cache_containment(cache_entries, dir, build_name):
        assert os.path.isfile(os.path.join(dir, util.SIMEX_CACHE))
        with open(os.path.join(dir, util.SIMEX_CACHE), "r") as cachefile:
            cache = json.load(cachefile)
            for cache_entry in cache_entries:
                assert cache_entry in cache[build_name]

    test_instances = [(b.revision.name, b.name) for b in cfg.all_builds()]

    for rev_name, build_name in test_instances:
        revision = cfg.get_revision(rev_name)
        example_build = cfg.get_build(build_name, revision)
        build.make_builds(cfg, revision, [example_build.info], [build_name], wanted_phases)
        check_cache_containment(wanted_cache_entries, example_build._cfg.basedir, build_name)

# pytest runs this function first, then on yield runs all tests, then finally runs the code following 'yield' (as cleanup/finalize)
@pytest.fixture(scope='session', autouse=True)
def cleanup_build_files():
    def try_delete(path):
        try:
            shutil.rmtree(path)
        except FileNotFoundError:
            pass
    
    yield 
    print('removing', f"{file_dir}/experiments_ymls/build_examples/builds")
    try_delete(f"{file_dir}/experiments_ymls/build_examples/builds")
    try_delete(f"{file_dir}/experiments_ymls/build_examples/dev-builds")
    try_delete(f"{file_dir}/experiments_ymls/build_examples/develop")
    try_delete(f"{file_dir}/experiments_ymls/build_examples/bin")
    try:
        os.remove(f"{file_dir}/experiments_ymls/build_examples/.simex.cache")
    except FileNotFoundError:
        pass
