
from collections import OrderedDict
from enum import IntEnum
import itertools
import json
import os
import yaml
import sys
import tempfile
import warnings

from . import instances
from . import util

DEFAULT_DEV_BUILD_NAME = '_dev'
EXPERIMENTS_LIST_THRESHOLD = 30
TIMEOUT_GRACE_PERIOD = 30

did_warn_libyaml = False
YmlLoader = yaml.SafeLoader
try:
	YmlLoader = yaml.CSafeLoader
except AttributeError:
	if not did_warn_libyaml:
		print('simexpal: Using pure Python YAML parser.'
				' Installing libyaml will improve performance.', file=sys.stderr)
		did_warn_libyaml = True

def get_aux_subdir(base_dir, experiment, variation, revision):
	var = ''
	if variation:
		var = '~' + ','.join(variation)
	rev = ''
	if revision:
		rev = '@' + revision
	return os.path.join(base_dir, 'aux', experiment + var + rev)

def get_output_subdir(base_dir, experiment, variation, revision):
	var = ''
	if variation:
		var = '~' + ','.join(variation)
	rev = ''
	if revision:
		rev = '@' + revision
	return os.path.join(base_dir, 'output', experiment + var + rev)

def get_aux_file_name(ext, instance, repetition):
	rep = ''
	if repetition > 0:
		rep = '[{}]'.format(repetition)
	return instance + '.' + ext + rep

def get_output_file_name(ext, instance, repetition):
	rep = ''
	if repetition > 0:
		rep = '[{}]'.format(repetition)
	return instance + '.' + ext + rep

class MatrixScope:
	__slots__ = ['experiments', 'revisions', 'axes', 'variants', 'instsets', 'repetitions']

	def __init__(self):
		self.experiments = None
		self.revisions = None
		self.axes = None
		self.variants = None
		self.instsets = None
		self.repetitions = None

class MatrixSelection:
	__slots__ = ['experiments', 'revisions', 'variations', 'instances', 'repetitions']

