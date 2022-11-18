
import errno
import os
import re
import shutil
import sys
import yaml
import json
import tempfile


def expand_at_params(s, fn, listfn=None):
	def subfn(m):
		result = fn(m.group(1))
		if result is None:
			raise RuntimeError("Unexpected @-parameter '{}' in {}".format(m.group(1), s))
		return result

	if isinstance(s, list):
		seq = [ ]
		for item in s:
			# Try to replace the whole item.
			if listfn is not None:
				m = re.fullmatch(r'@(\w+)@', item)
				if m:
					result = listfn(m.group(1))
					if result is not None:
						seq.extend(result)
						continue

			seq.append(re.sub(r'@(\w+(:[^@]+)?)@', subfn, item))
		return seq
	else:
		assert isinstance(s, str)
		return re.sub(r'@(\w+(:[^@]+)?)@', subfn, s)

def try_mkdir(path):
	try:
		os.mkdir(path)
	except OSError as error:
		if error.errno != errno.EEXIST:
			raise

def try_rmfile(path):
	try:
		os.remove(path)
	except OSError as error:
		if error.errno != errno.ENOENT:
			raise

def try_rmtree(path):
	try:
		shutil.rmtree(path)
	except OSError as error:
		if error.errno != errno.ENOENT:
			raise

def touch(path):
	with open(path, 'w'):
		pass

def yaml_to_string(yml):
	return yaml.dump(yml, Dumper=yaml.SafeDumper)

def write_yaml_file(f, yml):
	return yaml.dump(yml, f, Dumper=yaml.SafeDumper)

def yaml_from_string(string):
	from simexpal.base import YmlLoader
	return yaml.load(string, Loader=YmlLoader)

def read_yaml_file(f):
	from simexpal.base import YmlLoader
	return yaml.load(f, Loader=YmlLoader)

def read_setup_file(setup_file):
	from simexpal.base import YmlLoader

	with open(setup_file, 'r') as f:
		setup_dict = yaml.load(f, Loader=YmlLoader)
		last_mod = os.fstat(f.fileno()).st_mtime
	return setup_dict, last_mod

def read_json_file(json_file):
	with open(json_file, 'r') as f:
		json_dict = json.load(f)
		last_mod = os.fstat(f.fileno()).st_mtime
	return json_dict, last_mod

def validate_setup_file(basedir, setup_file, setup_file_schema_name):
	""" Reads, validates and sanitizes the setup file
	"""

	def _validate_dict(dictionary, source, schema):
		from jsonschema import Draft7Validator

		validator = Draft7Validator(schema)
		validation_errors = list(validator.iter_errors(dictionary))

		if len(validation_errors) > 0:
			for err in validation_errors:
				err_source = "[{}]".format("][".join(str(x) for x in err.absolute_path))

				print("simexpal: Validation error in {} at {}:\n{}\n{}".format(
					source, err_source, err.instance, err.message), file=sys.stderr, end="\n\n")

				# The error comes from subschemas in anyOf, oneOf or allOf.
				if err.context:
					print("Below are the validation errors of each respective subschema:")

					schema_index = None
					for sub_error in sorted(err.context, key=lambda e: e.schema_path[0]):
						cur_schema_index = sub_error.schema_path[0]
						if cur_schema_index != schema_index:
							schema_index = cur_schema_index
							print("\nValidation errors in subschema [{}]:".format(cur_schema_index))
						print(sub_error.message)
					print()
			return False
		return True

	cur_file_path = os.path.abspath(os.path.dirname(__file__))

	validation_cache_dict = {}
	try:
		with open(os.path.join(basedir, 'validation.cache'), 'r') as f:
			validation_cache_dict = json.load(f)
	except FileNotFoundError:
		pass

	# Validate setup file and potentially cache results.
	setup_file_path = os.path.join(basedir, setup_file)
	setup_file_dict, setup_file_last_mod = read_setup_file(setup_file_path)
	setup_file_schema_path = os.path.join(cur_file_path, 'schemes', setup_file_schema_name)
	setup_file_schema, setup_file_schema_last_mod = read_json_file(setup_file_schema_path)

	setup_file_is_valid = None
	if (setup_file not in validation_cache_dict
		or setup_file_last_mod != validation_cache_dict[setup_file]
		or setup_file_schema_name not in validation_cache_dict
		or setup_file_schema_last_mod != validation_cache_dict[setup_file_schema_name]):

		setup_file_is_valid = _validate_dict(setup_file_dict, setup_file, setup_file_schema)
		if setup_file_is_valid:
			validation_cache_dict[setup_file] = setup_file_last_mod
			validation_cache_dict[setup_file_schema_name] = setup_file_schema_last_mod

	# Validate launchers.yml file and potentially cache results.
	launchers_yml_is_valid = None
	try:
		launchers_yml_dict, launchers_yml_last_mod = read_setup_file(os.path.expanduser('~/.simexpal/launchers.yml'))
		launchers_yml_schema_path = os.path.join(cur_file_path, 'schemes', 'launchers.json')
		launchers_yml_schema, launchers_yml_schema_last_mod = read_json_file(launchers_yml_schema_path)

		if ('launchers.yml' not in validation_cache_dict
			or launchers_yml_last_mod != validation_cache_dict['launchers.yml']
			or launchers_yml_schema_last_mod != validation_cache_dict['launchers.json']):

			launchers_yml_is_valid = _validate_dict(launchers_yml_dict, 'launchers.yml', launchers_yml_schema)
			if launchers_yml_is_valid:
				validation_cache_dict['launchers.yml'] = launchers_yml_last_mod
				validation_cache_dict['launchers.json'] = launchers_yml_schema_last_mod
	except FileNotFoundError:
		pass

	writeback_cache = False
	do_exit = False
	if setup_file_is_valid is not None:
		if setup_file_is_valid:
			writeback_cache = True
		else:
			do_exit = True

	if launchers_yml_is_valid is not None:
		if launchers_yml_is_valid:
			writeback_cache = True
		else:
			do_exit = True

	if writeback_cache:
		fd, path = tempfile.mkstemp(dir=basedir)
		with os.fdopen(fd, 'w') as tmp:
			json.dump(validation_cache_dict, tmp)
		os.rename(path, 'validation.cache')

	if do_exit:
		sys.exit(1)

	return setup_file_dict

def compute_network_size(path, out):
	import networkit as nk
	try:
		g = nk.readGraph(path, nk.Format.EdgeList,
				separator=' ', firstNode=0, continuous=False, directed=False)
	except Exception: # Exception due the attempt of reading a non-network file
		return
	data = {
		'n': g.numberOfNodes(),
		'm': g.numberOfEdges()
	}
	yaml.dump(data, out, default_flow_style=False)

def ensure_list_type(arg):
	if isinstance(arg, list):
		return arg
	assert isinstance(arg, str)
	return [arg]

def read_file(path):
	try:
		f = open(path, 'r')
	except FileNotFoundError:
		return ''
	else:
		with f:
			return f.read()

def extract_file_prefix_from_path(file_path, suffix=None):
	"""

	:param file_path: absolute file path
	:param suffix: (optional) suffix which will be removed from the extensionless basename of the file
	:return: prefix of file
	"""

	prefix = os.path.splitext(os.path.basename(file_path))[0]
	if suffix is not None:
		prefix = prefix.split(suffix)[0]

	return prefix
