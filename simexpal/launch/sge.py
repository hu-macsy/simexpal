
import os
import subprocess
import sys
import tempfile
import yaml

from .. import util
from . import common

dry_run = False

class SgeLauncher(common.Launcher):
	def __init__(self, queue):
		self.queue = queue

	def submit(self, config, run):
		self._do_submit(config, True, run)

	def submit_multiple(self, config, runs):
		self._do_submit(config, False, runs)

	def _do_submit(self, config, single_task, r):
		util.try_mkdir(os.path.join(config.basedir, 'aux'))
		util.try_mkdir(os.path.join(config.basedir, 'aux/_sge'))

		script = os.path.abspath(sys.argv[0])

		sge_args = ['qsub', '-b', 'y', '-q', self.queue]
		sge_args.extend(['-o', os.path.join(config.basedir, 'aux/_sge/$JOB_ID.out'),
				'-e', os.path.join(config.basedir, 'aux/_sge/$JOB_ID.err')])
		invoke_args = [script, '-C', config.basedir, 'internal-invoke']

		if single_task:
			if not common.lock_run(r):
				return
			locked = [r]
			print("Launching experiment '{}', instance '{}' on SGE queue '{}'".format(
					r.experiment.name, r.instance.shortname, self.queue))

			invoke_args.extend(['--experiment', r.experiment.name,
					'--instance', r.instance.shortname,
					'--repetition', str(r.repetition)])
		else:
			locked = [ ]
			for run in r:
				if not common.lock_run(run):
					continue
				print("Launching experiment '{}', instance '{}' on SGE queue '{}'".format(
						run.experiment.name, run.instance.shortname, self.queue))
				locked.append(run)

			if not locked:
				return

			spec_dict = {'array': [
				{'experiment': run.experiment.name,
					'instance': run.instance.shortname,
					'repetition': run.repetition}
				for run in locked
			]}
			(specfd, specfile) = tempfile.mkstemp(prefix='', suffix='.spec',
					dir=os.path.join(run.config.basedir, 'aux/_sge'))
			with os.fdopen(specfd, 'w') as f:
				yaml.dump(spec_dict, f, default_flow_style=False)

			sge_args.extend(['-t', '{}-{}'.format(0, len(locked)-1)])
			invoke_args.extend(['--specfile', specfile, '--sge-index'])

		if not dry_run:
			subprocess.check_call(sge_args + invoke_args)
		else:
			print("Would invoke SGE as:", sge_args + invoke_args)
			if single_task:
				subprocess.check_call(invoke_args + ['-n'])
			else:
				for i in range(len(locked)):
					sim_env = os.environ.copy()
					sim_env['SGE_TASK_ID'] = str(i)
					subprocess.check_call(invoke_args + ['-n'], env=sim_env)

		for run in locked:
			common.create_run_file(run)