class Config:
	"""Represents the entire configuration (i.e., an experiments.yml file)."""

	def __init__(self, basedir, yml):
		assert os.path.isabs(basedir)
		self.basedir = basedir
		self.yml = yml

		self.status_cache_path = basedir + '/status.cache'
		self.status_cache_dict = {}

		self._insts = OrderedDict()
		self._build_infos = OrderedDict()
		self._revisions = OrderedDict()
		self._variants = OrderedDict()
		self._exp_infos = OrderedDict()

		self._experiments_discovered = False
		self._experiments = OrderedDict()
		self._runs_discovered = False
		self._runs = OrderedDict()

		def check_for_reserved_name(name):
			if name.startswith('_'):
				raise RuntimeError(f"Names starting with an underscore are reserved for internal simexpal objects: {name}")

		def construct_instances():
			if 'instances' in self.yml:
				for inst_yml in self.yml['instances']:
					for idx in range(len(inst_yml['items'])):
						yield Instance(self, inst_yml, idx)

		def construct_variants():
			if 'variants' in self.yml:
				for axis_yml in self.yml['variants']:
					check_for_reserved_name(axis_yml['axis'])

					for variant_yml in axis_yml['items']:
						check_for_reserved_name(variant_yml['name'])

						yield Variant(self, axis_yml['axis'], variant_yml)

		for inst in sorted(construct_instances(), key=lambda inst: inst.shortname):
			if inst.shortname in self._insts:
				raise RuntimeError("The instance name '{}' is ambiguous".format(inst.shortname))
			self._insts[inst.shortname] = inst

		if 'builds' in self.yml:
			for build_yml in sorted(self.yml['builds'], key=lambda y: y['name']):
				check_for_reserved_name(build_yml['name'])

				if build_yml['name'] in self._build_infos:
					raise RuntimeError("The build name '{}' is ambiguous".format(build_yml['name']))
				self._build_infos[build_yml['name']] = BuildInfo(self, build_yml)

		if 'revisions' in self.yml:
			revision_list = []

			for revision_yml in self.yml['revisions']:
				if 'name' in revision_yml:
					check_for_reserved_name(revision_yml['name'])
				revision_list.append(Revision(self, revision_yml))

			for revision in sorted(revision_list, key=lambda y: y.name):
				if revision.name in self._revisions:
					raise RuntimeError("The revision name '{}' is ambiguous".format(revision.name))
				self._revisions[revision.name] = revision

		for variant in sorted(construct_variants(), key=lambda variant: variant.name):
			if variant.name in self._variants:
				raise RuntimeError("The variant name '{}' is ambiguous".format(variant.name))
			self._variants[variant.name] = variant

		if 'experiments' in self.yml:
			for exp_yml in sorted(self.yml['experiments'], key=lambda y: y['name']):
				check_for_reserved_name(exp_yml['name'])

				if exp_yml['name'] in self._exp_infos:
					raise RuntimeError("The experiment name '{}' is ambiguous".format(exp_yml['name']))
				self._exp_infos[exp_yml['name']] = ExperimentInfo(self, exp_yml)

		try:
			with open(self.status_cache_path, 'r') as f:
				self.status_cache_dict = json.load(f)
		except FileNotFoundError:
			pass

	def instance_dir(self):
		"""Path of the directory that stores all the instances."""
		return os.path.join(self.basedir, self.yml['instdir'])

	def all_instance_ids(self):
		for inst in self.all_instances():
			yield inst.shortname

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

	def all_non_dev_revisions(self):
		for revision in self.all_revisions():
			if not revision.is_dev_build:
				yield revision

	def all_dev_revisions(self):
		for revision in self.all_revisions():
			if revision.is_dev_build:
				yield revision

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

	def all_non_dev_builds(self):
		for build in self.all_builds():
			if not build.revision.is_dev_build:
				yield build

	def all_dev_builds(self):
		for build in self.all_builds():
			if build.revision.is_dev_build:
				yield build

	def all_builds_for_revision(self, revision):
		for build in self.all_builds():
			if build.revision == revision:
				yield build

	def get_build(self, name, revision):
		for build in self.all_builds(): # TODO: Avoid a quadratic blowup.
			if build.name == name and build.revision == revision:
				return build
		raise RuntimeError("Build '{}' does not exist in revision '{}'".format(name, revision.name))

	def all_variants(self):
		yield from self._variants.values()

	def all_variants_for_axis(self, axis):
		for var in self.all_variants():
			if var.axis == axis:
				yield var

	def get_variant(self, name):
		if name not in self._variants:
			raise RuntimeError("Variant {} does not exist".format(name))
		return self._variants[name]

	def all_experiment_infos(self):
		yield from self._exp_infos.values()

	def get_experiment_info(self, name):
		if name not in self._exp_infos:
			raise RuntimeError("Experiment {} does not exist".format(name))
		return self._exp_infos[name]

	def _fill_experiments(self):

		def extract_experiments(selection):
			def revisions_for_experiment(exp_info):
				if 'use_builds' in exp_info._exp_yml:
					if selection.revisions is not None:
						yield from selection.revisions
					else:
						yield from self.all_revisions()
				else:
					yield None

			for exp_info in selection.experiments:
				yield from itertools.product([exp_info], revisions_for_experiment(exp_info), selection.variations)

		key = lambda x: (x[0].name, x[1].name if x[1] is not None else '_none',
						[sub_var.name for sub_var in x[2]])

		for exp_info, revision, variation in self._expand_matrix(extract_experiments, key=key):
			self._experiments[(exp_info, revision, variation)] = Experiment(self, exp_info, revision, variation)

		self._experiments_discovered = True

	def all_experiments(self):

		if not self._experiments_discovered:
			self._fill_experiments()

		yield from self._experiments.values()

	def _fill_runs(self):

		def extract_runs(selection):
			# Helper to find all selected revisions for a given experiment.
			def revisions_for_experiment(exp_info):
				if 'use_builds' in exp_info._exp_yml:
					if selection.revisions is not None:
						yield from selection.revisions
					else:
						yield from self.all_revisions()
				else:
					yield None

			for exp_info in selection.experiments:
				for revision in revisions_for_experiment(exp_info):
					for variation in selection.variations:
						for instance in selection.instances:
							if selection.repetitions is not None:
								reps = range(0, selection.repetitions)
							elif exp_info.repeat is not None:
								reps = range(0, exp_info.repeat)
							else:
								reps = range(0, 1)
							for rep in reps:
								yield (self._experiments[(exp_info, revision, variation)], instance, rep)
		key = lambda t: (t[0].name, t[0].revision.name if t[0].revision is not None else '_none',
						[sub_var.name for sub_var in t[0].variation], t[1].shortname, t[2])

		if not self._experiments_discovered:
			self._fill_experiments()

		for experiment, instance, rep in self._expand_matrix(extract_runs, key=key):
			self._runs[(experiment, instance, rep)] = Run(self, experiment, instance, rep)

		self._runs_discovered = True

	def discover_all_runs(self):

		if not self._runs_discovered:
			self._fill_runs()

		yield from self._runs.values()

	def collect_successful_results(self, parse_fn=None):
		"""
		Collects all successful runs and optionally parses their output.

		:param parse_fn: Function to parse the output. Takes two parameters
			``(run, f)`` where ``run`` is a :class:`simexpal.base.Run` object
			and ``f`` is a Python file object.
		:return: list of parsed outputs if ``parse_fn`` is given,
			generator of successful :class:`simexpal.base.Run` objects otherwise
		"""

		def successful_runs(verbose=False):
			for run in self.discover_all_runs():
				finished = os.access(run.output_file_path('status'), os.F_OK)
				if not finished:
					if verbose:
						print("Skipping unfinished run {}/{}[{}]".format(run.experiment.name,
																		run.instance.shortname, run.repetition))
					continue

				if run.get_status().is_negative:
					if verbose:
						print("Skipping failed run {}/{}[{}]".format(run.experiment.name,
																	run.instance.shortname, run.repetition))
					continue
				yield run
			self.writeback_status_cache()

		if parse_fn:
			msg = "Calling 'Config.collect_successful_results()' with a parse function is deprecated and will be " \
					"removed in future versions. Instead, call it without any parameters and it will return a " \
					"generator of successful simexpal.base.Run objects."
			warnings.warn(msg, DeprecationWarning)

			res = []
			for run in successful_runs(verbose=True):
				with open(run.output_file_path('out'), 'r') as f:
					res.append(parse_fn(run, f))
			self.writeback_status_cache()
			return res
		else:
			return successful_runs()

	def export_experiments(self, included_statuses=None):
		"""
		Exports experiments based on their status.

		:param included_statuses: List of :class:`simexpal.base.Status` objects which get exported.
			Alternatively an integer list can be used, where the following translation is used:
			0 - not submitted,
			1 - in submission,
			2 - submitted,
			3 - started,
			4 - finished,
			5 - timeout,
			6 - killed,
			7 - failed.

		:return: List of (``exp_name``, ``variation-tuple``, ``inst_shortname``, ``status``)-tuples
		"""
		experiment_list = []

		if included_statuses is not None:
			for run in self.discover_all_runs():
				status = run.get_status()
				if status in included_statuses:
					experiment_list.append((
						run.experiment.name,
						tuple(variant.name for variant in run.experiment.variation),
						run.instance.shortname,
						str(status)
					))
		self.writeback_status_cache()
		return experiment_list

	def export_successful_experiments(self):
		return self.export_experiments([s for s in Status if s.is_positive])

	def export_failed_experiments(self):
		return self.export_experiments([s for s in Status if s.is_negative])

	# -----------------------------------------------------------------------------------
	# Matrix expansion.
	# -----------------------------------------------------------------------------------

	# Main function to expand information from the matrix.
	# Calls the 'extract' function on all scopes of the matrix and returns the union
	# of all iterables that were produced by 'extract'.
	# Sorts (and deduplicates) the output according to the key.
	def _expand_matrix(self, extract, key=None):
		if key is None:
			key = lambda ent: ent

		def extract_included(parent, yml):
			scope = self._restrict_scope(parent, yml)

			if 'include' in yml:
				for incl_yml in yml['include']:
					yield from extract_included(scope, incl_yml)
			else:
				sel = self._get_selection_from_scope(scope)
				yield from extract(sel)

		def generate_unordered_expansion():
			scope = MatrixScope()

			if 'matrix' in self.yml:
				yield from extract_included(scope, self.yml['matrix'])
			else:
				sel = self._get_selection_from_scope(scope)
				yield from extract(sel)

		# Perform sorting and deduplication according to the key.
		ordered = sorted(generate_unordered_expansion(), key=key)
		return (next(grp) for _, grp in itertools.groupby(ordered, key=key))

	def _restrict_scope(self, parent, yml):
		def restrict_set(broad, narrow):
			if narrow is None:
				return broad
			if broad is None:
				return set(narrow)
			return broad.intersection(narrow)

		scope = MatrixScope()
		scope.experiments = restrict_set(parent.experiments,
				yml.get('experiments', None))
		scope.revisions = restrict_set(parent.revisions,
				yml.get('revisions', None))
		scope.axes = restrict_set(parent.axes,
				yml.get('axes', None))
		scope.variants = restrict_set(parent.variants,
				yml.get('variants', None))
		scope.instsets = restrict_set(parent.instsets,
				yml.get('instsets', None))
		scope.repetitions = restrict_set(parent.repetitions,
				range(yml['repetitions']) if 'repetitions' in yml else None)
		return scope

	# Finds all experiments, revisions, etc. that are selected by a given scope.
	def _get_selection_from_scope(self, scope):
		sel = MatrixSelection()
		sel.experiments = self._get_selected_experiments(scope)
		sel.revisions = self._get_selected_revisions(scope)
		sel.instances = self._get_selected_instances(scope)
		sel.repetitions = self._get_selected_repetitions(scope)
		sel.variations = self._get_selected_variations(scope)

		return sel

	# Determine all experiments selected by a scope.
	def _get_selected_experiments(self, scope):
		if scope.experiments is not None:
			return [self.get_experiment_info(experiment) for experiment in scope.experiments]
		else:
			return list(self.all_experiment_infos())

	# Determine all revisions selected by a scope.
	def _get_selected_revisions(self, scope):
		if scope.revisions is not None:
			return [self.get_revision(revision) for revision in scope.revisions]
		return None

	# Determine all instances selected by a scope.
	def _get_selected_instances(self, scope):
		if scope.instsets is not None:
			return [inst for inst in self.all_instances() if not scope.instsets.isdisjoint(inst.instsets)]
		else:
			return list(self.all_instances())

	# Determine the number of repetitions selected by a scope.
	def _get_selected_repetitions(self, scope):
		if scope.repetitions is not None:
			return len(scope.repetitions)
		return None

	# Determine all variations selected by a scope.
	def _get_selected_variations(self, scope):

		def scope_selects_all_variants_of_axis(axis):
			if scope.variants is not None:
				for var in self.all_variants_for_axis(axis):
					if var.name in scope.variants:
						return False
			return True

		if scope.axes is None:
			axes = {var.axis for var in self.all_variants()}
		else:
			axes = scope.axes

		variants = {}
		for axis in axes:
			if scope.variants is None or scope_selects_all_variants_of_axis(axis):
				variants[axis] = {var.name for var in self.all_variants_for_axis(axis)}
			else:
				variants[axis] = {var_name for var_name in scope.variants if self.get_variant(var_name).axis == axis}

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
			return tuple([self.get_variant(variant) for variant in variant_list])

		return [make_variation(prod) for prod in itertools.product(*variation_bundle)]

	def writeback_status_cache(self):
		fd, path = tempfile.mkstemp(dir=self.basedir)
		with os.fdopen(fd, 'w') as tmp:
			json.dump(self.status_cache_dict, tmp)
		os.rename(path, self.status_cache_path)

