
import os
import tempfile
import sys

from ..base import DEFAULT_SOCKETPATH
from . import common
from .. import queuesock
from .. import util

class QueueLauncher(common.Launcher):
	def submit(self, cfg, run):
		util.try_mkdir(os.path.join(cfg.basedir, 'aux'))
		util.try_mkdir(os.path.join(cfg.basedir, 'aux/_queue'))

		try:
			queuesock.show_queue()
		except FileNotFoundError:
			print("There is currently no queue daemon running. Please start a new daemon before launching experiments.")
			sys.exit(1)
		except ConnectionRefusedError:
			print("There is currently a queue daemon running that did not terminate properly. Use "
				"'simex queue interactive --force' or 'simex q daemon --force' to forcefully launch a new daemon. "
				 "Alternatively you can delete the socket '{}' manually and start a new daemon.".format(
				DEFAULT_SOCKETPATH))
			sys.exit(1)

		if not common.lock_run(run):
			return
		common.create_run_file(run)

		specfd, specfile = tempfile.mkstemp(prefix='', suffix='-spec.yml',
											dir=os.path.join(cfg.basedir, 'aux/_queue'))

		specs = {'manifest': common.compile_manifest(run).yml}
		with os.fdopen(specfd, 'w') as f:
			util.write_yaml_file(f, specs)

		print("Launching run {}/{}[{}] on local machine".format(
				run.experiment.display_name, run.instance.shortname, run.repetition))

		queuesock.sendrecv({
			'action': 'launch',
			'specfile_path': specfile
		})

