
from enum import Enum, IntEnum
import os.path
import subprocess

from . import util

def make_builds(cfg, revision, infos, wanted_builds, wanted_phases):
	order = compute_order(cfg, infos)

	print("simexpal: Making builds {} @ {}".format(', '.join([info.name for info in order]),
			revision.name))
	for info in order:
		make_build_in_order(cfg, cfg.get_build(info.name, revision), wanted_builds, wanted_phases)

def compute_order(cfg, desired):
	class State(Enum):
		NULL = 0
		EXPANDING = 1
		ORDERED = 2

	order = [ ]

	# The following code does a topologic sort of the desired items.
	# It lazily expands their dependencies using expand().
	stack = [ ]
	state = dict()

	def expand(info):
		for name in info.requirements:
			yield cfg.get_build_info(name)

	def visit(info):
		if info.name not in state:
			links = expand(info)
			state[info.name] = State.EXPANDING
			stack.append((info, list(links)))
		elif state[info.name] == State.EXPANDING:
			raise RuntimeError("Program has circular dependencies")
		else:
			# Programs that are already ordered do not need to be considered again.
			assert state[info.name] == State.ORDERED

	for info in desired:
		visit(info)

		while stack:
			(info, rem_links) = stack[-1]
			if not rem_links:
				assert state[info.name] == State.EXPANDING
				state[info.name] = State.ORDERED
				stack.pop()
				order.append(info)
			else:
				visit(rem_links.pop())

	return order

# Determine which phases to run.
class Phase(IntEnum):
	NULL = 0
	CHECKOUT = 1
	REGENERATE = 2
	CONFIGURE = 3
	COMPILE = 4
	INSTALL = 5

