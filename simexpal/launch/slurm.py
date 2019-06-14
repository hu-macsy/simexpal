
import os
import subprocess
import sys
import tempfile
import yaml

from .. import util
from . import common

template='''#!/bin/sh
@SIMEX@ -C '@CONFIG_DIR@' internal-invoke --experiment @EXPERIMENT@ --instance @INSTANCE@ --repetition @REP@
'''

class SlurmLauncher(common.Launcher):
	def __init__(self, queue):
		self.queue = queue

	def submit(self, cfg, run):
		self._do_submit(cfg, run)

	def _do_submit(self, cfg, r):
		util.try_mkdir(os.path.join(cfg.basedir, 'aux'))
		util.try_mkdir(os.path.join(cfg.basedir, 'aux/_slurm'))

		def substitute(p):
			if p == 'SIMEX':
				return os.path.abspath(sys.argv[0])
			elif p == 'CONFIG_DIR':
				return cfg.basedir
			elif p == 'EXPERIMENT':
				return r.experiment.name
			elif p == 'INSTANCE':
				return r.instance.filename
			elif p == 'REP':
				return str(r.repetition)
			else:
				return None

		script = util.expand_at_params(template, substitute)

		# TODO: Support multiple queues
		sbatch_args = ['sbatch']
		sbatch_args.extend(['-o', os.path.join(cfg.basedir, 'aux/_slurm/%A.out'),
				'-e', os.path.join(cfg.basedir, 'aux/_slurm/%A.err')])

		if not common.lock_run(r):
			return
		locked = [r]
		print("Launching experiment '{}', instance '{}' on slurm queue '{}'".format(
				r.experiment.name, r.instance.filename, '?'))

		process = subprocess.Popen(sbatch_args, stdin=subprocess.PIPE);
		process.communicate(script.encode()) # Assume UTF-8 encoding here.
		assert process.returncode == 0

		for run in locked:
			common.create_run_file(run)

