
import gzip
import os
import sys
import zipfile

from .util import try_mkdir, expand_at_params

class DownloadException(Exception):
	pass

repos = {
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
	import requests

	def download_as_stream(url, download_path):
		with requests.get(url, stream=True) as request:
			content_length = request.headers.get('content-length')
			with open(download_path, 'wb') as f:
				if content_length is not None:
					content_length = int(content_length)
					downloaded = 0
					progress = -1
					for chunk in request.iter_content(chunk_size=1000000):
						f.write(chunk)

						downloaded += len(chunk)
						if sys.stdout.isatty():
							# We are running in a terminal.
							done = int(50*downloaded/content_length)
							sys.stdout.write("\r[{}{}]{}% ({:.2f}MB/{:.2f}MB)".format(
								'='*done, ' '*(50-done), 2*done, downloaded/2**20, content_length/2**20))
							sys.stdout.flush()
						else:
							done = int(10*downloaded/content_length)
							# Only draw a new progress bar when at least 10% progress was made or we are in the first
							# iteration of this loop.
							if done > progress:
								sys.stdout.write("[{}{}]{}% ({:.2f}MB/{:.2f}MB)\n".format(
									'='*done, ' '*(10-done), 10*done, downloaded/2**20, content_length/2**20))
								sys.stdout.flush()
							progress = done
					print()
				else:
					for chunk in request.iter_content(chunk_size=1000000):
						f.write(chunk)

	shortname = os.path.splitext(filename)[0]
	if 'repo' in inst_yml:
		repo = inst_yml['repo']

		try_mkdir(instances_dir)

		# Download the instance from the repository.
		prefix = ''
		if 'repo-subdir' in inst_yml:
			prefix = inst_yml['repo-subdir'] + '/'
		fmt = repos[repo]['file_fmt']
		url = repos[repo]['url'] + prefix + filename + fmt

		download_path = os.path.join(instances_dir, filename + '.download')
		download_as_stream(url, download_path)

		# Decompress the instance.
		def extract(reader, f):
			f.write(reader.read())

		tmp_path = os.path.join(instances_dir, filename + '.tmp')
		compression = fmt.split('.')[-1]
		if repo == 'snap':
			with gzip.open(download_path, 'rb') as reader:
				with open(tmp_path, 'wb') as f:
					extract(reader, f)
		elif repo == 'network_repository':
			zip_file = zipfile.ZipFile(download_path + compression, 'r')
			# TODO finish
		else:
			raise DownloadException('Unknown repository: ' + repo)

		os.unlink(download_path)
		os.rename(tmp_path, partial_path + ext)
	elif 'method' in inst_yml:
		method = inst_yml['method']
		if method == 'url':
			def substitute(p):
				if p == 'INSTANCE_FILENAME':
					return filename
				raise RuntimeError("Unexpected parameter {}".format(p))

			url = expand_at_params(inst_yml['url'], substitute)
			download_path = partial_path + ext
			download_as_stream(url, download_path)
		elif method == 'git':
			import subprocess

			repo_dir = os.path.join(instances_dir, inst_yml['repo_name'])
			if not os.path.isdir(repo_dir):
				subprocess.check_call(['git', 'clone', inst_yml['git'], repo_dir, '--no-checkout'])

			git_subdir = inst_yml.get('git_subdir', None)
			if git_subdir is not None:
				file_path = os.path.join(git_subdir, filename)
			else:
				file_path = filename

			object_name = inst_yml['commit'] + ':' + file_path
			output = subprocess.check_output(['git', 'show', object_name], cwd=repo_dir)
			with open(os.path.join(instances_dir, filename + ext), 'wb') as f:
				f.write(output)
		else:
			raise RuntimeError(f"Unknown method for instance '{shortname}': {method}")
	else:
		raise RuntimeError(f"Unknown download option for instance '{shortname}'")

# Reformats the network to a SNAP/EdgeList format.
def convert_to_edgelist(inst_yml, in_path, out_path):
	repo = inst_yml['repo']

	if repo == 'konect':
		separator = ' '
		comment_prefix = '%'
	elif repo == 'snap':
		separator = '\t'
		comment_prefix = '#'

	def get_other_separator(separator):
		if separator == ' ':
			return '\t'
		return ' '
	with open(in_path, 'r') as in_f:
		with open(out_path, 'w') as out_f:
			for line in in_f:
				if line.startswith(comment_prefix):
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

