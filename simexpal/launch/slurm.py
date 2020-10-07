
import collections
import os
import subprocess
import sys
import tempfile

from .. import util
from . import common

script_template = '''#!/bin/sh
@SIMEX@ internal-invoke @MODE@ @SPECFILE@
'''

class SlurmLauncher(common.Launcher):
	def __init__(self, queue):
		self.queue = queue

	def submit(self, cfg, run):
		self._do_submit(cfg, run.experiment, [run])

	def submit_multiple(self, cfg, runs):
		groups = collections.defaultdict(list)
		for run in runs:
			groups[run.experiment].append(run)
		for grp_exp, grp_runs in groups.items():
			self._do_submit(cfg, grp_exp, grp_runs)

	def _do_submit(self, cfg, experiment, runs):
		util.try_mkdir(os.path.join(cfg.basedir, 'aux'))
		util.try_mkdir(os.path.join(cfg.basedir, 'aux/_slurm'))

		# Lock the runs to make sure that we do not submit runs twice.
		locked = []
		for run in runs:
			if not common.lock_run(run):
				continue
			locked.append(run)

		if not locked:
			return
		use_array = len(locked) > 1

		# Build the specfile.
		if not use_array:
			specs = {
				'manifest': common.compile_manifest(locked[0]).yml
			}
		else:
			specs = {
				'manifests': [common.compile_manifest(run).yml for run in locked]
			}

		(specfd, specfile) = tempfile.mkstemp(prefix='', suffix='-spec.yml',
				dir=os.path.join(cfg.basedir, 'aux/_slurm'))
		with os.fdopen(specfd, 'w') as f:
			util.write_yaml_file(f, specs)

		# Expand the script that is passed to sbatch.
		def substitute(p):
			if p == 'SIMEX':
				return os.path.abspath(sys.argv[0])
			elif p == 'SPECFILE':
				return specfile
			elif p == 'MODE':
				return '--slurm-array' if use_array else '--slurm'
			else:
				return None

		sbatch_script = util.expand_at_params(script_template, substitute)

		ps = experiment.effective_process_settings
		ts = experiment.effective_thread_settings

		# Build the sbatch command to run the script.
		# TODO: Support multiple queues
		sbatch_args = ['sbatch', '-J', experiment.display_name]
		if self.queue:
			sbatch_args += ['-p', self.queue]
		if ps and ps['num_nodes']:
			sbatch_args += ['-N', str(ps['num_nodes'])]
		if ps and ps['procs_per_node']:
			sbatch_args += ['--ntasks-per-node', str(ps['procs_per_node'])]
		if ts and ts['num_threads']:
			sbatch_args += ['-c', str(ts['num_threads'])]
		log_pattern = '%A-%a' if use_array else '%A'
		sbatch_args.extend(['-o', os.path.join(cfg.basedir, 'aux/_slurm/' + log_pattern + '.out'),
				'-e', os.path.join(cfg.basedir, 'aux/_slurm/' + log_pattern + '.err')])

		if use_array:
			sbatch_args.append('--array=0-' + str(len(locked) - 1))

		# Add custom sbatch parameters of the user.
		slurm_args = util.ensure_list_type(experiment.effective_slurm_args)
		sbatch_args.extend(slurm_args)

		# Finally start the run.
		for run in locked:
			if self.queue:
				print("Submitting experiment '{}', instance '{}' to slurm partition '{}'".format(
						run.experiment.name, run.instance.shortname, self.queue))
			else:
				print("Submitting experiment '{}', instance '{}' to default slurm partition".format(
						run.experiment.name, run.instance.shortname))

		process = subprocess.Popen(sbatch_args, stdin=subprocess.PIPE)
		process.communicate(sbatch_script.encode())  # Assume UTF-8 encoding here.
		assert process.returncode == 0

		for run in locked:
			common.create_run_file(run)

