The "experiments.yml" reference
===============================

Simexpal needs an ``experiments.yml`` file to to automatically execute your experiments
on the desired instances. In this page we describe the structure of the ``experiments.yml``
file. The ``experiments.yml`` is a YAML file that contains a dictionary with several keys:

- ``instances``: list of all the instances that will be used for the experiments
- ``instdir``: path to the directory that stores all the instances
- ``experiments``: list of all the experiments that will be executed on the instances

There are also further keys that allow for customization of the experiments and to
automatically build the binaries the experiments run from:

- ``builds``: list of Git builds, which also include build instructions
- ``revisions``: list of Git revisions of builds
- ``variants``: list of additional input parameters for experiments
- ``matrix``: specifies which combinations of experiments, instances, variants and revisions are run

Instances
---------
This entry is a list of instances that will be used for experiments. The following keys are
used for specifying instances:

- ``extensions``: list of extensions that the instance has
- ``extra_args``:  list of extra arguments
- ``files``: list of files the instance consists of
- ``format``: archive format of the instance
- ``items``: list of instances
- ``name``: name of the instance (used when dealing with instances that consist of unrelated files)
- ``repo``: source of instances
- ``set``: list of sets the instance belongs to

For detailed usage examples, see the :ref:`Instances` page.

Builds
------
This entry is a list of builds that will be used for revisions. The following keys are
used for specifying builds:

- ``configure``: list of dictionaries containing configuration parameters
- ``compile``: list of dictionaries containing compilation parameters
- ``environ``: dictionary of (environment variable, value)-pairs
- ``git``: link to the Git repository
- ``install``: list of dictionaries containing installation parameters
- ``name``: (arbitrary) name of the build
- ``recursive-clone``: boolean (``true``/``false``) - whether to pull git submodules recursively or not
- ``regenerate``: list of dictionaries containing regeneration parameters
- ``requires``: list of required builds
- ``workdir``: path of the working directory

For detailed usage examples, see the :ref:`Builds` page.

Revisions
---------
This entry is a list of revisions that will be used for experiments. The following keys are
used for specifying revisions:

- ``build_version``: dictionary of (build, SHA-1 hash/branch)-pairs
- ``develop``: boolean (``true``/``false``) - whether this revision is a develop revision or not
- ``name``: (arbitrary) name of the revision

For detailed usage examples, see the :ref:`Revisions` page.

Experiments
-----------
This entry is a list of experiments that will be executed on all the instances.
Each experiment includes three keys:


- ``args``: list of experiment arguments
- ``environ``: dictionary of (environment variable, value)-pairs
- ``name``: name of the experiment
- ``num_nodes``: number of nodes on which to run
- ``num_threads``: number of cpus required per task
- ``output``: dictionary containing all output file extensions
- ``procs_per_node``: number of tasks to invoke on each node
- ``repeat``: integer - number of times an experiment is repeated
- ``slurm_args``: list of additional ``sbatch`` arguments
- ``stdout``: extension of the output file
- ``timeout``: integer - timeout in seconds
- ``use_builds``: list of used build names

For detailed usage examples, see the :ref:`Experiments` page.

Variants
--------
This entry is a list of variants that will be used for experiments. The following keys are
used for specifying variants:

- ``axis``: name of the variant axis
- ``environ``: dictionary of (environment variable, value)-pairs
- ``extra_args``: list of variant arguments
- ``items``: list of dictionaries, which specify variants belonging to the same axis.
- ``name``: name of the variant
- ``num_nodes``: number of nodes on which to run
- ``num_threads``: number of cpus required per task
- ``procs_per_node``: number of tasks to invoke on each node

For detailed usage examples, see the :ref:`Variants` page.

Run Matrix
----------
This entry is a list of desired experiment combinations. The following keys are
used for specifying desired experiment combinations:

- ``axes``: list of included axis names
- ``experiments``: list of included experiment names
- ``include``: list of dictionaries, which specify included experiment combinations
- ``instsets``: list of included instance set names
- ``repetitions``: integer - number of times all combinations of an ``include`` entry are repeated
- ``revisions``: list of included revision names
- ``variants``: list of included variant names

For detailed usage examples, see the :ref:`RunMatrix` page.
