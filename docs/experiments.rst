.. _Experiments:

Experiments
===========

You might want to take a look at the following pages before exploring experiments:

- :ref:`QuickStart`
- :ref:`AtVariables`
- :ref:`Instances`
- :ref:`Builds`
- :ref:`Revisions`
- :ref:`Variants`

On this page we describe how to specify experiments in our ``experiments.yml`` file. We will see how
to use builds in experiments, redirect the output and enable options such as repeating experiments or
setting a timeout. Moreover, we will see that simexpal can be used together with batch schedulers (e.g.
`Slurm <https://slurm.schedmd.com/overview.html>`_,
`Oracle Grid Engine <https://docs.oracle.com/cd/E19680-01/html/821-1541/docinfo.html#scrolltoc>`_ (formerly SGE),
...), and how to set environment variables.

Specifying Experiments
----------------------

In this section we will see how to specify experiments with different kinds of :ref:`Instances` and
:ref:`Variants` by using the keys:

- ``name``: name of the experiment
- ``args``: list of experiment arguments.

.. _ExperimentsWithLocalRemoteInstances:

Experiments with Local/Remote Instances
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Assuming we have a ``./sort.py`` file in the same directory as the ``experiments.yml`` that
takes a keyword argument ``--algo`` and a path to a single
(:ref:`local <LocalInstances>`/:ref:`remote <RemoteInstances>`) instance as input, we can define
our ``experiments.yml`` as follows:

.. code-block:: YAML
   :linenos:
   :caption: How to specify experiments for local and remote instances in the experiments.yml file.

   experiments:
     - name: insertion-sort
       args: ['./sort.py', '--algo=insertion-sort', '@INSTANCE@']
       stdout: out

In the examples above we created an experiment named `insertion-sort`. As experiment arguments we have
a list of strings (instead of one space separated string). Note that the :ref:`@-variable <AtVariables>`
``@INSTANCE@`` resolves to the paths of the instances given in the ``instances`` stanza, i.e,
``/instance_directory/<instance_name>``.

If the instances have :ref:`InstanceExtraArguments`, we further need to add the :ref:`@-variable <AtVariables>`
``@EXTRA_ARGS@`` to the experiment arguments, e.g,
``args: ['./sort.py', '--algo=insertion-sort', '@INSTANCE@', '@EXTRA_ARGS@']`` for the example above.
``@EXTRA_ARGS@`` will resolve to the specified extra arguments of the respective instance (and also the used
:ref:`variants <ExperimentsWithVariants>`, see below).

.. _ExperimentsWithMultipleExtensionInstances:

Experiments with Multiple Extension Instances
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Specifying experiments with :ref:`multiple extension <MultipleExtensions>` instances works similarly to
specifying experiments with :ref:`local/remote intances <ExperimentsWithLocalRemoteInstances>`. They
only differ in the used :ref:`@-variable <AtVariables>` in the experiment arguments. Here, we use the
@-variable ``@INSTANCE:<ext>@``, where ``<ext>`` is an extension that is specified in the
``extensions`` key of an instance in the ``instances`` stanza.

Assuming you have an algorithm that takes a path to a ``.graph`` and a ``.yxz`` file as input, you can
specify your experiment as follows:

.. code-block:: YAML
   :linenos:
   :caption: How to specify experiments for multiple extension instances in the experiments.yml file.

   experiments:
     - name: graph-algorithm
       args: ['./algorithm.py', '@INSTANCE:graph', '@INSTANCE:xyz@']
       stdout: out

The ``@INSTANCE:graph@`` variable will resolve to ``/instance_directory/<instance_name>.graph`` during
runtime. Analogously for the ``@INSTANCE:xyz@`` variable.

:ref:`InstanceExtraArguments` are handled analogously to the case of :ref:`ExperimentsWithLocalRemoteInstances`.

Experiments with Arbitrary Input File Instances
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Specifying experiments with :ref:`arbitrary input file <ArbitraryInputFiles>` instances works similarly to
specifying experiments with :ref:`multiple extension intances <ExperimentsWithMultipleExtensionInstances>`.
They only differ in the used :ref:`@-variable <AtVariables>` in the experiment arguments. Here, we use the
@-variable ``@INSTANCE:<index>@``, where ``<index>`` is the index of the desired file specified in the
``files`` key of an instance in the ``instances`` stanza. Note that indices start at ``0``.

Assuming you have an algorithm that takes two input files as input and you want to pass the path to the first
file of the ``files`` key and then the path to the second file to your algorithm, you can specify your experiment
as follows:

.. code-block:: YAML
   :linenos:
   :caption: How to specify experiments for arbitrary input file instances in the experiments.yml file.

   experiments:
     - name: algorithm
       args: ['./algorithm.py', '@INSTANCE:0', '@INSTANCE:1@']
       stdout: out

The ``@INSTANCE:0@`` variable will resolve to ``/instance_directory/files[0]``, where ``files[0]`` is
the first filename of the ``files`` key. Analogously for the ``@INSTANCE:1`` variable.

:ref:`InstanceExtraArguments` are handled analogously to the case of :ref:`ExperimentsWithLocalRemoteInstances`.

.. _ExperimentsWithVariants:

Experiments with Variants
^^^^^^^^^^^^^^^^^^^^^^^^^

To specify experiments with :ref:`Variants` we need to add the ``@EXTRA_ARGS@`` variable to the experiment
arguments:

.. code-block:: YAML
   :linenos:
   :caption: How to specify experiments with variants in the experiments.yml file.

   experiments:
     - name: algorithm
       args: ['./algorithm.py', '@INSTANCE@', '@EXTRA_ARGS@']
       stdout: out

The ``@EXTRA_ARGS@`` variable resolves to the extra arguments of all variants (and also the used instance, see
above) of the experiment during runtime. For example, assume we have the following ``variants`` stanza:

.. code-block:: YAML
   :linenos:

   variants:
     - axis: 'block-algo'
       items:
         - name: 'ba-insert'
           extra_args: ['insertion_sort']
         - name: 'ba-bubble'
           extra_args: ['bubble_sort']
     - axis: 'block-size'
       items:
         - name: 'bs32'
           extra_args: ['32']
         - name: 'bs64'
           extra_args: ['64']

Then ``@EXTRA_ARGS@`` will resolve to

- ``'ba-bubble', 'bs32'``,
- ``'ba-bubble', 'bs64'``,
- ``'ba-insert', 'bs32'`` and
- ``'ba-insert', 'bs64'``

in the respective experiments.

Use Builds
----------

On the :ref:`Builds` page we explained how to set up automated builds. In order to use those builds
for our experiments we need to specify them with the

- ``use_builds``: list of used build names

key. Assuming that we have defined ``build1`` in our ``builds`` stanza, we can link the build to
the experiment as follows:

.. code-block:: YAML
   :linenos:
   :caption: How to specify used builds for experiments in the experiments.yml file.

   experiments:
     - name: experiment1
       args: ['<name_of_executable_of_build1>', ...]
       use_builds: [build1]
       ...

In this way simexpal will check the :ref:`installation directory <BuildDirectories>` and the ``extra_paths``
of the builds specified in ``use_builds`` for the executable. If a build
:ref:`requires other builds <DependentBuilds>` and they are properly specified in the ``requires`` key, then
simexpal will also check the installation directories and ``extra_paths`` of those builds.

Output
------

To redirect the output of an experiment to the ``./output/`` folder, we specify the

- ``stdout``: extension of the output file
- ``output``: dictionary containing all output file extensions

keys.

Assume the following ``experiments`` stanza in our ``experiments.yml``:

.. code-block:: YAML
   :linenos:
   :caption: How to specify the output file extensions for experiments in the experiments.yml file.

   experiments:
     - name: experiment1
       ...
       stdout: 'out'
       output:
         extensions: ['out', 'foo']

Simexpal will then store the outputs in ``<instance_name>.out`` files, which are located in the

- ``./output/<experiment_name>~<variant_names>@<revision_name>``

directory.

.. note::
   In previous versions of simexpal we would specify the ``output`` key with ``'stdout'`` as value, i.e
   ``output: 'stdout'``, to achieve the behaviour above. This is deprecated and might be removed in
   future versions.

The substring ``~<variant_names>`` only appears, if the experiment has variants. ``<variant_names>``
will then be a comma separated enumeration of the used variants. The suffix ``@<revision_name>``
appears if the experiment uses builds and shows the name of the used revision.

To access the output files with other extensions, we can use the :ref:`@-variable <AtVariables>`
``@OUTPUT:<ext>@``, where ``<ext>`` is an extension specified in the ``extensions`` key. This
@-variable can be used in the ``args`` key of experiments and is useful for use cases like the following:

The experiments that we are running store all intermediate steps and results. Thus, when taking a look at
the output files, we could encounter thousands (or even more) lines of information even though we might
only be interested in the last couple of lines. To avoid this, we add another input parameter, which takes a
file path, to our experiments. We then store the final experiment results in this file. Our experiment ``args``
could then look like this:

- ``args: ['experiments.py', '@INSTANCE@', '@OUTPUT:foo@']``,

where the first file path is the path to the instance and the second file path is the path to the output file
that contains the final results (``@OUTPUT:foo@`` will resolve to the output file with extension ``.foo``).

.. _ExperimentsRepeat:

Repeat
------

Sometimes it might be useful to validate experiment results by repeating the experiment. In order to
avoid duplicating an ``experiments`` entry we can use the

- ``repeat``: integer - number of times an experiment is repeated

key. To repeat an experiment twice we define our ``experiments`` stanza as follows:

.. code-block:: YAML
   :linenos:
   :caption: How to specify repetitions for experiments in the experiments.yml file.

   experiments:
     - name: experiment1
       ...
       repeat: 2

The default value of ``repeat`` is ``1``.

Timeout
-------

Use the ``timeout`` key in the experiments section to specify the time in
seconds an experiment is allowed to run for. When the timeout is exceeded, the
experiment will be terminated forcefully. The following is an example on how to
set a timeout after 7200 seconds (2 hours): 

.. code-block:: YAML
   :linenos:
   :caption: How to specify a timeout for experiments in the experiments.yml file.

   experiments:
     - name: experiment1
       ...
       timeout: 7200

After the experiment has reached the limit of the specified timeout, the signal
``SIGXCPU`` is sent to the running process. ``SIGXCPU`` can be handled by the
process first, and after a grace period the signal ``SIGTERM`` is sent to the
process for the final termination.

.. _ExperimentsSettingEnvironmentVariables:

Setting Environment Variables
-----------------------------

When using APIs like `OpenMP <https://www.openmp.org/spec-html/5.0/openmp.html>`_ it is sometimes
necessary to specify settings as environment variables. Thus, simexpal supports setting environment
variables in experiments by specifying the

- ``environ``: dictionary of (environment variable, value)-pairs

key. For example you can specify the ``OMP_NUM_THREADS`` environment variable as follows:

.. code-block:: YAML
   :linenos:
   :caption: How to specify environment variables for experiments in the experiments.yml file.

   experiments:
     - name: experiment1
       args: ...
       ...
       environ:
         OMP_NUM_THREADS: 2
      - name: experiment2
        args: ...
        ...
        environ:
         OMP_NUM_THREADS: 4

Slurm
-----

.. _ExperimentsSupportedSlurmArgs:

sbatch: ``--ntasks-per-node``, ``-c``, ``-N``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

When using a job scheduler like `Slurm <https://slurm.schedmd.com/overview.html>`_ it might be
useful to run your software using different node/cpu settings.

Currently, simexpal supports the following three ``sbatch`` parameters by using its own keywords in
the ``experiments.yml``:

- ``procs_per_node``: number of tasks to invoke on each node (slurm: ``--ntasks-per-node=n``)
- ``num_threads``:    number of cpus required per task (slurm: ``-c``, ``--cpus-per-task=ncpus``)
- ``num_nodes``:      number of nodes on which to run (N = min[-max]) (slurm: ``-N``, ``--nodes=N``)
- ``exclusive``:      boolean to set the ``--exclusive`` flag, so the job allocation reserves all resources of a node

.. code-block:: YAML
   :linenos:
   :caption: How to specify supported Slurm parameters for experiments in the experiments.yml file.

   experiments:
     - name: experiment1
       ...
       num_nodes: 1
       procs_per_node: 24
       num_threads: 2
     - name: experiment2
       ...
       num_nodes: 2
       procs_per_node: 24
       num_threads: 2


When launching your experiments with slurm, the line ``-N 1 --ntasks-per-node 24 -c 2``
will be appended to the sbatch command for ``experiment1``. Analogously for ``experiment2``.

Arbitrary ``sbatch`` Arguments
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

In the section before, we saw how to set the values of three supported ``sbatch`` arguments. In
this section, we will see how to set the value of any supported ``sbatch`` command. To do so, we
use the

- ``slurm_args``: list of additional ``sbatch`` arguments

key. For example, we can set the job name of an experiment by using the ``-J`` parameter of the
``sbatch`` command:

.. code-block:: YAML
   :linenos:
   :caption: How to specify additional Slurm parameters for experiments in the experiments.yml file.

   experiments:
     - name: experiment1
       ...
       slurm_args: ['-J', 'arbitrary_jobname']

Next
----

To get a more detailed understanding of experiment variants and fully set up your experiments, you
can visit the :ref:`Variants` page. If you do not plan on having experiments, you can visit the
:ref:`RunMatrix` page to modify the experiment combinations that you want to run.