class Instance:
	"""Represents a single instance"""

	def __init__(self, cfg, inst_yml, index):
		self._cfg = cfg
		self._inst_yml = inst_yml
		self.index = index

	@property
	def filename(self):
		msg = "The 'Instance.filename' attribute is deprecated and will be removed in future versions."
		warnings.warn(msg, DeprecationWarning)

		return self.filenames[0]

	@property
	def yml_name(self):
		if isinstance(self._inst_yml['items'][self.index], dict):
			assert 'name' in self._inst_yml['items'][self.index]

			return self._inst_yml['items'][self.index]['name']

		return self._inst_yml['items'][self.index]

	@property
	def has_multi_ext(self):
		return 'extensions' in self._inst_yml

	@property
	def has_multi_files(self):
		if isinstance(self._inst_yml['items'][self.index], dict):
			return 'files' in self._inst_yml['items'][self.index]
		return False

	@property
	def extensions(self):
		assert self.has_multi_ext
		return self._inst_yml['extensions']

	@property
	def config(self):
		return self._cfg

	@property
	def shortname(self):
		return os.path.splitext(self.yml_name)[0]

	@property
	def fullpath(self):
		return os.path.join(self._cfg.instance_dir(), self.unique_filename)

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

	@property
	def filenames(self):
		if self.has_multi_ext:
			return [self.yml_name + '.' + ext for ext in self._inst_yml['extensions']]
		elif self.has_multi_files:
			return [file for file in self._inst_yml['items'][self.index]['files']]
		else:
			return [self.yml_name]

	@property
	def unique_filename(self):
		if len(self.filenames) > 1:
			raise RuntimeError("The instance '{}' does not have a unique filename.".format(self.yml_name))
		return self.filenames[0]

	def check_available(self):
		for file in self.filenames:
			if not os.path.isfile(os.path.join(self._cfg.instance_dir(), file)):
				return False
		return True

	def install(self):
		if self.check_available():
			return

		util.try_mkdir(self._cfg.instance_dir())

		if 'repo' in self._inst_yml:
			if self._inst_yml['repo'] == 'local':
				return

		partial_path = os.path.join(self._cfg.instance_dir(), self.unique_filename)
		if 'repo' in self._inst_yml:
			print("Downloading instance '{}' from {} repository".format(self.unique_filename,
					self._inst_yml['repo']))

			instances.download_instance(self._inst_yml,
					self.config.instance_dir(), self.unique_filename, partial_path, '.post0')
		else:
			assert 'generator' in self._inst_yml
			import subprocess

			def substitute(p):
				if p == 'INSTANCE_FILENAME':
					return self.unique_filename
				raise RuntimeError("Unexpected parameter {}".format(p))

			print("Generating instance '{}'".format(self.unique_filename))

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
					partial_path + '.post0', partial_path + '.post1')
			os.unlink(partial_path + '.post0')
			stage = 1

		os.rename(partial_path + '.post{}'.format(stage), partial_path)

	def run_transform(self, transform, out_path):
		assert transform == 'to_edgelist'
		instances.convert_to_edgelist(self._inst_yml,
				self.fullpath, out_path + '.transf1')
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
			if isinstance(self._build_yml['requires'], list):
				for name in self._build_yml['requires']:
					yield name
			else:
				assert isinstance(self._build_yml['requires'], str)
				yield self._build_yml['requires']

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

	@property
	def exports_python(self):
		if 'exports_python' not in self._build_yml:
			return []
		return [self._build_yml['exports_python']]

	@property
	def configure(self):
		return self._build_yml.get('configure', [])

	@property
	def compile(self):
		return self._build_yml.get('compile', [])

	@property
	def install(self):
		return self._build_yml.get('install', [])

	@property
	def git_repo(self):
		return self._build_yml.get('git', '')

	@property
	def recursive_clone(self):
		return self._build_yml.get('recursive-clone', False)

	@property
	def regenerate(self):
		return self._build_yml.get('regenerate', [])

	@property
	def extra_paths(self):
		return self._build_yml.get('extra_paths', [])

