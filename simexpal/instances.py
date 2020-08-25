
import gzip
import os
import requests
import tarfile
import zipfile

from .util import try_mkdir

class DownloadException(Exception):
	pass

repos = {
	'konect': {
		'url': 'http://konect.cc/files/download.tsv.',
		'file_fmt': '.tar.bz2',
	},
	'snap': {
			'url': 'https://snap.stanford.edu/data/',
			'file_fmt': '.txt.gz'
	},
	'network_repository': {
		'url': 'http://nrvis.com/download/data/',
		'file_fmt': '.zip'
	}
}

def download_instance(inst_yml, instances_dir, filename, partial_path, ext):
	repo = inst_yml['repo']

	try_mkdir(instances_dir)

	# Download the instance from the repository.
	prefix = ''
	if 'repo-subdir' in inst_yml:
		prefix = inst_yml['repo-subdir'] + '/'
	fmt = repos[repo]['file_fmt']
	url = repos[repo]['url'] + prefix + filename + fmt

	download_path = os.path.join(instances_dir, filename + '.download')
	request = requests.get(url)
	with open(download_path, 'wb') as f:
		f.write(request.content)

	# Decompress the instance.
	def extract(reader, f):
		f.write(reader.read())

	tmp_path = os.path.join(instances_dir, filename + '.tmp')
	compression = fmt.split('.')[-1]
	if repo == 'konect':
		tar = tarfile.open(download_path, 'r:' + compression)
		member_name = next(elem for elem in tar.getnames() if 'out.' in elem)

		with tar.extractfile(member_name) as reader:
			with open(tmp_path, 'wb') as f:
				extract(reader, f)
	elif repo == 'snap':
		with gzip.open(download_path, 'rb') as reader:
			with open(tmp_path, 'wb') as f:
				extract(reader, f)
	elif repo == 'network_repository':
		zip_file = zipfile.ZipFile(download_path + compression, 'r')
		# TODO finish
	else:
		DownloadException('Unknown repository: ' + repo)

	os.unlink(download_path)
	os.rename(tmp_path, partial_path + ext)

# Reformats the network to a SNAP/EdgeList format.
def convert_to_edgelist(inst_yml, in_path, out_path):
	repo = inst_yml['repo']

	if repo == 'konect':
		separator = ' '
		commentPrefix = '%'
	elif repo == 'snap':
		separator = '\t'
		commentPrefix = '#'

	def get_other_separator(separator):
		if separator == ' ':
			return '\t'
		return ' '
	with open(in_path, 'r') as in_f:
		with open(out_path, 'w') as out_f:
			for line in in_f:
				if line.startswith(commentPrefix):
					continue
				split_line = line.strip().split(separator)
				if len(split_line) < 2:
					separator = get_other_separator(separator)
					split_line = line.strip().split(separator)
					if len(split_line) < 2:
						raise Exception("Unknown separator: " + line.strip())
				split_line = [x for x in filter(lambda x: len(x) > 0, split_line)]
				(u, v) = split_line[0], split_line[1]
				out_f.write("{:s} {:s}\n".format(u, v))

