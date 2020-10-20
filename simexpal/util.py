
import errno
import os
import re
import shutil
import sys
import yaml
import json
from jsonschema import Draft7Validator
import warnings

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
	return setup_dict

def validate_setup_file(setup_file):
	""" Reads, validates and sanitizes the setup file
	"""

	def _validate_dict(dictionary, source, schema_path):
		with open(schema_path, 'r') as f:
			schema = json.load(f)

		validator = Draft7Validator(schema)
		validation_errors = list(validator.iter_errors(dictionary))

		if len(validation_errors) > 0:
			for err in validation_errors:
				err_source = "[{}]".format("][".join(str(x) for x in err.absolute_path))

				print("simexpal: Validation error in {} at {}:\n{}\n{}".format(
					source, err_source, err.instance, err.message), file=sys.stderr, end="\n\n")
			sys.exit(1)

	cur_file_path = os.path.abspath(os.path.dirname(__file__))

	exp_yml_dict = read_setup_file(setup_file)
	schema_path = os.path.join(cur_file_path, "schemes", "experiments.json")
	_validate_dict(exp_yml_dict, "experiments.yml", schema_path)

	try:
		launchers_yml_dict = read_setup_file(os.path.expanduser('~/.simexpal/launchers.yml'))
		schema_path = os.path.join(cur_file_path, "schemes", "launchers.json")
		_validate_dict(launchers_yml_dict, "launchers.yml", schema_path)
	except FileNotFoundError:
		pass

	for exp in exp_yml_dict.get('experiments', []):
		if exp.get('output', None) == 'stdout':
			msg = "Specifying the stdout path via 'output: stdout' is deprecated and will be removed in future " \
					"versions. Use 'stdout: out' instead."
			warnings.warn(msg, DeprecationWarning)

			break

	if 'instdir' not in exp_yml_dict:
		exp_yml_dict['instdir'] = './instances'

	return exp_yml_dict

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
