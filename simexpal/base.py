
from collections import OrderedDict
import copy
import itertools
import os
import yaml

from . import instances
from . import util

class MatrixScope:
	@staticmethod
	def walk_matrix(cfg, root_yml, expand):
		outmost = MatrixScope(cfg, None)

		result = set()
		if 'matrix' not in root_yml:
			result.update(expand(outmost))
		else:
			for item_yml in root_yml['matrix']['include']:
				scope = MatrixScope(cfg, outmost)
				scope.select(item_yml)
				result.update(expand(scope))

		return result

	def __init__(self, cfg, outer):
		self.cfg = cfg

		if outer is not None:
			self.selected_exps = copy.copy(outer.selected_exps)
			self.selected_revs = copy.copy(outer.selected_revs)
			self.selected_axes = copy.copy(outer.selected_axes)
			self.selected_variants = copy.deepcopy(outer.selected_variants)
			self.selected_instsets = copy.copy(outer.selected_instsets)
			self.num_repetitions = outer.num_repetitions
		else:
			self.selected_exps = None
			self.selected_revs = None
			self.selected_axes = None
			self.selected_variants = {}
			self.selected_instsets = None
			self.num_repetitions = None

	def select(self, item_yml):
		if 'experiments' in item_yml:
			if self.selected_exps is None:
				self.selected_exps = set()
			self.selected_exps.update(item_yml['experiments'])

		if 'revisions' in item_yml:
			if self.selected_revs is None:
				self.selected_revs = set()
			self.selected_revs.update(item_yml['revisions'])

		if 'axes' in item_yml:
			if self.selected_axes is None:
				self.selected_axes = set()
			self.selected_axes.update(item_yml['axes'])

		if 'variants' in item_yml:
			for name in item_yml['variants']:
				variant = self.cfg.get_variant(name)
				if variant.axis not in self.selected_variants:
					self.selected_variants[variant.axis] = set()
				self.selected_variants[variant.axis].add(variant.name)

		if 'instsets' in item_yml:
			if self.selected_instsets is None:
				self.selected_instsets = set()
			self.selected_instsets.update(item_yml['instsets'])

		if 'repeat' in item_yml:
			self.num_repetitions = item_yml['repeat']

