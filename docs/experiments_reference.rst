The "experiments.yml" reference
===============================

Simexpal needs an "experiments.yml" file to to automatically execute your experiments
on the desired instances. In this page we describe the structure of the "experiments.yml"
file. The "experiments.yml" is a YAML file that contains a dictionary with several keys:

- instances: list of all the instances that will be used for the experiments.
- instdir: path to the directory that stores all the instances.
- experiments: list of all the experiments that will be executed on the instances.

There are also further keys that allow for customization of the experiments and to
automatically build the binaries the experiments run from:

- builds: list of Git builds, which also include build instructions.
- revisions: list of Git revisions of builds.
- variants: list of additional input parameters for experiments.
- matrix: specifies which combinations of experiments, instances, variants and revisions are run.

Instances
---------
This entry is a list of instances that will be used for experiments. The following keys are
used for specifying instances:

- ``extensions``: list of extensions that the instance has
- ``files``: list of files the instance consists of
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

Experiments
-----------
This entry is a list of experiments that will be executed on all the instances.
Each experiment includes three keys:

- name: a unique identifier of the experiment.
- args: list of command-line arguments to run the code of the experiment.
- output: where the result of the experiments should be saved.

In the example below we show how to run two experiments (insertion-sort and bubble-sort)
on our instances.
demo.py is the code that executes our experiment and accepts two arguments:
the sorting algorithm and the path of the instance.
The resulting data will be outputted to the standard output.

.. literalinclude:: ./experiments.yml.example
   :linenos:
   :lines: 8-
   :language: yaml
   :caption: How to list experiments in the experiments.yml file.
