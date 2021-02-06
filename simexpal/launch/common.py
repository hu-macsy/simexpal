
import os
import selectors
import signal
import subprocess
import sys
import time

import yaml

from .. import base
from .. import util

class Launcher:
	pass

def lock_run(run):
	util.try_mkdir(os.path.join(run.config.basedir, 'aux'))
	util.try_mkdir(os.path.join(run.config.basedir, 'output'))
	util.try_mkdir(run.experiment.aux_subdir)
	util.try_mkdir(run.experiment.output_subdir)

	# We will try to launch the experiment.
	# First, create a .lock file. If that is successful, we are the process that
	# gets to launch the experiment. Afterwards, concurrent access to our files
	# can be considered a bug (or deliberate misuse) and will lead to hard failures.
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

def create_run_file(run, yml_dict={}):

	# Create the .run file. This signals that the run has been submitted.
	with open(run.aux_file_path('run.tmp'), 'w') as f:
		yaml.dump(yml_dict, f)
	os.rename(run.aux_file_path('run.tmp'), run.aux_file_path('run'))

# Stores all information that is necessary to invoke a run.
# This is a view over a POD object which can be YAML-encoded and sent
# over a wire or stored into a file.
class RunManifest:
	def __init__(self, yml):
		self.yml = yml

	@property
	def base_dir(self):
		return self.yml['config']['base_dir']

	@property
	def instance_dir(self):
		return self.yml['config']['instance_dir']

	@property
	def revision(self):
		return self.yml['revision']

	@property
	def instance(self):
		return self.yml['instance']

	@property
	def instance_name(self):
		return self.yml['instance_name']

	@property
	def instance_extensions(self):
		return self.yml['instance_extensions']

	@property
	def instance_files(self):
		return self.yml['instance_files']

	@property
	def instance_is_filess(self):
		return self.yml['instance_is_filess']

	@property
	def experiment(self):
		return self.yml['experiment']

	@property
	def repetition(self):
		return self.yml['repetition']

	@property
	def args(self):
		return self.yml['args']

	@property
	def environ(self):
		env_vars = self.yml['environ']
		for variant in self.yml['variants']:
			env_vars.update(variant['environ'].items())

		return env_vars

	@property
	def timeout(self):
		return self.yml['timeout']

	@property
	def aux_subdir(self):
		return base.get_aux_subdir(self.base_dir, self.experiment,
				[var_yml['name'] for var_yml in self.yml['variants']],
				self.revision)

	@property
	def output_subdir(self):
		return base.get_output_subdir(self.base_dir, self.experiment,
				[var_yml['name'] for var_yml in self.yml['variants']],
				self.revision)

	@property
	def workdir(self):
		return self.yml['workdir']

	@property
	def builds(self):
		return self.yml['builds']

	@property
	def output_extensions(self):
		return self.yml['output_extensions']

	@property
	def stdout(self):
		return self.yml['stdout']

	@property
	def variants(self):
		return [v['name'] for v in self.yml['variants']]

	def get_variant_value(self, axis):
		for variant in self.yml['variants']:
			if axis == variant['axis']:
				if not variant['is_dynamic']:
					raise RuntimeError("The axis '{}' does not have dynamic variants".format(axis))
				return variant['value']
		raise RuntimeError("The experiment '{}' does not use the variant axis '{}'".format(self.yml['experiment'], axis))

	def aux_file_path(self, ext):
		return os.path.join(self.aux_subdir,
				base.get_aux_file_name(ext, self.instance, self.repetition))

	def output_file_path(self, ext):
		return os.path.join(self.output_subdir,
				base.get_output_file_name(ext, self.instance, self.repetition))

	def get_extra_args(self):
		extra_args = []
		for var_yml in self.yml['variants']:
			extra_args.extend(var_yml['extra_args'])
		extra_args.extend(self.yml['instance_extra_args'])
		return extra_args

	def get_paths(self):
		paths = []
		for build_yml in self.yml['builds'].values():
			paths.append(os.path.join(build_yml['prefix'], 'bin'))
		return paths

	def get_ldso_paths(self):
		paths = []
		for build_yml in self.yml['builds'].values():
			paths.append(os.path.join(build_yml['prefix'], 'lib64'))
			paths.append(os.path.join(build_yml['prefix'], 'lib'))
		return paths

	def get_python_paths(self):
		paths = []
		for build_yml in self.yml['builds'].values():
			for export in build_yml['exports_python']:
				paths.append(os.path.join(build_yml['prefix'], export))
		return paths

	def get_source_dir_for(self, build_name):
		if build_name not in self.yml['builds']:
			raise RuntimeError("The experiment '{}' does not use the build '{}'".format(self.yml['experiment'], build_name))
		return self.yml['builds'][build_name]['source']

	def get_compile_dir_for(self, build_name):
		if build_name not in self.yml['builds']:
			raise RuntimeError("The experiment '{}' does not use the build '{}'".format(self.yml['experiment'], build_name))
		return self.yml['builds'][build_name]['compile']

	def get_prefix_dir_for(self, build_name):
		if build_name not in self.yml['builds']:
			raise RuntimeError("The experiment '{}' does not use the build '{}'".format(self.yml['experiment'], build_name))
		return self.yml['builds'][build_name]['prefix']

