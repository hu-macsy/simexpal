
import os
import socket
import selectors
import subprocess
import sys
import tempfile

from . import util


class Queue:

	def __init__(self, serve_socket):
		self.socket = serve_socket
		self.socket_path = serve_socket.getsockname()
		self.selector = selectors.DefaultSelector()
		self._should_stop = False

	@staticmethod
	def get_display_name(manifest):
		display_name = manifest['experiment']

		variants = manifest['variants']
		if variants:
			display_name += ' ~ ' + ', '.join([variant['name'] for variant in variants])

		revision = manifest['revision']
		if revision:
			display_name += ' @ ' + revision

		return display_name

	def run(self):
		print('Serving on {}'.format(self.socket_path))
		self.socket.listen()
		self.selector.register(self.socket, selectors.EVENT_READ)

		requests = []
		cur_subprocess = None
		subprocess_terminated = True
		while True:
			events = self.selector.select(1)

			for sk, mask in events:
				if sk.fileobj == self.socket:
					conn, _ = self.socket.accept()
					connection = Connection(conn)

					self.selector.register(conn, selectors.EVENT_READ, connection)
				else:
					request = sk.data.progress()
					if request:
						if request['action'] == 'launch':
							requests.append(request)
						elif request['action'] == 'stop':
							self._should_stop = True
						else:
							print("Ignoring request with unknown action '{}': {}".format(request['action'], request))

					sk.data.close()
					self.selector.unregister(sk.fd)

			if cur_subprocess is not None:
				subprocess_terminated = cur_subprocess.poll() is not None

			if subprocess_terminated and not len(requests) == 0:
				request = requests.pop(0)

				if self._should_stop:
					print("Closing socket on {}".format(self.socket_path))
					self.socket.close()
					os.remove(self.socket_path)
					break

				if request['action'] == 'launch':
					specfile_path = request['specfile_path']
					with open(specfile_path, 'r') as f:
						manifest = util.read_yaml_file(f)['manifest']

					display_name = self.get_display_name(manifest)
					print("Launching run {}/{}[{}]".format(
						display_name, manifest['instance'], manifest['repetition']))

					script = os.path.abspath(sys.argv[0])

					cur_subprocess = subprocess.Popen([script, 'internal-invoke', '--method=queue', specfile_path])

class Connection:
	def __init__(self, connection):
		self.connection = connection

	def progress(self):
		recv_buffer = bytes()
		while True:
			data = self.connection.recv(4096)
			if not data:
				break
			recv_buffer += data

		return util.yaml_from_string(recv_buffer.decode())

	def close(self):
		self.connection.close()

def run_queue(sockfd=None, force=False):
	if sockfd is not None:
		serve_sock = socket.socket(fileno=sockfd)
	else:
		sockpath = os.path.expanduser('~/.extlq.sock')
		serve_sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
		if force:
			util.try_rmfile(sockpath)
		serve_sock.bind(sockpath)

	queue = Queue(serve_sock)
	queue.run()

def sendrecv(m):
	sockpath = os.path.expanduser('~/.extlq.sock')
	s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
	s.connect(sockpath)
	s.send(util.yaml_to_string(m).encode())
	s.close()

def stop_queue():
	sendrecv({
		'action': 'stop'
	})