class Config:
	"""Represents the entire configuration (i.e., an experiments.yml file)."""

	def __init__(self, basedir, yml):
		assert os.path.isabs(basedir)
		self.basedir = basedir
		self.yml = yml

		self._insts = OrderedDict()
		self._build_infos = OrderedDict()
		self._revisions = OrderedDict()
		self._variants = OrderedDict()
		self._exp_infos = OrderedDict()

		def construct_instances():
			if 'instances' in self.yml:
				for inst_yml in self.yml['instances']:
					for item in inst_yml['items']:
						yield Instance(self, item, inst_yml)

		def construct_variants():
			if 'variants' in self.yml:
				for axis_yml in self.yml['variants']:
					for variant_yml in axis_yml['items']:
						yield Variant(self, axis_yml['axis'], variant_yml)

		for inst in sorted(construct_instances(), key=lambda inst: inst.filename):
			self._insts[inst.filename] = inst

		if 'builds' in self.yml:
			for build_yml in sorted(self.yml['builds'], key=lambda y: y['name']):
				self._build_infos[build_yml['name']] = BuildInfo(self, build_yml)

		if 'revisions' in self.yml:
			for revision_yml in sorted(self.yml['revisions'], key=lambda y: y['name']):
				self._revisions[revision_yml['name']] = Revision(self, revision_yml)

		for variant in sorted(construct_variants(), key=lambda variant: variant.name):
			self._variants[variant.name] = variant

		if 'experiments' in self.yml:
			for exp_yml in sorted(self.yml['experiments'], key=lambda y: y['name']):
				self._exp_infos[exp_yml['name']] = ExperimentInfo(self, exp_yml)

	def instance_dir(self):
		"""Path of the directory that stores all the instances."""
		return os.path.join(self.basedir, self.yml['instdir'])

	def all_instance_ids(self):
		for inst in self.all_instances():
			yield inst.filename

	def all_instances(self):
		yield from self._insts.values()

	def get_instance(self, name):
		if name not in self._insts:
			raise RuntimeError("Instance {} does not exist".format(name))
		return self._insts[name]

	def get_build_info(self, name):
		if name not in self._build_infos:
			raise RuntimeError("BuildInfo {} does not exist".format(name))
		return self._build_infos[name]

	def all_revisions(self):
		yield from self._revisions.values()

	def get_revision(self, name):
		if name is None: # TODO: Questionable special case.
			return None
		if name not in self._revisions:
			raise RuntimeError("Revision {} does not exist".format(name))
		return self._revisions[name]

	def all_builds(self):
		if 'builds' in self.yml:
			for build_yml in sorted(self.yml['builds'], key=lambda y: y['name']):
				for revision in self.all_revisions():
					spec_set = set(revision.specified_versions)
					if build_yml['name'] not in spec_set:
						continue
					# TODO: Exclude the build if not all requirements are specified in spec_set.
					yield Build(self, self.get_build_info(build_yml['name']), revision)

	def all_builds_for_revision(self, revision):
		for build in self.all_builds():
			if build.revision == revision:
				yield build

	def get_build(self, name, revision):
		for build in self.all_builds(): # TODO: Avoid a quadratic blowup.
			if build.name == name and build.revision == revision:
				return build
		raise RuntimeError("Build {} does not exist".format(name))

	def all_variants(self):
		yield from self._variants.values()

	def get_variant(self, name):
		if name not in self._variants:
			raise RuntimeError("Variant {} does not exist".format(name))
		return self._variants[name]

	def _test_variation_id_in_scope(self, variation_id, scope):
		if scope.selected_axes is not None:
			for name in variation_id:
				variant = self.get_variant(name)
				if variant.axes not in scope.selected_axes:
					return False
		if scope.selected_variants is not None:
			for name in variation_id:
				variant = self.get_variant(name)
				if variant.axis in scope.selected_variants:
					if variant.name not in scope.selected_variants[variant.axis]:
						return False
		return True

	# Determine all variations selected by a scope.
	def _expand_variation_ids_in_scope(self, scope):
		if scope.selected_axes is None:
			axes = {var.axis for var in self.all_variants()}
		else:
			axes = scope.selected_axes

		variants = {}
		for axis in axes:
			if scope.selected_variants is None or axis not in scope.selected_variants:
				variants[axis] = {var.name for var in self.all_variants() if var.axis == axis}
			else:
				variants[axis] = scope.selected_variants[axis]

		variation_bundle = [ ]
		for axis_variants in variants.values():
			# Sort once so that variation order is deterministic.
			variant_list = sorted(axis_variants, key=lambda name: name if name is not None else '')
			variation_bundle.append(variant_list)

		# A variation is defined as a tuple of variants.
		def make_variation(prod):
			variant_filter = filter(lambda name: name is not None, prod)
			# Sort again so that order of the variants does not depend on the axes.
			variant_list = sorted(variant_filter)
			return tuple(variant_list)

		return [make_variation(prod) for prod in itertools.product(*variation_bundle)]

	def get_experiment_info(self, name):
		if name not in self._exp_infos:
			raise RuntimeError("Experiment {} does not exist".format(name))
		return self._exp_infos[name]

	def all_experiments(self):
		for exp_name, rev_name, var_names in self._expand_experiment_matrix():
			revision = self.get_revision(rev_name)
			variation = [self.get_variant(var_name) for var_name in var_names]
			yield Experiment(self, self.get_experiment_info(exp_name), revision, variation)

	def _expand_experiment_matrix(self):
		def expand(scope):
			# Determine all experiments selected by this scope.
			if scope.selected_exps is None:
				experiments = [exp_yml['name'] for exp_yml in self.yml['experiments']]
			else:
				experiments = scope.selected_exps

			# Helper to find all selected revisions for a given experiment.
			def revisions_for_experiment(exp_name):
				if scope.selected_revs is None:
					if 'use_builds' in self.get_experiment_info(exp_name)._exp_yml:
						for revision in self.all_revisions():
							yield revision.name
					else:
						yield None
				else:
					yield from scope.selected_revs

			variation_ids = self._expand_variation_ids_in_scope(scope)
			for exp_name in experiments:
				yield from itertools.product([exp_name], revisions_for_experiment(exp_name),
						variation_ids)

		expansion = MatrixScope.walk_matrix(self, self.yml, expand)
		return sorted(expansion)

	def _experiment_matches_item(self, item_yml, name, revision):
		if 'experiments' in item_yml:
			if name not in item_yml['experiments']:
				return False
		if revision is None:
			if 'revisions' in item_yml:
				return False
		else:
			if 'revisions' in item_yml:
				if revision.name not in item_yml['revisions']:
					return False
		return True

	def discover_all_runs(self):
		for exp in self.all_experiments():
			for inst_name, rep in self._expand_run_matrix(exp):
				instance = self.get_instance(inst_name)
				yield Run(self, exp, instance, rep)

	def _expand_run_matrix(self, exp):
		def expand(scope):
			if scope.selected_exps is not None:
				if exp.name not in scope.selected_exps:
					return
			if scope.selected_revs is not None:
				if exp.revision.name not in scope.selected_revs:
					return
			if scope.selected_variants is not None:
				variation_id = tuple(var.name for var in exp.variation)
				if variation_id not in self._expand_variation_ids_in_scope(scope):
					return

			if scope.selected_instsets is not None:
				instsets = scope.selected_instsets
			else:
				instset_combinations = [instance.instsets for instance in self.all_instances()]
				instsets = set().union(*instset_combinations)

			for instance in self.all_instances():
				if instsets.isdisjoint(instance.instsets):
					continue

				reps = range(0, 1)
				if scope.num_repetitions is not None:
					reps = range(0, scope.num_repetitions)
				elif 'repeat' in exp.info._exp_yml:
					reps = range(0, exp.info._exp_yml['repeat'])
				for rep in reps:
					yield (instance.filename, rep)

		expansion = MatrixScope.walk_matrix(self, self.yml, expand)
		return sorted(expansion)

	def collect_successful_results(self, parse_fn):
		"""
		Collects all success runs and parses their output.

		:param: parse_fn: Function to parse the output. Takes two parameters
			(run, f) where run is a :class:`simexpal.base.Run` object and f
			is a Python file object.
		"""

		res = [ ]
		for run in self.discover_all_runs():
			exp = run.experiment
			finished = os.access(run.output_file_path('status'), os.F_OK)
			if not finished:
				print("Skipping unfinished run {}/{}[{}]".format(run.experiment.name,
						run.instance.shortname, run.repetition))
				continue

			with open(run.output_file_path('status'), "r") as f:
				status_dict = yaml.load(f, Loader=yaml.Loader)
			if status_dict['timeout'] or status_dict['signal'] or status_dict['status'] > 0:
				print("Skipping failed run {}/{}[{}]".format(run.experiment.name,
						run.instance.shortname, run.repetition))
				continue

			with open(run.output_file_path('out'), 'r') as f:
				res.append(parse_fn(run, f))
		return res

