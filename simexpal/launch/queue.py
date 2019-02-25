
import json
import os
import socket

from . import common

class QueueLauncher(common.Launcher):
	def submit(self, config, run):
		if not common.lock_run(run):
			return
		common.create_run_file(run)

		print("Launching experiment '{}', instance '{}' on local machine".format(
				run.experiment.name, run.instance.filename))

		m = {
			'basedir': config.basedir,
			'experiment': run.experiment.name,
			'instance': run.instance.filename,
			'repetition': run.repetition
		}

		sockpath = os.path.expanduser('~/.extlq.sock')
		s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
		s.connect(sockpath)
		s.send((json.dumps(m) + '\n').encode())
		s.close()