def make_build_in_order(cfg, build, wanted_builds, wanted_phases):
	if not build.revision.is_dev_build:
		util.try_mkdir('builds/')
		checkout_dir = build.clone_dir
	else:
		util.try_mkdir('develop/')
		util.try_mkdir('dev-builds/')
		checkout_dir = build.source_dir

	def num_allocated_cpus():
		try:
			cpuset = os.sched_getaffinity(0)
		except AttributeError:
			# MacOS does not have CPU affinity.
			return None
		return len(cpuset)

	def get_concurrency():
		n = num_allocated_cpus()
		if n is None:
			# The best that we can do is returning the number of all CPUs.
			n = os.cpu_count()
		return n

	def get_source_dir_for(build_name):
		other_build = cfg.get_build(build_name, build.revision)
		if not other_build.revision.is_dev_build:
			return other_build.clone_dir
		return other_build.source_dir

	def get_compile_dir_for(build_name):
		other_build = cfg.get_build(build_name, build.revision)
		return other_build.compile_dir

	def get_prefix_dir_for(build_name):
		other_build = cfg.get_build(build_name, build.revision)
		return other_build.prefix_dir

	def substitute(var):
		# 'THIS_SOURCE_DIR' is prefered, 'THIS_CLONE_DIR' is deprecated
		if var in ['THIS_CLONE_DIR', 'THIS_SOURCE_DIR']:
			if not build.revision.is_dev_build:
				return build.clone_dir
			else:
				return build.source_dir
		elif var == 'THIS_COMPILE_DIR':
			return build.compile_dir
		elif var == 'THIS_PREFIX_DIR':
			return build.prefix_dir
		elif var.startswith('SOURCE_DIR_FOR:'):
			return get_source_dir_for(var.split(':')[1])
		elif var.startswith('COMPILE_DIR_FOR:'):
			return get_compile_dir_for(var.split(':')[1])
		elif var.startswith('PREFIX_DIR_FOR:'):
			return get_prefix_dir_for(var.split(':')[1])
		elif var == 'PARALLELISM':
			return str(get_concurrency())

	# Build the environment.
	def prepend_env(var, items):
		if(var in os.environ):
			return ':'.join(items) + ':' + os.environ[var]
		return ':'.join(items)

	recursive_infos = build.info.traverse_requirements()
	recursive_builds = [cfg.get_build(info.name, build.revision) for info in recursive_infos]

	def collect_prefix_paths(subdir):
		return [os.path.join(req.prefix_dir, subdir) for req in recursive_builds]
	pkgconfig_paths = collect_prefix_paths('lib64/pkgconfig')
	pkgconfig_paths += collect_prefix_paths('lib/pkgconfig')

	base_environ = os.environ.copy()
	base_environ['PKG_CONFIG_PATH'] = prepend_env('PKG_CONFIG_PATH', pkgconfig_paths)

	def skip_phase(phase):
		return phase > max(wanted_phases)

	done_phases = set()
	if build.name in wanted_builds:
		if (build.is_installed() or skip_phase(Phase.INSTALL)) and Phase.INSTALL not in wanted_phases:
			done_phases.add(Phase.INSTALL)
		if (build.is_compiled() or skip_phase(Phase.COMPILE)) and Phase.COMPILE not in wanted_phases:
			done_phases.add(Phase.COMPILE)
		if (build.is_configured() or skip_phase(Phase.CONFIGURE)) and Phase.CONFIGURE not in wanted_phases:
			done_phases.add(Phase.CONFIGURE)
		if (build.is_regenerated() or skip_phase(Phase.REGENERATE)) and Phase.REGENERATE not in wanted_phases:
			done_phases.add(Phase.REGENERATE)
		if (build.is_checked_out() or skip_phase(Phase.CHECKOUT)) and Phase.CHECKOUT not in wanted_phases:
			done_phases.add(Phase.CHECKOUT)
	else:
		if build.is_installed():
			done_phases.add(Phase.INSTALL)
		if build.is_compiled():
			done_phases.add(Phase.COMPILE)
		if build.is_configured():
			done_phases.add(Phase.CONFIGURE)
		if build.is_regenerated():
			done_phases.add(Phase.REGENERATE)
		if build.is_checked_out():
			done_phases.add(Phase.CHECKOUT)

	def want_phase(phase):
		# TODO: Support additional phase section modes. For example:
		#       - Clean rebuilds from scratch. This should be prefered for production use.
		return phase not in done_phases

	# Perform the actual build phases.
	def log_phase(step):
		print("simexpal: Running {}-phase for build {}".format(step, build.name))

	did_work = False

	def do_step(step_yml, default_workdir=None):
		workdir = default_workdir
		if 'workdir' in step_yml:
			workdir = util.expand_at_params(step_yml['workdir'], substitute)

		environ = base_environ.copy()
		if 'environ' in step_yml:
			for (var, value) in step_yml['environ'].items():
				environ[var] = util.expand_at_params(value, substitute)

		if isinstance(step_yml['args'], list):
			shell = False
			args = [util.expand_at_params(arg, substitute) for arg in step_yml['args']]
		else:
			assert isinstance(step_yml['args'], str)
			shell = True
			args = util.expand_at_params(step_yml['args'], substitute)

		subprocess.check_call(args, cwd=workdir, env=environ, shell=shell)

	if want_phase(Phase.CHECKOUT):
		log_phase('checkout')

		if not build.revision.is_dev_build:

			def git_ref_changed():
				local_hash = subprocess.check_output(['git', 'rev-parse', generic_tag], cwd=build.repo_dir)
				local_hash = local_hash.strip().decode()

				if local_hash == git_ref:
					return False
				else:
					remote_refs = subprocess.check_output(['git', 'ls-remote', build.info.git_repo, git_ref]).decode().splitlines()

					if len(remote_refs) == 0:
						raise RuntimeError("Git reference '{}' does not exist". format(git_ref))
					elif len(remote_refs) > 1:
						raise RuntimeError("Git reference '{}' is ambiguous". format(git_ref))
					else:
						remote_hash, _ = remote_refs[0].split('\t')

						if local_hash == remote_hash:
							return False

				return True

			git_ref = build.revision.version_for_build(build.name)
			generic_tag = 'refs/tags/simexpal-rev/' + build.revision.name

			# Fetch the remote ref to a local tag.
			fetch_refspec = ['+' + git_ref + ':' + generic_tag]

			# TODO: If we *know* that the ref is a tag, we want to do something like the following:
			#fetch_refspec = ['+refs/tags/' + git_ref + ':' + generic_tag]

			# Create the repository (in an empty state).
			if not os.access(build.repo_dir, os.F_OK):
				subprocess.check_call(['git', 'init', '-q', '--bare', build.repo_dir])

			# Fetch the specified revision if it does not exist already.
			verify_ref_result = subprocess.call(['git', '--git-dir', build.repo_dir,
					'rev-parse', '-q', '--verify', generic_tag],
				stdout=subprocess.DEVNULL)

			if verify_ref_result != 0 or git_ref_changed():
				# As we create generic_tag, we can add --no-tags here.
				subprocess.check_call(['git', '--git-dir', build.repo_dir,
						'fetch', '--depth=1', '--no-tags',
						build.info.git_repo] + fetch_refspec)

			# Prune the existing worktree.
			util.try_rmtree(build.clone_dir)
			subprocess.check_call(['git', '--git-dir', build.repo_dir,
					'worktree', 'prune'])

			# Recreate the worktree and check out the specified revision.
			subprocess.check_call(['git', '--git-dir', build.repo_dir,
					'worktree', 'add', '--detach',
					build.clone_dir,
					generic_tag])
		else:
			# Recreate the source directory
			util.try_rmtree(build.source_dir)
			util.try_mkdir(build.source_dir)

			# Clone the git repository into the build.source_dir
			subprocess.check_call(['git', 'clone', build.info.git_repo, build.source_dir])

		util.touch(os.path.join(checkout_dir, 'checkedout.simexpal'))

		if build.info.recursive_clone:
			# Clone submodules recursively
			subprocess.check_call(['git', 'submodule',
					'update', '--init', '--recursive'], cwd=checkout_dir)

		did_work = True

	if want_phase(Phase.REGENERATE):
		log_phase('regenerate')

		regenerate_args = util.ensure_list_type(build.info.regenerate)
		for step_yml in regenerate_args:
			do_step(step_yml, default_workdir=checkout_dir)
		util.touch(os.path.join(checkout_dir, 'regenerated.simexpal'))
		did_work = True

	if want_phase(Phase.CONFIGURE):
		log_phase('configure')

		# Recreate the compilation directory.
		util.try_rmtree(build.compile_dir)
		util.try_mkdir(build.compile_dir)

		configure_args = util.ensure_list_type(build.info.configure)
		for step_yml in configure_args:
			do_step(step_yml, default_workdir=build.compile_dir)
		util.touch(os.path.join(build.compile_dir, 'configured.simexpal'))
		did_work = True

	if want_phase(Phase.COMPILE):
		log_phase('compile')

		compile_args = util.ensure_list_type(build.info.compile)
		for step_yml in compile_args:
			do_step(step_yml, default_workdir=build.compile_dir)
		util.touch(os.path.join(build.compile_dir, 'compiled.simexpal'))
		did_work = True

	if want_phase(Phase.INSTALL):
		log_phase('install')

		# Recreate the prefix directory.
		util.try_rmtree(build.prefix_dir)
		util.try_mkdir(build.prefix_dir)

		install_args = util.ensure_list_type(build.info.install)
		for step_yml in install_args:
			do_step(step_yml, default_workdir=build.compile_dir)
		util.touch(os.path.join(build.prefix_dir, 'installed.simexpal'))
		did_work = True

	if not did_work:
		print("simexpal: Nothing to do for {}".format(build.name))