def compile_manifest(run):
	exp = run.experiment

	# Perform a DFS to discover all used builds.
	recursive_builds = []
	builds_visited = set()

	for name in exp.info.used_builds:
		assert name not in builds_visited
		build = run.config.get_build(name, exp.revision)
		recursive_builds.append(build)
		builds_visited.add(name)

	i = 0  # Need index-based loop as recursive_builds is mutated in the loop.
	while i < len(recursive_builds):
		build = recursive_builds[i]
		for req_name in build.info.requirements:
			if req_name in builds_visited:
				continue
			req_build = run.config.get_build(req_name, exp.revision)
			recursive_builds.append(req_build)
			builds_visited.add(req_name)
		i += 1

	instance_files = None
	instance_extensions = None
	if not run.instance.is_fileless:
		if run.instance.has_multi_files:
			instance_files = run.instance.filenames
		elif run.instance.has_multi_ext:
			instance_extensions = run.instance.extensions

	builds_dict = {}
	for build in recursive_builds:
		builds_dict[build.name] = {
			'source': build.source_dir if build.revision.is_dev_build else build.clone_dir,
			'compile': build.compile_dir,
			'prefix': build.prefix_dir,
			'exports_python': build.info.exports_python,
			'extra_paths': util.ensure_list_type(build.info.extra_paths)
		}

	# Collect extra arguments from variants
	variants_yml = []
	for variant in exp.variation:
		environ = {}
		for k, v in variant.environ.items():
			environ[k] = str(v)

		variants_yml.append({
			'axis': variant.axis,
			'name': variant.name,
			'extra_args': variant.extra_args,
			'environ': environ,
			'is_dynamic': variant.is_dynamic,
			'value': variant.value
		})

	environ = {}
	for (k, v) in exp.info.environ.items():
		environ[k] = str(v)

	stdout = None
	if exp.info.stdout is not None:
		stdout = exp.info.stdout
	elif exp.info.output == 'stdout':
		stdout = 'out'

	return RunManifest({
		'config': {
			'base_dir': run.config.basedir,
			'instance_dir': run.config.instance_dir()
		},
		'experiment': exp.name,
		'variants': variants_yml,
		'revision': exp.revision.name if exp.revision else None,
		'instance': run.instance.shortname,
		'instance_name': run.instance.yml_name,
		'instance_extensions': instance_extensions,
		'instance_files': instance_files,
		'instance_extra_args': run.instance.extra_args,
		'instance_is_filess': run.instance.is_fileless,
		'repetition': run.repetition,
		'builds': builds_dict,
		'args': exp.info.args,
		'timeout': float(exp.info.timeout) if exp.info.timeout is not None else exp.info.timeout,
		'environ': environ,
		'output_extensions': exp.info.output_extensions,
		'stdout': stdout,
		'workdir': exp.info.workdir
	})

