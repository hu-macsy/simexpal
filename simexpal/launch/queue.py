
import os
import tempfile

from . import common
from .. import queuesock
from .. import util

class QueueLauncher(common.Launcher):
	def submit(self, cfg, run):
		util.try_mkdir(os.path.join(cfg.basedir, 'aux'))
		util.try_mkdir(os.path.join(cfg.basedir, 'aux/_queue'))

		if not common.lock_run(run):
			return
		common.create_run_file(run)

		specfd, specfile = tempfile.mkstemp(prefix='', suffix='-spec.yml',
											dir=os.path.join(cfg.basedir, 'aux/_queue'))

		specs = {'manifest': common.compile_manifest(run).yml}
		with os.fdopen(specfd, 'w') as f:
			util.write_yaml_file(f, specs)

		print("Launching experiment '{}', instance '{}' on local machine".format(
				run.experiment.name, run.instance.shortname))

		queuesock.sendrecv({
			'action': 'launch',
			'specfile_path': specfile
		})