class Revision:
	def __init__(self, cfg, revision_yml):
		self._cfg = cfg
		self.revision_yml = revision_yml

	@property
	def name(self):
		if 'name' not in self.revision_yml:
			return DEFAULT_DEV_BUILD_NAME
		return self.revision_yml['name']

	@property
	def specified_versions(self):
		return self.revision_yml['build_version'].keys()

	def version_for_build(self, build_name):
		return self.revision_yml['build_version'][build_name]

	@property
	def is_dev_build(self):
		return self.revision_yml.get('develop', False)

	@property
	def is_default_dev_build(self):
		return self.name == DEFAULT_DEV_BUILD_NAME

class Build:
	def __init__(self, cfg, info, revision):
		self._cfg = cfg
		self.info = info
		self.revision = revision

	@property
	def name(self):
		return self.info.name

	def _get_dev_build_suffix(self):
		if self.revision.is_default_dev_build:
			return ''
		else:
			return '@' + self.revision.name

	@property
	def repo_dir(self):
		# Use the source_dir property for dev-build revisions
		assert not self.revision.is_dev_build

		return os.path.join(self._cfg.basedir, 'builds', self.name + '.repo')

	@property
	def clone_dir(self):
		# Use the source_dir property for dev-build revisions
		assert not self.revision.is_dev_build

		rev = '@' + self.revision.name
		return os.path.join(self._cfg.basedir, 'builds', self.name + rev + '.clone')

	@property
	def compile_dir(self):
		if self.revision.is_dev_build:
			rev = self._get_dev_build_suffix()
			return os.path.join(self._cfg.basedir, 'dev-builds', self.name + rev + '.compile')
		rev = '@' + self.revision.name
		return os.path.join(self._cfg.basedir, 'builds', self.name + rev + '.compile')

	@property
	def prefix_dir(self):
		if self.revision.is_dev_build:
			rev = self._get_dev_build_suffix()
			return os.path.join(self._cfg.basedir, 'dev-builds', self.name + rev)
		rev = '@' + self.revision.name
		return os.path.join(self._cfg.basedir, 'builds', self.name + rev)

	@property
	def source_dir(self):
		"""
			dev-builds only have a source directory instead of a repo and clone directory
		"""
		assert self.revision.is_dev_build

		rev = self._get_dev_build_suffix()
		return os.path.join(self._cfg.basedir, 'develop', self.name + rev)

	def is_checked_out(self):
		if self.revision.is_dev_build:
			return os.access(os.path.join(self.source_dir, 'checkedout.simexpal'), os.F_OK)
		return os.access(os.path.join(self.clone_dir, 'checkedout.simexpal'), os.F_OK)

	def is_regenerated(self):
		if self.revision.is_dev_build:
			return os.access(os.path.join(self.source_dir, 'regenerated.simexpal'), os.F_OK)
		return os.access(os.path.join(self.clone_dir, 'regenerated.simexpal'), os.F_OK)

	def is_configured(self):
		return os.access(os.path.join(self.compile_dir, 'configured.simexpal'), os.F_OK)

	def is_compiled(self):
		return os.access(os.path.join(self.compile_dir, 'compiled.simexpal'), os.F_OK)

	def is_installed(self):
		return os.access(os.path.join(self.prefix_dir, 'installed.simexpal'), os.F_OK)

	def purge(self, delete_source=False):
		if not self.revision.is_dev_build:
			util.try_rmtree(self.clone_dir)
		elif delete_source:
			util.try_rmtree(self.source_dir)

		util.try_rmtree(self.compile_dir)
		util.try_rmtree(self.prefix_dir)