def invoke_run(manifest):

	def get_qualified_output_file(ext):
		if ext not in manifest.output_extensions:
			raise RuntimeError(
				f"Unexpected output extension for experiment '{manifest.experiment}': .{ext}\n"
			)
		return manifest.output_file_path(ext)

	(stdout_pipe, stdout) = (None, None)
	if manifest.stdout is not None:
		stdout_path = get_qualified_output_file(manifest.stdout)

		# We do not actually need to write anything to the output file.
		# However, we might want to pipe experimental output to it.
		with open(stdout_path, 'w') as f:
			stdout = os.dup(f.fileno())
	else:
		stdout_path = manifest.aux_file_path('stdout')
		(stdout_pipe, stdout) = os.pipe()
		os.set_blocking(stdout_pipe, False)

	# Create all the other the output files.
	# The creation of the output file with extension '.out' signals that the run has been started.
	diff_set = {manifest.stdout} if manifest.stdout is not None else set()
	for ext in manifest.output_extensions - diff_set:
		util.touch(manifest.output_file_path(ext))

	# Create the error file.
	(stderr_pipe, stderr) = os.pipe()
	os.set_blocking(stderr_pipe, False)

	def get_qualified_filename(identifier):
		if manifest.instance_is_filess:
			raise RuntimeError(f"The instance '{manifest.instance}' is fileless")

		if identifier.isdigit():
			identifier = int(identifier)
			if manifest.instance_files is None:
				raise RuntimeError(
					f"Instance '{manifest.instance}' does not have any files specified in the experiments.yml"
				) from None
			if len(manifest.instance_files) <= identifier:
				raise IndexError('File index out of range: {}'.format(identifier))
			return ''.join([manifest.instance_dir, '/', manifest.instance_files[identifier]])
		else:
			if manifest.instance_extensions is None:
				raise RuntimeError(
					f"Instance '{manifest.instance}' does not have any extensions specified in the experiments.yml"
				) from None
			if identifier not in manifest.instance_extensions:
				raise RuntimeError(
					f"Unexpected file extension for instance '{manifest.instance}': .{identifier}"
				) from None
			return ''.join([manifest.instance_dir, '/', manifest.instance_name, '.', identifier])

	def substitute(p):
		if p == 'INSTANCE':
			if manifest.instance_is_filess:
				raise RuntimeError(f"The instance '{manifest.instance}' is fileless")

			return manifest.instance_dir + '/' + manifest.instance_name
		elif p.startswith('INSTANCE:'):
			return get_qualified_filename(p.split(':')[1])
		elif p == 'REPETITION':
			return str(manifest.repetition)
		elif p == 'OUTPUT':
			return stdout_path
		elif p.startswith('OUTPUT:'):
			return get_qualified_output_file(p.split(':')[1])
		elif p.startswith('SOURCE_DIR_FOR:'):
			return manifest.get_source_dir_for(p.split(':')[1])
		elif p.startswith('COMPILE_DIR_FOR:'):
			return manifest.get_compile_dir_for(p.split(':')[1])
		elif p.startswith('PREFIX_DIR_FOR:'):
			return manifest.get_prefix_dir_for(p.split(':')[1])
		elif p == 'OUTPUT_SUBDIR':
			return manifest.output_subdir
		elif p == 'BASE_DIR':
			return manifest.base_dir
		elif p == 'INSTANCE_DIR':
			return manifest.instance_dir
		elif p.startswith('VARIANT_VALUE:'):
			return str(manifest.get_variant_value(p.split(':')[1]))
		else:
			return None

	def substitute_list(p):
		if p == 'EXTRA_ARGS':
			return util.expand_at_params(manifest.get_extra_args(), substitute)
		else:
			return None

	cmd = util.expand_at_params(manifest.args, substitute, listfn=substitute_list)

	# Build the environment.
	def prepend_env(var, items):
		if var in os.environ:
			return ':'.join(items) + ':' + os.environ[var]
		return ':'.join(items)

	def substitute_extra_paths(p):
		if p in ['THIS_CLONE_DIR', 'THIS_SOURCE_DIR']:
			return build_yml['source']
		elif p == 'THIS_COMPILE_DIR':
			return build_yml['compile']
		elif p == 'THIS_PREFIX_DIR':
			return build_yml['prefix']
		elif p.startswith('SOURCE_DIR_FOR:'):
			return manifest.get_source_dir_for(p.split(':')[1])
		elif p.startswith('COMPILE_DIR_FOR:'):
			return manifest.get_compile_dir_for(p.split(':')[1])
		elif p.startswith('PREFIX_DIR_FOR:'):
			return manifest.get_prefix_dir_for(p.split(':')[1])
		elif p == 'BASE_DIR':
			return manifest.base_dir
		elif p == 'INSTANCE_DIR':
			return manifest.instance_dir
		else:
			return None
	environ = os.environ.copy()

	extra_paths = manifest.get_paths()
	for build_yml in manifest.builds.values():
		extra_paths.extend(util.expand_at_params(build_yml['extra_paths'], substitute_extra_paths))

	environ['PATH'] = prepend_env('PATH', extra_paths)
	environ['LD_LIBRARY_PATH'] = prepend_env('LD_LIBRARY_PATH', manifest.get_ldso_paths())
	environ['PYTHONPATH'] = prepend_env('PYTHONPATH', manifest.get_python_paths())

	manifest_environ = manifest.environ
	for env_var in manifest_environ:
		manifest_environ[env_var] = util.expand_at_params(manifest_environ[env_var], substitute)

	environ.update(manifest_environ)

	# Dumps data from an FD to the FS.
	# Creates the output file only if something is written.
	class LazyWriter:
		def __init__(self, fd, path):
			self._fd = fd
			self._path = path
			self._out = None

		def progress(self):
			# Specify some chunk size to avoid reading the whole pipe at once.
			chunk = os.read(self._fd, 16 * 1024)
			if not len(chunk):
				return False

			if self._out is None:
				self._out = open(self._path, "wb")
			self._out.write(chunk)
			self._out.flush()
			return True

		def close(self):
			if self._out is not None:
				self._out.close()

	start = time.perf_counter()
	cwd = (util.expand_at_params(manifest.workdir, substitute)
			if manifest.workdir is not None else manifest.base_dir)
	try:
		child = subprocess.Popen(cmd, cwd=cwd, env=environ,
				stdout=stdout, stderr=stderr)
	except FileNotFoundError:
		import traceback

		# Log the error traceback.
		with open(manifest.aux_file_path('stderr'), 'w') as f:
			f.write(traceback.format_exc())

		# Create the .status file.
		status_dict = {'timeout': False, 'walltime': 0,
				'status': -1, 'signal': None,
				'error': 'executable_not_found'}
		with open(manifest.output_file_path('status.tmp'), "w") as f:
			yaml.dump(status_dict, f)
		os.rename(manifest.output_file_path('status.tmp'), manifest.output_file_path('status'))

		return

	os.close(stderr)
	sel = selectors.DefaultSelector()

	if manifest.stdout is None:
		os.close(stdout)
		stdout_writer = LazyWriter(stdout_pipe, manifest.aux_file_path('stdout'))
		sel.register(stdout_pipe, selectors.EVENT_READ, stdout_writer)
	stderr_writer = LazyWriter(stderr_pipe, manifest.aux_file_path('stderr'))
	sel.register(stderr_pipe, selectors.EVENT_READ, stderr_writer)

	signal_reader, signal_writer = os.pipe()
	os.set_blocking(signal_writer, False)
	signal.set_wakeup_fd(signal_writer)

	# We need to install a signal handler in order for
	# signal.set_wakeup_fd() to write the signal into fd
	signal.signal(signal.SIGTERM, lambda *args: None)
	signal.signal(signal.SIGINT, lambda *args: None)

	sel.register(signal_reader, selectors.EVENT_READ)

	do_exit = False

	# Wait until the run program finishes.
	while True:
		if child.poll() is not None:
			break

		elapsed = time.perf_counter() - start
		if manifest.timeout is not None and elapsed > manifest.timeout:
			# Programs can catch the SIGXCPU signal and keep running.
			# Thus, the kill command ensures that the time limit is respected (with a grace period).
			if elapsed > manifest.timeout + base.TIMEOUT_GRACE_PERIOD:
				child.kill()
			else:
				child.send_signal(signal.SIGXCPU)

		# Consume any output that might be ready.
		events = sel.select(timeout=1)
		for (sk, mask) in events:
			if sk.fileobj == signal_reader:
				sel.unregister(signal_reader)
				child.kill()
				do_exit = True  # We also need to terminate the parent process. Otherwise subsequent experiments will be launched.
			elif not sk.data.progress():
				sel.unregister(sk.fd)

	os.close(signal_reader)
	os.close(signal_writer)

	# Consume all remaining output.
	while True:
		events = sel.select(timeout=0)
		for (sk, mask) in events:
			if not sk.data.progress():
				sel.unregister(sk.fd)
		if not events:
			break
	if manifest.stdout is None:
		stdout_writer.close()
		os.close(stdout_pipe)
	stderr_writer.close()
	os.close(stderr_pipe)
	runtime = time.perf_counter() - start

	# Collect the status information.
	status = None
	sigcode = None
	if child.returncode < 0:  # Killed by a signal?
		sigcode = signal.Signals(-child.returncode).name
	else:
		status = child.returncode
	did_timeout = manifest.timeout is not None and runtime > manifest.timeout

	# Create the status file to signal that we are finished.
	status_dict = {'timeout': did_timeout, 'walltime': runtime,
			'status': status, 'signal': sigcode,
			'error': None}
	with open(manifest.output_file_path('status.tmp'), "w") as f:
		yaml.dump(status_dict, f)
	os.rename(manifest.output_file_path('status.tmp'), manifest.output_file_path('status'))

	if do_exit:
		raise RuntimeError(
			"simexpal received a termination signal (either SIGINT or SIGTERM) and has terminated "
			"the current child process")