class Instance:
	"""Represents a single instance"""

	def __init__(self, cfg, filename, inst_yml):
		self._cfg = cfg
		self.filename = filename
		self._inst_yml = inst_yml

	@property
	def config(self):
		return self._cfg

	@property
	def shortname(self):
		return os.path.splitext(self.filename)[0]

	@property
	def fullpath(self):
		return os.path.join(self._cfg.instance_dir(), self.filename)

	@property
	def instsets(self):
		if 'set' not in self._inst_yml:
			return set([None])
		if isinstance(self._inst_yml['set'], list):
			return set(self._inst_yml['set'])
		assert isinstance(self._inst_yml['set'], str)
		return set([self._inst_yml['set']])

	@property
	def repo(self):
		if 'repo' not in self._inst_yml:
			return None
		return self._inst_yml['repo']

	def check_available(self):
		return os.path.isfile(os.path.join(self._cfg.instance_dir(), self.filename))

	def install(self):
		if self.check_available():
			return

		util.try_mkdir(self._cfg.instance_dir())

		if 'repo' in self._inst_yml:
			if self._inst_yml['repo'] == 'local':
				return

		partial_path = os.path.join(self._cfg.instance_dir(), self.filename)
		if 'repo' in self._inst_yml:
			print("Downloading instance '{}' from {} repository".format(self.filename,
					self._inst_yml['repo']))

			instances.download_instance(self._inst_yml,
					self.config.instance_dir(), self.filename, partial_path, '.post0')
		else:
			assert 'generator' in self._inst_yml
			import subprocess

			def substitute(p):
				if p == 'INSTANCE_FILENAME':
					return self.filename
				raise RuntimeError("Unexpected parameter {}".format(p))

			print("Generating instance '{}'".format(self.filename))

			assert isinstance(self._inst_yml['generator']['args'], list)
			cmd = [util.expand_at_params(arg_tmpl, substitute) for arg_tmpl
					in self._inst_yml['generator']['args']]

			with open(partial_path + '.gen', 'w') as f:
				subprocess.check_call(cmd, cwd=self.config.basedir,
						stdout=f, stderr=subprocess.PIPE)
			os.rename(partial_path + '.gen', partial_path + '.post0')

		stage = 0
		if 'postprocess' in self._inst_yml:
			assert self._inst_yml['postprocess'] == 'to_edgelist'
			instances.convert_to_edgelist(self._inst_yml,
					partial_path + '.post0', partial_path + '.post1');
			os.unlink(partial_path + '.post0')
			stage = 1

		os.rename(partial_path + '.post{}'.format(stage), partial_path)

	def run_transform(self, transform, out_path):
		stage = 0
		assert transform == 'to_edgelist'
		instances.convert_to_edgelist(self._inst_yml,
				self.fullpath, out_path + '.transf1');
		stage = 1

		os.rename(out_path + '.transf{}'.format(stage), out_path)