def extract_process_settings(yml):
	if 'num_nodes' not in yml:
		return None
	return {
		'num_nodes': yml['num_nodes'],
		'procs_per_node': yml.get('procs_per_node', None)
	}

def extract_thread_settings(yml):
	if 'num_threads' not in yml:
		return None
	return {
		'num_threads': yml['num_threads']
	}

class Variant:
	def __init__(self, cfg, axis, variant_yml):
		self._cfg = cfg
		self.axis = axis
		self.variant_yml = variant_yml

	@property
	def name(self):
		return self.variant_yml['name']

	@property
	def process_settings(self):
		return extract_process_settings(self.variant_yml)

	@property
	def thread_settings(self):
		return extract_thread_settings(self.variant_yml)

	@property
	def slurm_args(self):
		return self.variant_yml.get('slurm_args', [])

	@property
	def launcher(self):
		return self.variant_yml.get('launcher', None)

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

	@property
	def process_settings(self):
		return extract_process_settings(self._exp_yml)

	@property
	def thread_settings(self):
		return extract_thread_settings(self._exp_yml)

	@property
	def slurm_args(self):
		return self._exp_yml.get('slurm_args', [])

	@property
	def timeout(self):
		return self._exp_yml.get('timeout', None)

	@property
	def output(self):
		return self._exp_yml.get('output', None)

	@property
	def output_extensions(self):
		if 'output' in self._exp_yml:
			if isinstance(self._exp_yml['output'], dict):
				return set(self._exp_yml['output'].get('extensions', []) + ['out'])
		return {'out'}

	@property
	def stdout(self):
		return self._exp_yml.get('stdout', None)

	@property
	def workdir(self):
		return self._exp_yml.get('workdir', None)

	@property
	def args(self):
		return self._exp_yml.get('args')

	@property
	def environ(self):
		return self._exp_yml.get('environ', {})

	@property
	def repeat(self):
		return self._exp_yml.get('repeat', None)

	@property
	def launcher(self):
		return self._exp_yml.get('launcher', None)

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
		return get_aux_subdir(self._cfg.basedir, self.name,
				[variant.name for variant in self.variation],
				self.revision.name if self.revision else None)

	@property
	def output_subdir(self):
		return get_output_subdir(self._cfg.basedir, self.name,
				[variant.name for variant in self.variation],
				self.revision.name if self.revision else None)

	@property
	def effective_process_settings(self):
		s = None
		for variant in self.variation:
			vs = variant.process_settings
			if not vs:
				continue
			if s:
				raise RuntimeError("Process settings for experiments '{}' overridden by multiple variants: {}".format(
					self.name, [s.name, variant.name]
				))
			s = variant

		if s is not None:
			return s.process_settings
		return self.info.process_settings

	@property
	def effective_thread_settings(self):
		s = None
		for variant in self.variation:
			vs = variant.thread_settings
			if not vs:
				continue
			if s:
				raise RuntimeError("Thread settings for experiments '{}' overridden by multiple variants: {}".format(
					self.name, [s.name, variant.name]
				))
			s = variant

		if s is not None:
			return s.thread_settings
		return self.info.thread_settings

	@property
	def display_name(self):
		display_name = self.name
		if self.variation:
			display_name += ' ~ ' + ', '.join([variant.name for variant in self.variation])
		if self.revision:
			display_name += ' @ ' + self.revision.name
		return display_name

	@property
	def effective_slurm_args(self):
		s = None
		for variant in self.variation:
			slurm_args = variant.slurm_args
			if not slurm_args:
				continue
			if s:
				raise RuntimeError("Extra slurm arguments for experiment '{}' overridden by multiple variants: {}".format(
					self.name, [s.name, variant.name]
				))
			s = variant

		if s is not None:
			return s.slurm_args
		return self.info.slurm_args

	@property
	def effective_launcher(self):
		s = None
		for variant in self.variation:
			variant_launcher = variant.launcher
			if not variant_launcher:
				continue
			if s:
				raise RuntimeError("Selected launcher for experiment '{}' overridden by multiple variants: {}".format(
					self.name, [s.name, variant.name]
				))
			s = variant

		if s is not None:
			return s.launcher
		return self.info.launcher

