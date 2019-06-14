
import os
import subprocess
import sys
import tempfile
import yaml

from .. import util
from . import common

script_template='''#!/bin/sh
@SIMEX@ internal-invoke --slurm @SPECFILE@
'''

class SlurmLauncher(common.Launcher):
	def __init__(self, queue):
		self.queue = queue

	def submit(self, cfg, run):
		self._do_submit(cfg, run)

	def _do_submit(self, cfg, r):
		util.try_mkdir(os.path.join(cfg.basedir, 'aux'))
		util.try_mkdir(os.path.join(cfg.basedir, 'aux/_slurm'))

		# Build the specfile.
		specs = common.compile_manifest(r).yml

		(specfd, specfile) = tempfile.mkstemp(prefix='', suffix='-spec.yml',
				dir=os.path.join(r.config.basedir, 'aux/_slurm'))
		with os.fdopen(specfd, 'w') as f:
			util.write_yaml_file(f, specs)

		# Expand the script that is passed to sbatch.
		def substitute(p):
			if p == 'SIMEX':
				return os.path.abspath(sys.argv[0])
			elif p == 'SPECFILE':
				return specfile
			else:
				return None

		sbatch_script = util.expand_at_params(script_template, substitute)

		# Build the sbatch command to run the script.
		# TODO: Support multiple queues
		sbatch_args = ['sbatch']
		sbatch_args.extend(['-o', os.path.join(cfg.basedir, 'aux/_slurm/%A.out'),
				'-e', os.path.join(cfg.basedir, 'aux/_slurm/%A.err')])

		# Finally start the run.
		if not common.lock_run(r):
			return
		locked = [r]
		print("Launching experiment '{}', instance '{}' on slurm queue '{}'".format(
				r.experiment.name, r.instance.filename, '?'))

		process = subprocess.Popen(sbatch_args, stdin=subprocess.PIPE);
		process.communicate(sbatch_script.encode()) # Assume UTF-8 encoding here.
		assert process.returncode == 0

		for run in locked:
			common.create_run_file(run)