class BuildInfo:
	def __init__(self, cfg, build_yml):
		self._cfg = cfg
		self._build_yml = build_yml

	@property
	def name(self):
		return self._build_yml['name']

	@property
	def requirements(self):
		if 'requires' in self._build_yml:
			for name in self._build_yml['requires']:
				yield name

	def traverse_requirements(self):
		# Perform a DFS to discover all recursively required builds.
		stack = []
		visited = set()

		for req_name in self.requirements:
			assert req_name not in visited
			req_info = self._cfg.get_build_info(req_name)
			stack.append(req_info)
			visited.add(req_name)

		while len(stack):
			current = stack.pop()
			yield current
			for req_name in current.requirements:
				if req_name in visited:
					continue
				req_info = self._cfg.get_build_info(req_name)
				stack.append(req_info)
				visited.add(req_name)

class Revision:
	def __init__(self, cfg, revision_yml):
		self._cfg = cfg
		self.revision_yml = revision_yml

	@property
	def name(self):
		return self.revision_yml['name']

	@property
	def specified_versions(self):
		return self.revision_yml['build_version'].keys()

	def version_for_build(self, build_name):
		return self.revision_yml['build_version'][build_name]

class Build:
	def __init__(self, cfg, info, revision):
		self._cfg = cfg
		self.info = info
		self.revision = revision

	@property
	def name(self):
		return self.info.name

	@property
	def clone_dir(self):
		rev = '@' + self.revision.name
		return os.path.join(self._cfg.basedir, 'builds', self.name + rev + '.clone')

	@property
	def compile_dir(self):
		rev = '@' + self.revision.name
		return os.path.join(self._cfg.basedir, 'builds', self.name + rev + '.compile')

	@property
	def prefix_dir(self):
		rev = '@' + self.revision.name
		return os.path.join(self._cfg.basedir, 'builds', self.name + rev)

class Variant:
	def __init__(self, cfg, axis, variant_yml):
		self._cfg = cfg
		self.axis = axis
		self.variant_yml = variant_yml

	@property
	def name(self):
		return self.variant_yml['name']

class ExperimentInfo:
	def __init__(self, cfg, exp_yml):
		self._cfg = cfg
		self._exp_yml = exp_yml

	@property
	def name(self):
		return self._exp_yml['name']

	@property
	def used_builds(self):
		if 'use_builds' in self._exp_yml:
			for name in self._exp_yml['use_builds']:
				yield name

class Experiment:
	"""
	Represents an experiment (see below).

	An experiment is defined as a combination of command line arguments
	and environment
	(from the experiment stanza in a experiments.yml file),
	a revision that is used to build the experiment's program
	and a set of variants (from the variants stanza in a experiments.yml file).
	"""

	def __init__(self, cfg, info, revision, variation):
		self._cfg = cfg
		self.info = info
		self.revision = revision
		self.variation = variation

	@property
	def name(self):
		return self.info.name

	@property
	def aux_subdir(self):
		var = ''
		if self.variation:
			var = '~' + ','.join([variant.name for variant in self.variation])
		rev = ''
		if self.revision:
			rev = '@' + self.revision.name
		return os.path.join(self._cfg.basedir, 'aux', self.name + var + rev)

	@property
	def output_subdir(self):
		var = ''
		if self.variation:
			var = '~' + ','.join([variant.name for variant in self.variation])
		rev = ''
		if self.revision:
			rev = '@' + self.revision.name
		return os.path.join(self._cfg.basedir, 'output', self.name + var + rev)

class Run:
	def __init__(self, cfg, experiment, instance, repetition):
		self._cfg = cfg
		self.experiment = experiment
		self.instance = instance
		self.repetition = repetition

	@property
	def config(self):
		return self._cfg

	# Contains auxiliary files that SHOULD NOT be necessary to determine the result of the run.
	def aux_file_path(self, ext):
		(fbase, _) = os.path.splitext(self.instance.filename)
		rep = ''
		if self.repetition > 0:
			rep = '[{}]'.format(self.repetition)
		return os.path.join(self.experiment.aux_subdir, fbase + '.' + ext + rep)

	# Contains the final output files; those SHOULD be all that is necessary to determine
	# if the run succeeded and to evaluate its result.
	def output_file_path(self, ext):
		(fbase, _) = os.path.splitext(self.instance.filename)
		rep = ''
		if self.repetition > 0:
			rep = '[{}]'.format(self.repetition)
		return os.path.join(self.experiment.output_subdir, fbase + '.' + ext + rep)

def read_and_validate_setup(basedir='.', setup_file='experiments.yml'):
	return util.validate_setup_file(os.path.join(basedir, setup_file))

def config_for_dir(basedir=None):
	if basedir is None:
		basedir = '.'
	yml = read_and_validate_setup(basedir=basedir)
	return Config(os.path.abspath(basedir), read_and_validate_setup(basedir=basedir))

