
from . import common
from .. import queuesock

class QueueLauncher(common.Launcher):
	def submit(self, config, run):
		if not common.lock_run(run):
			return
		common.create_run_file(run)

		print("Launching experiment '{}', instance '{}' on local machine".format(
				run.experiment.name, run.instance.shortname))

		queuesock.sendrecv({
			'action': 'launch',
			'manifest': common.compile_manifest(run).yml
		})

