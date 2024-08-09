
import os
import json
import pytest
import subprocess

from simexpal import base
from simexpal import build
from simexpal import util

file_dir = os.path.abspath(os.path.dirname(__file__))
wanted_phases = [build.Phase.REGENERATE, build.Phase.COMPILE, build.Phase.CONFIGURE, build.Phase.INSTALL]
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

    check_cache_containment(wanted_cache_entries, vcs_less_build._cfg.basedir, 'main')

def test_simex_develop_build():
    cfg = base.config_for_dir(file_dir + '/experiments_ymls/build_examples/')
    
    def check_cache_containment(cache_entries, dir, build_name):
        assert os.path.isfile(os.path.join(dir, util.SIMEX_CACHE))
        with open(os.path.join(dir, util.SIMEX_CACHE), "r") as cachefile:
            cache = json.load(cachefile)
            for cache_entry in cache_entries:
                assert cache_entry in cache[build_name]
    
    test_instances = [('git-non-dev-gdsb', 'git-gdsb'), ('git-dev-gdsb', 'git-gdsb'), ('non-git-dev-cpp', 'non-git-cpp'), ('non-git-dev-py', 'non-git-py')]

    for rev_name, build_name in test_instances:
        revision = cfg.get_revision(rev_name)
        git_example = cfg.get_build(build_name, revision)
        build.make_builds(cfg, revision, [git_example.info], [build_name], wanted_phases)
        check_cache_containment(wanted_cache_entries, git_example._cfg.basedir, rev_name)    

