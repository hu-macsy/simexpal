
import errno
import os
import re
import shutil
import sys
import yaml

def expand_at_params(s, fn, listfn=None):
	def subfn(m):
		result = fn(m.group(1))
		if result is None:
			raise RuntimeError("Unexpected @-parameter {}".format(s))
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

did_warn_libyaml = False

def yaml_to_string(yml):
	return yaml.dump(yml, Dumper=yaml.SafeDumper)

def write_yaml_file(f, yml):
	return yaml.dump(yml, f, Dumper=yaml.SafeDumper)

def yaml_from_string(string):
	return yaml.load(string, Loader=yaml.SafeLoader)

def read_yaml_file(f):
	return yaml.load(f, Loader=yaml.SafeLoader)

def read_setup_file(setup_file):
	global did_warn_libyaml

	with open(setup_file, 'r') as f:
		Loader = yaml.SafeLoader
		try:
			Loader = yaml.CSafeLoader
		except AttributeError:
			if not did_warn_libyaml:
				print('simexpal: Using pure Python YAML parser.'
						' Installing libyaml will improve performance.', file=sys.stderr)
				did_warn_libyaml = True

		setup_dict = yaml.load(f, Loader=Loader)
	return setup_dict

def validate_setup_file(setup_file):
	""" Reads, validates and sanitizes the setup file
	"""

	setup_dict = read_setup_file(setup_file)

	if 'instdir' not in setup_dict:
		setup_dict['instdir'] = './instances';

	return setup_dict

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
