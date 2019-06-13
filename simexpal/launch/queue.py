
import json
import os
import socket

from . import common
from .. import queuesock

class QueueLauncher(common.Launcher):
	def submit(self, config, run):
		if not common.lock_run(run):
			return
		common.create_run_file(run)

		print("Launching experiment '{}', instance '{}' on local machine".format(
				run.experiment.name, run.instance.filename))

		queuesock.sendrecv({
			'action': 'launch',
			'basedir': config.basedir,
			'experiment': run.experiment.name,
			'instance': run.instance.filename,
			'repetition': run.repetition
		})

