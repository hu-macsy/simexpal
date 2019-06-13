
import asyncio
import json
import os
import socket

def run_queue(sockfd=None):
	q = asyncio.Queue()

	async def handle_queue():
		while True:
			it = await q.get()

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

	async def handle_echo(reader, writer):
		bits = await reader.readline()
		m = json.loads(bits.decode())
		q.put_nowait(m)

	sockpath = os.path.expanduser('~/.extlq.sock')
	if sockfd is not None:
		sock = socket.socket(fileno=sockfd)
	else:
		sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
		sock.bind(sockpath)

	loop = asyncio.get_event_loop()
	loop.create_task(handle_queue())
	server = loop.run_until_complete(asyncio.start_server(handle_echo, sock=sock, loop=loop))

	# Serve requests until Ctrl+C is pressed
	print('Serving on {}'.format(server.sockets[0].getsockname()))
	try:
		loop.run_forever()
	except KeyboardInterrupt:
		pass

	# Close the server
	server.close()
	loop.run_until_complete(server.wait_closed())
	loop.close()

	if sockfd is None:
		os.unlink(sockpath)

def sendrecv(m):
	sockpath = os.path.expanduser('~/.extlq.sock')
	s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
	s.connect(sockpath)
	s.send((json.dumps(m) + '\n').encode())
	s.close()

