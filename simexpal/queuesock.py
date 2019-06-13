
import functools
import json
import os
import selectors
import socket

from . import util

def run_queue(sockfd=None, force=False):
	sockpath = os.path.expanduser('~/.extlq.sock')
	if sockfd is not None:
		serve_sock = socket.socket(fileno=sockfd)
	else:
		serve_sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
		if force:
			util.try_rmfile(sockpath)
		serve_sock.bind(sockpath)

	sel = selectors.DefaultSelector()

	class Queue:
		def __init__(self):
			self.done = False

	q = Queue()

	# Dispatch a request and return a response.
	# This function is the main workhorse of the queue server.
	def dispatch(req):
		if req['action'] == 'stop':
			q.done = True
		else:
			assert req['action'] == 'launch'
			cfg = extl.base.config_for_dir(basedir=it['basedir'])

			for run in cfg.discover_all_runs():
				if run.experiment.name != it['experiment']:
					continue
				if run.instance.filename != it['instance']:
					continue
				if run.repetition != it['repetition']:
					continue

				print("Processing experiment '{}', instance '{}'".format(
						run.experiment.name, run.instance.filename))
				extl.launch.common.invoke_run(run)

	class Connection:
		def __init__(self):
			self.recv_buffer = bytes()

	def handle_serve(mask):
		sock, _ = serve_sock.accept()
		con = Connection()
		sel.register(sock, selectors.EVENT_READ,
				functools.partial(handle_req, sock, con))

	def handle_req(sock, con, mask):
		data = sock.recv(4096)
		if data:
			con.recv_buffer += data
			return

		req = json.loads(con.recv_buffer.decode())
		resp = dispatch(req)
		sel.unregister(sock)

	sel.register(serve_sock, selectors.EVENT_READ, handle_serve)
	serve_sock.listen()

	# Serve requests until Ctrl+C is pressed
	print('Serving on {}'.format(serve_sock.getsockname()))
	while not q.done:
		events = sel.select();
		for key, mask in events:
			key.data(mask)

	if sockfd is None:
		os.unlink(sockpath)

def sendrecv(m):
	sockpath = os.path.expanduser('~/.extlq.sock')
	s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
	s.connect(sockpath)
	s.send((json.dumps(m) + '\n').encode())
	s.close()

def stop_queue():
	sendrecv({
		'action': 'stop'
	})

