
import os
import socket
import selectors
import subprocess
import sys

from . import base
from . import util


class Queue:

	def __init__(self, serve_socket):
		self.socket = serve_socket
		self.socket_path = serve_socket.getsockname()
		self.selector = selectors.DefaultSelector()
		self._should_stop = False

	@staticmethod
	def get_run_display_name(manifest):
		display_name = manifest['experiment']

		variants = manifest['variants']
		if variants:
			display_name += ' ~ ' + ', '.join([variant['name'] for variant in variants])

		revision = manifest['revision']
		if revision:
			display_name += ' @ ' + revision

		return "{}/{}[{}]".format(display_name, manifest['instance'], manifest['repetition'])

	def run(self):
		print('Serving on {}'.format(self.socket_path))
		self.socket.listen()
		self.selector.register(self.socket, selectors.EVENT_READ)

		requests = []
		num_completed_runs = 0
		cur_subproc = None
		cur_subproc_terminated = True
		cur_run = None
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
						elif request['action'] == 'kill':
							print("Terminating current subprocess")
							if cur_subproc is not None:
								cur_subproc.terminate()
							self.close()
							return
						elif request['action'] == 'show':
							pending_runs = []
							for request in requests:
								specfile_path = request['specfile_path']
								with open(specfile_path, 'r') as f:
									manifest = util.read_yaml_file(f)['manifest']

								pending_runs.append(self.get_run_display_name(manifest))

							queue_info = {
								'current_run': cur_run,
								'pending_runs': pending_runs,
								'num_completed_runs': num_completed_runs
							}
							sk.data.send(util.yaml_to_string(queue_info))
						else:
							print("Ignoring request with unknown action '{}': {}".format(request['action'], request))

					sk.data.close()
					self.selector.unregister(sk.fd)

			if cur_subproc is not None:
				cur_subproc_terminated = cur_subproc.poll() is not None

			if cur_subproc_terminated:

				if cur_subproc is not None:
					cur_run = None
					cur_subproc = None
					num_completed_runs += 1

				if not len(requests) == 0:
					request = requests.pop(0)

					specfile_path = request['specfile_path']
					with open(specfile_path, 'r') as f:
						manifest = util.read_yaml_file(f)['manifest']

					cur_run = self.get_run_display_name(manifest)
					print("Launching run {}".format(cur_run))

					script = os.path.abspath(sys.argv[0])

					cur_subproc = subprocess.Popen([script, 'internal-invoke', '--method=queue', specfile_path])
				elif self._should_stop:
					self.close()
					break

	def close(self):
		print("Closing socket on {}".format(self.socket_path))
		self.socket.close()
		os.remove(self.socket_path)

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

	def send(self, message):
		self.connection.send(message.encode())

def run_queue(sockfd=None, force=False):
	if sockfd is not None:
		serve_sock = socket.socket(fileno=sockfd)
	else:
		serve_sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
		if force:
			util.try_rmfile(base.DEFAULT_SOCKETPATH)
		serve_sock.bind(base.DEFAULT_SOCKETPATH)

	queue = Queue(serve_sock)
	queue.run()

def sendrecv(m):
	s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
	s.connect(base.DEFAULT_SOCKETPATH)
	s.send(util.yaml_to_string(m).encode())
	s.shutdown(socket.SHUT_WR)

	recv_buffer = bytes()
	while True:
		data = s.recv(4096)
		if not data:
			break
		recv_buffer += data

	s.close()
	return util.yaml_from_string(recv_buffer.decode())

def stop_queue():
	sendrecv({
		'action': 'stop'
	})

def kill_queue():
	sendrecv({
		'action': 'kill'
	})

def show_queue():
	return sendrecv({
		'action': 'show'
	})
