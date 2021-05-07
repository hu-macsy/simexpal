
import os
import socket
import selectors
import subprocess
import sys

from . import base
from . import util
from collections import OrderedDict


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
		import signal

		signal_reader, signal_writer = os.pipe()
		os.set_blocking(signal_writer, False)
		signal.set_wakeup_fd(signal_writer)

		# We need to install a signal handler in order for
		# signal.set_wakeup_fd() to write the signal into fd
		signal.signal(signal.SIGTERM, lambda *args: None)
		signal.signal(signal.SIGINT, lambda *args: None)

		self.selector.register(signal_reader, selectors.EVENT_READ)

		print('Serving on {}'.format(self.socket_path))
		self.socket.listen()
		self.selector.register(self.socket, selectors.EVENT_READ)

		requests = OrderedDict()
		num_completed_runs = 0
		cur_queue_jobid = None
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
					if sk.fileobj == signal_reader:
						self.selector.unregister(signal_reader)
						# SIGTERM or SIGINT was sent to the process. We have to kill the queue launcher.
						request = {'action': 'kill'}
					else:
						request = sk.data.progress()

					if request:
						if request['action'] == 'launch':
							queue_jobid = util.extract_file_prefix_from_path(request['specfile_path'], '-spec')
							requests[queue_jobid] = request
						elif request['action'] == 'get_job_status_dict':
							queried_jobs = {}
							if cur_queue_jobid is not None:
								queried_jobs[cur_queue_jobid] = int(base.Status.STARTED)
							for queue_jobid in requests:
								queried_jobs[queue_jobid] = int(base.Status.SUBMITTED)
							sk.data.send(util.yaml_to_string(queried_jobs))
						elif request['action'] == 'stop':
							self._should_stop = True
						elif request['action'] == 'kill':
							print("Terminating current subprocess")
							if cur_subproc is not None:
								# terminate() is sufficient as the subprocess is a simexpal process
								# and thus will always terminate accordingly when receiving SIGTERM
								cur_subproc.terminate()
							os.close(signal_reader)
							os.close(signal_writer)
							self.close()

							raise RuntimeError(
								"simexpal received a termination signal (either SIGINT or SIGTERM) and has terminated "
								"the current child process")
						elif request['action'] == 'show':
							pending_runs = []
							for request in requests.values():
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
					cur_queue_jobid = None
					cur_run = None
					cur_subproc = None
					num_completed_runs += 1

				if not len(requests) == 0:
					queue_jobid, request = requests.popitem(last=False)  # FIFO

					specfile_path = request['specfile_path']
					with open(specfile_path, 'r') as f:
						manifest = util.read_yaml_file(f)['manifest']

					cur_queue_jobid = queue_jobid
					cur_run = self.get_run_display_name(manifest)
					print("Launching run {} with queue jobid '{}'".format(cur_run, cur_queue_jobid))

					script = os.path.abspath(sys.argv[0])

					with open(os.path.join(manifest['config']['base_dir'], 'aux/_queue/' + queue_jobid + '.err'), 'w') as f:
						cur_subproc = subprocess.Popen([script, 'internal-invoke', '--method=queue', specfile_path], stderr=f)
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

def get_job_status_dict():
	return sendrecv({
		'action': 'get_job_status_dict'
	})
