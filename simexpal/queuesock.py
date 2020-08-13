
from enum import Enum
import functools
import os
import socket

from . import launch
from .launch import common
from . import util
from . import evloop

class _State(Enum):
	REQUEST = 0
	DONE = 1

class _Queue:
	@staticmethod
	def handle_sock(self, descriptor):
		accepted, _ = self.sock.accept()
		con = _Connection(self, accepted)
		con.run(descriptor.get_loop())

	@staticmethod
	def observe_loop(self, descriptor):
		self._handle.unregister()
		self._observer.unregister()

		if self.path is not None:
			os.unlink(self.path)

	def __init__(self, sock, path=None):
		self.sock = sock
		self.path = path
		self._handle = None
		self._observer = None

	def run(self, loop):
		self._handle = loop.register_file(self.sock, evloop.READ,
				functools.partial(_Queue.handle_sock, self))
		self._observer = loop.register_observer(functools.partial(_Queue.observe_loop, self))
		self.sock.listen()

	# Dispatch a request and return a response.
	# This function is the main workhorse of the queue server.
	def dispatch(self, loop, req):
		if req['action'] == 'stop':
			loop.shutdown()
		else:
			assert req['action'] == 'launch'
			manifest = launch.common.RunManifest(req['manifest'])

			print("Processing experiment '{}', instance '{}'".format(
					manifest.experiment, manifest.instance))
			launch.common.invoke_run(manifest)

class _Connection:
	@staticmethod
	def handle_sock(self, descriptor):
		assert self.state == _State.REQUEST

		data = self.sock.recv(4096)
		if data:
			self.recv_buffer += data
			return

		req = util.yaml_from_string(self.recv_buffer.decode())
		resp = self.queue.dispatch(descriptor.get_loop(), req)
		self.state = _State.DONE
		self._handle.unregister()

	@staticmethod
	def observe_loop(self, descriptor):
		self._handle.unregister()
		self._observer.unregister()

	def __init__(self, queue, sock):
		self.queue = queue
		self.sock = sock
		self.recv_buffer = bytes()
		self.state = _State.REQUEST
		self._handle = None
		self._observer = None

	def run(self, loop):
		self._handle = loop.register_file(self.sock, evloop.READ,
				functools.partial(_Connection.handle_sock, self))
		self._observer = loop.register_observer(functools.partial(_Connection.observe_loop, self))

def run_queue(loop, sockfd=None, force=False):
	if sockfd is not None:
		serve_sock = socket.socket(fileno=sockfd)
		queue = _Queue(serve_sock)
	else:
		sockpath = os.path.expanduser('~/.extlq.sock')
		serve_sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
		if force:
			util.try_rmfile(sockpath)
		serve_sock.bind(sockpath)
		queue = _Queue(serve_sock, path=sockpath)

	queue.run(loop)
	print('Serving on {}'.format(serve_sock.getsockname()))

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