class Status(IntEnum):
	NOT_SUBMITTED = 0
	IN_SUBMISSION = 1
	SUBMITTED = 2
	STARTED = 3
	FINISHED = 4
	TIMEOUT = 5
	KILLED = 6
	FAILED = 7

	def __str__(self):
		if self.value == Status.NOT_SUBMITTED:
			return 'not submitted'
		if self.value == Status.SUBMITTED:
			return 'submitted'
		if self.value == Status.IN_SUBMISSION:
			return 'in submission'
		if self.value == Status.STARTED:
			return 'started'
		if self.value == Status.FINISHED:
			return 'finished'
		if self.value == Status.TIMEOUT:
			return 'timeout'
		if self.value == Status.KILLED:
			return 'killed'
		if self.value == Status.FAILED:
			return 'failed'

	@property
	def is_positive(self):
		return self.value == Status.FINISHED

	@property
	def is_neutral(self):
		return self.value in [Status.IN_SUBMISSION, Status.SUBMITTED, Status.STARTED]

	@property
	def is_negative(self):
		return self.value in [Status.TIMEOUT, Status.KILLED, Status.FAILED]

class Run:
	def __init__(self, cfg, experiment, instance, repetition):
		self._cfg = cfg
		self.experiment = experiment
		self.instance = instance
		self.repetition = repetition

	@property
	def config(self):
		return self._cfg

	@property
	def internal_name(self):
		internal_name = self.experiment.name
		if self.experiment.variation:
			internal_name += '~' + ','.join([variant.name for variant in self.experiment.variation])
		if self.experiment.revision:
			internal_name += '@' + self.experiment.revision.name
		if self.repetition:
			internal_name += '[{}]'.format(self.repetition)
		return internal_name

	# Contains auxiliary files that SHOULD NOT be necessary to determine the result of the run.
	def aux_file_path(self, ext):
		return os.path.join(self.experiment.aux_subdir,
				get_aux_file_name(ext, self.instance.shortname, self.repetition))

	# Contains the final output files; those SHOULD be all that is necessary to determine
	# if the run succeeded and to evaluate its result.
	def output_file_path(self, ext):
		return os.path.join(self.experiment.output_subdir,
				get_output_file_name(ext, self.instance.shortname, self.repetition))

	def _update_status_cache_dict(self):

		# Determine status cache entry.
		status, last_mod = Status.NOT_SUBMITTED, None
		try:
			with open(self.output_file_path('status'), 'r') as f:
				status_dict = yaml.load(f, Loader=YmlLoader)
				last_mod = os.fstat(f.fileno()).st_mtime

			if status_dict['timeout']:
				status = Status.TIMEOUT
			elif status_dict['signal']:
				status = Status.KILLED
			elif status_dict['status'] > 0:
				status = Status.FAILED
			else:
				status = Status.FINISHED
		except FileNotFoundError:
			if os.access(self.output_file_path('out'), os.F_OK):
				status, last_mod = Status.STARTED, os.stat(self.output_file_path('out')).st_mtime
			elif os.access(self.aux_file_path('run'), os.F_OK):
				status, last_mod = Status.SUBMITTED, os.stat(self.aux_file_path('run')).st_mtime
			elif os.access(self.aux_file_path('lock'), os.F_OK):
				status, last_mod = Status.IN_SUBMISSION, os.stat(self.aux_file_path('lock')).st_mtime

		internal_name = self.internal_name
		if internal_name not in self._cfg.status_cache_dict:
			self._cfg.status_cache_dict[internal_name] = {
				self.instance.shortname: {'status': status, 'last_mod': last_mod}}
		else:
			self._cfg.status_cache_dict[internal_name][self.instance.shortname] = {
				'status': status, 'last_mod': last_mod}

		return status

	def purge_status_cache_dict(self):
		try:
			del self._cfg.status_cache_dict[self.internal_name][self.instance.shortname]
		except KeyError:
			pass

	def get_status(self):

		internal_name = self.internal_name
		if internal_name in self._cfg.status_cache_dict:
			if self.instance.shortname in self._cfg.status_cache_dict[internal_name]:
				cache_entry = self._cfg.status_cache_dict[internal_name][self.instance.shortname]

				last_mod = None
				last_mod_source = None
				try:
					last_mod = os.stat(self.output_file_path('status')).st_mtime
					last_mod_source = 'status'
				except FileNotFoundError:
					try:
						last_mod = os.stat(self.output_file_path('out')).st_mtime
						last_mod_source = 'out'
					except FileNotFoundError:
						try:
							last_mod = os.stat(self.aux_file_path('run')).st_mtime
							last_mod_source = 'run'
						except FileNotFoundError:
							try:
								last_mod = os.stat(self.aux_file_path('lock')).st_mtime
								last_mod_source = 'lock'
							except FileNotFoundError:
								pass

				if last_mod == cache_entry["last_mod"]:

					# Verify that the file with the same last modification time truly produced this
					# cache entry by matching the cached status with the source it originated from.
					status = Status(cache_entry["status"])
					if (status.is_positive or status.is_negative) and last_mod_source == 'status':
						return status
					elif status == Status.STARTED and last_mod_source == 'out':
						return status
					elif status == Status.SUBMITTED and last_mod_source == 'run':
						return status
					elif status == Status.IN_SUBMISSION and last_mod_source == 'lock':
						return status
					elif status == Status.NOT_SUBMITTED and last_mod_source is None:
						return status

		return self._update_status_cache_dict()

	def output_file_path_from_yml(self):
		def get_qualified_output_file(ext):
			if ext not in self.experiment.info.output_extensions:
				raise RuntimeError(
					f"Unexpected output extension for experiment '{self.experiment.name}': .{ext}\n"
				)
			return self.output_file_path(ext)

		if self.experiment.info.output == 'stdout':
			return self.output_file_path('out')
		elif self.experiment.info.stdout is not None:
			return get_qualified_output_file(self.experiment.info.stdout)

		return self.aux_file_path('stdout')

	def open_output_file(self):
		try:
			return open(self.output_file_path_from_yml())
		except FileNotFoundError:
			raise RuntimeError("The experiment '{}' with instance '{}' has not been started yet".format(
				self.experiment.display_name, self.instance.shortname))

def read_and_validate_setup(basedir='.', setup_file='experiments.yml'):
	return util.validate_setup_file(os.path.join(basedir, setup_file))

def config_for_dir(basedir=None):
	if basedir is None:
		basedir = '.'
	yml = read_and_validate_setup(basedir=basedir)
	return Config(os.path.abspath(basedir), yml)

