
import errno
import os
import re
import shutil
import yaml

def expand_at_params(s, fn, listfn=None):
	def subfn(m):
		result = fn(m.group(1))
		if result is None:
			raise RuntimeError("Unexpected @-parameter {}".format(p))
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

			seq.append(re.sub(r'@(\w+)@', subfn, item))
		return seq
	else:
		assert isinstance(s, str)
		return re.sub(r'@(\w+)@', subfn, s)

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
		if error.errno != errno.EEXIST:
			raise

def try_rmtree(path):
	try:
		shutil.rmtree(path)
	except OSError as error:
		if error.errno != errno.ENOENT:
			raise

def touch(path):
	with open(path, 'w') as f:
		pass

def read_setup_file(setup_file):
	with open(setup_file, 'r') as f:
		setup_dict = yaml.load(f, Loader=yaml.BaseLoader)
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

