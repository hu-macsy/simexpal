
import collections
import os
import re
import subprocess
import sys
import tempfile

from .. import util
from . import common

script_template = '''#!/bin/sh
@SIMEX@ internal-invoke @MODE@ @SPECFILE@
'''

# regex for matching Slurm JobIDs
jobid_regex = r'Submitted batch job (?P<jobid>.+)'
prog = re.compile(jobid_regex)


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
		manifest = common.compile_manifest(locked[0])
		if not use_array:
			specs = {
				'manifest': manifest.yml
			}
		else:
			manifests = [manifest.yml]
			manifests.extend([common.compile_manifest(run).yml for run in locked[1:]])
			specs = {
				'manifests': manifests
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
				return '--method=slurm-array' if use_array else '--method=slurm'
			else:
				return None

		sbatch_script = util.expand_at_params(script_template, substitute)

		def substitute_slurm_settings(p):
			if p.startswith('VARIANT_VALUE:'):
				# Verify that all runs have the same variants.
				if use_array:
					for run in locked[1:]:
						if not locked[0].experiment.variation == run.experiment.variation:
							raise RuntimeError("Can not start experiment '{}' as Slurm job array. The experiment "
												"contains inconsistent variants.".format(locked[0].experiment.display_name))

				return str(manifest.get_variant_value(p.split(':')[1]))
			else:
				return None

		ps = experiment.effective_process_settings
		ts = experiment.effective_thread_settings

		def _represents_int(x):
			try:
				int(x)
				return True
			except ValueError:
				return False

		if ps is not None:
			if ps['num_nodes'] is not None:
				if isinstance(ps['num_nodes'], str):
					ps['num_nodes'] = util.expand_at_params(ps['num_nodes'], substitute_slurm_settings)
				if not _represents_int(ps['num_nodes']):
					raise RuntimeError("The value of the 'num_nodes' key has to be an integer: {}".format(ps['num_nodes']))

			if ps['procs_per_node'] is not None:
				if isinstance(ps['procs_per_node'], str):
					ps['procs_per_node'] = util.expand_at_params(ps['procs_per_node'], substitute_slurm_settings)
				if not _represents_int(ps['procs_per_node']):
					raise RuntimeError("The value of the 'procs_per_node' key has to be an integer: {}".format(ps['procs_per_node']))

		if ts is not None:
			if isinstance(ts['num_threads'], str):
				ts['num_threads'] = util.expand_at_params(ts['num_threads'], substitute_slurm_settings)
			if not _represents_int(ts['num_threads']):
				raise RuntimeError("The value of the 'num_threads' key has to be an integer: {}".format(ts['num_threads']))

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
				print("Submitting run {}/{}[{}] to slurm partition '{}'".format(
						run.experiment.display_name, run.instance.shortname, run.repetition, self.queue))
			else:
				print("Submitting run {}/{}[{}] to default slurm partition".format(
						run.experiment.display_name, run.instance.shortname, run.repetition))

		process = subprocess.Popen(sbatch_args, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
		out, _ = process.communicate(sbatch_script.encode())  # Assume UTF-8 encoding here.
		return_msg = out.decode()
		print(return_msg)

		assert process.returncode == 0

		jobid = prog.match(return_msg).group('jobid')
		if use_array:
			for idx, run in enumerate(locked):
				common.create_run_file(run, {'slurm_jobid': str(jobid) + '_' + str(idx)})
		else:
			common.create_run_file(locked[0], {'slurm_jobid': str(jobid)})

