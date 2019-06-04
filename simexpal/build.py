
from enum import Enum, IntEnum
import os.path
import subprocess

from . import util

def make_builds(cfg, revision, infos):
	order = compute_order(cfg, infos)

	print("simexpal: Making builds {} @ {}".format(', '.join([info.name for info in order]),
			revision.name))
	for info in order:
		make_build_in_order(cfg, cfg.get_build(info.name, revision))

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
			for (circ_action, circ_subject, _) in stack:
				print(Action.strings[circ_action], circ_subject.name)
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

def make_build_in_order(cfg, build):
	util.try_mkdir('builds/')

	def substitute(var):
		if var == 'THIS_CLONE_DIR':
			return build.clone_dir
		elif var == 'THIS_PREFIX_DIR':
			return build.prefix_dir
		elif var == 'PARALLELISM':
			nthreads = len(os.sched_getaffinity(0))
			return str(nthreads)

	# Build the environment.
	def prepend_env(var, items):
		if(var in os.environ):
			return ':'.join(items) + ':' + os.environ[var]
		return ':'.join(items)

	recursive_infos = build.info.traverse_requirements()
	recursive_builds = [cfg.get_build(info.name, build.revision) for info in recursive_infos]

	def collect_prefix_paths(subdir):
		return [os.path.join(req.prefix_dir, subdir) for req in recursive_builds]
	pkgconfig_paths = collect_prefix_paths('lib/pkgconfig')

	base_environ = os.environ.copy()
	base_environ['PKG_CONFIG_PATH'] = prepend_env('PKG_CONFIG_PATH', pkgconfig_paths)

	# Determine which phases to run.
	class Phase(IntEnum):
		NULL = 0
		CHECKOUT = 1
		REGENERATE = 2
		CONFIGURE = 3
		COMPILE = 4
		INSTALL = 5

	done_phases = set()
	if os.access(os.path.join(build.prefix_dir, 'installed.simexpal'), os.F_OK):
		done_phases.add(Phase.INSTALL)
	if os.access(os.path.join(build.compile_dir, 'compiled.simexpal'), os.F_OK):
		done_phases.add(Phase.COMPILE)
	if os.access(os.path.join(build.compile_dir, 'configured.simexpal'), os.F_OK):
		done_phases.add(Phase.CONFIGURE)
	if os.access(os.path.join(build.clone_dir, 'regenerated.simexpal'), os.F_OK):
		done_phases.add(Phase.REGENERATE)
	if os.access(os.path.join(build.clone_dir, 'checkedout.simexpal'), os.F_OK):
		done_phases.add(Phase.CHECKOUT)

	def want_phase(phase):
		# TODO: Support additional phase section modes. For example:
		#       - Clean rebuilds from scratch. This should be prefered for production use.
		#       - Running individual phases. This should help with debugging.
		return not done_phases or phase > max(done_phases)

	# Perform the actual build phases.
	def log_phase(step):
		print("simexpal: Running {}-phase for build {}".format(step, build.name))

	did_work = False

	def do_step(step_yml, workdir=None):
		environ = base_environ.copy()
		if 'environ' in step_yml:
			for (var, value) in step_yml['environ'].items():
				environ[var] = util.expand_at_params(value, substitute)
		args = [util.expand_at_params(arg, substitute) for arg in step_yml['args']]
		subprocess.check_call(args, cwd=workdir, env=environ)

	if want_phase(Phase.CHECKOUT):
		log_phase('checkout')

		# Recreate the source directory.
		util.try_rmtree(build.clone_dir)

		subprocess.check_call(['git', 'clone', build.info._build_yml['git'], build.clone_dir])
		subprocess.check_call(['git', '--git-dir', build.clone_dir + '/.git',
				'--work-tree', build.clone_dir,
				'checkout',
				build.revision.version_for_build(build.name)])
		util.touch(os.path.join(build.clone_dir, 'checkedout.simexpal'))
		did_work = True

	if want_phase(Phase.REGENERATE):
		log_phase('regenerate')
		if 'regenerate' in build.info._build_yml:
			for step_yml in build.info._build_yml['regenerate']:
				do_step(step_yml, build.clone_dir)
		util.touch(os.path.join(build.clone_dir, 'regenerated.simexpal'))
		did_work = True

	if want_phase(Phase.CONFIGURE):
		log_phase('configure')

		# Recreate the compilation directory.
		util.try_rmtree(build.compile_dir)
		util.try_mkdir(build.compile_dir)

		if 'configure' in build.info._build_yml:
			for step_yml in build.info._build_yml['configure']:
				do_step(step_yml, workdir=build.compile_dir)
		util.touch(os.path.join(build.compile_dir, 'configured.simexpal'))
		did_work = True

	if want_phase(Phase.COMPILE):
		log_phase('compile')
		if 'compile' in build.info._build_yml:
			for step_yml in build.info._build_yml['compile']:
				do_step(step_yml, workdir=build.compile_dir)
		util.touch(os.path.join(build.compile_dir, 'compiled.simexpal'))
		did_work = True

	if want_phase(Phase.INSTALL):
		log_phase('install')

		# Recreate the prefix directory.
		util.try_rmtree(build.prefix_dir)
		util.try_mkdir(build.prefix_dir)

		if 'install' in build.info._build_yml:
			for step_yml in build.info._build_yml['install']:
				do_step(step_yml, workdir=build.compile_dir)
		util.touch(os.path.join(build.prefix_dir, 'installed.simexpal'))
		did_work = True

	if not did_work:
		print("simexpal: Nothing to do for {}".format(build.name))

