
import os
import selectors
import signal
import subprocess
import time

import yaml

from .. import util

class Launcher:
	pass

def lock_run(run):
	(exp, instance) = (run.experiment, run.instance.filename)
	util.try_mkdir(os.path.join(run.config.basedir, 'aux'))
	util.try_mkdir(os.path.join(run.config.basedir, 'output'))
	util.try_mkdir(exp.aux_subdir)
	util.try_mkdir(exp.output_subdir)

	# We will try to launch the experiment.
	# First, create a .lock file. If that is successful, we are the process that
	# gets to launch the experiment. Afterwards, concurrent access to our files
	# can be considered a bug (or deliberate misuse) and will lead to hard failues.
	try:
		lockfd = os.open(run.aux_file_path('lock'),
				os.O_RDONLY | os.O_CREAT | os.O_EXCL, mode=0)
	except FileExistsError:
		# TODO: Those warnings should be behind a flag.
#				print("Warning: .lock file exists for experiment '{}', instance '{}'".format(
#						exp.name, instance))
#				print("Either experiments are launched concurrently or the launcher crashed.")
		return False
	os.close(lockfd)
	return True

def create_run_file(run):
	(exp, instance) = (run.experiment, run.instance.filename)

	# Create the .run file. This signals that the run has been submitted.
	with open(run.aux_file_path('run.tmp'), "w") as f:
		pass
	os.rename(run.aux_file_path('run.tmp'), run.aux_file_path('run'))

def invoke_run(run):
	(exp, instance) = (run.experiment, run.instance.filename)

	# Perform a DFS to discover all used builds.
	recusive_builds = []
	builds_visited = set()

	for name in exp.info.used_builds:
		assert name not in builds_visited
		build = run.config.get_build(name, exp.revision)
		recusive_builds.append(build)
		builds_visited.add(name)

	i = 0 # Need index-based loop as recusive_builds is mutated in the loop.
	while i < len(recusive_builds):
		build = recusive_builds[i]
		for req_name in build.info.requirements:
			if req_name in builds_visited:
				continue
			req_build = run.config.get_build(req_name, exp.revision)
			recusive_builds.append(req_build)
			builds_visited.add(req_name)
		i += 1

	# Collect extra arguments from variants
	extra_args = [ ]
	for variant in exp.variation:
		extra_args.extend(variant.variant_yml['extra_args'])

	# Create the output file. This signals that the run has been started.
	stdout = None
	with open(run.output_file_path('out'), "w") as f:
		# We do not actually need to write anything to the output file.
		# However, we might want to pipe experimental output to it.
		if 'output' in exp.info._exp_yml and exp.info._exp_yml['output'] == 'stdout':
			stdout = os.dup(f.fileno())

	def substitute(p):
		if p == 'INSTANCE':
			return run.config.instance_dir() + '/' + instance
		elif p == 'REPETITION':
			return str(run.repetition)
		elif p == 'OUTPUT':
			return run.output_file_path('out')
		else:
			return None

	def substitute_list(p):
		if p == 'EXTRA_ARGS':
			return extra_args
		else:
			return None

	assert isinstance(exp.info._exp_yml['args'], list)
	cmd = util.expand_at_params(exp.info._exp_yml['args'], substitute, listfn=substitute_list)

	# Build the environment.
	def prepend_env(var, items):
		if(var in os.environ):
			return ':'.join(items) + ':' + os.environ[var]
		return ':'.join(items)

	build_paths = [os.path.join(p.prefix_dir, 'bin') for p in recusive_builds]
	build_ld_paths = [os.path.join(p.prefix_dir, 'lib') for p in recusive_builds]

	environ = os.environ.copy()
	environ['PATH'] = prepend_env('PATH', build_paths)
	environ['LD_LIBRARY_PATH'] = prepend_env('LD_LIBRARY_PATH', build_ld_paths)

	if 'environ' in exp.info._exp_yml:
		for (k, v) in exp.info._exp_yml['environ'].items():
			environ[k] = str(v)

	# Dumps data from an FD to the FS.
	# Creates the output file only if something is written.
	class LazyWriter:
		def __init__(self, fd, path):
			self._fd = fd
			self._path = path
			self._out = None

		def progress(self):
			# Specify some chunk size to avoid reading the whole pipe at once.
			chunk = self._fd.read(16 * 1024)
			if not len(chunk):
				return False

			if self._out is None:
				self._out = open(self._path, "wb")
			self._out.write(chunk)
			return True

		def close(self):
			if self._out is not None:
				self._out.close()

	start = time.perf_counter()
	child = subprocess.Popen(cmd, cwd=run.config.basedir, env=environ,
			stdout=stdout, stderr=subprocess.PIPE)
	sel = selectors.DefaultSelector()
	
	stderr_writer = LazyWriter(child.stderr, run.aux_file_path('stderr'))
	sel.register(child.stderr, selectors.EVENT_READ, stderr_writer)

	# Wait until the run program finishes.
	while True:
		if child.poll() is not None:
			break

		elapsed = time.perf_counter() - start
		if 'timeout' in exp.info._exp_yml and elapsed > float(exp.info._exp_yml['timeout']):
			child.send_signal(signal.SIGXCPU)

		# Consume any output that might be ready.
		events = sel.select(timeout=1)
		for (sk, mask) in events:
			if not sk.data.progress():
				sel.unregister(sk.fd)

	# Consume all remaining output.
	while True:
		events = sel.select(timeout=0)
		for (sk, mask) in events:
			if not sk.data.progress():
				sel.unregister(sk.fd)
		if not events:
			break
	stderr_writer.close()
	runtime = time.perf_counter() - start

	# Collect the status information.
	status = None
	sigcode = None
	if child.returncode < 0: # Killed by a signal?
		sigcode = signal.Signals(-child.returncode).name
	else:
		status = child.returncode
	timeout = 'timeout' in exp.info._exp_yml and runtime > float(exp.info._exp_yml['timeout'])

	# Create the status file to signal that we are finished.
	status_dict = {'timeout': timeout, 'walltime': runtime,
			'status': status, 'signal': sigcode}
	with open(run.output_file_path('status.tmp'), "w") as f:
		yaml.dump(status_dict, f)
	os.rename(run.output_file_path('status.tmp'), run.output_file_path('status'))

