.. _AtVariables:

@-Variables
===========

@-variables are placeholder variables that can be used in the ``experiments.yml`` file. They are enclosed
by at signs, i.e. ``@...@`` and get resolved during runtime.

For example: In order to avoid the duplication of command line arguments of experiments for each instance,
e.g. ``experiment.py /path/to/instance1``, ``experiment.py /path/to/instance2``, ... we use the
``@INSTANCE@`` variable that resolves to the respective paths of the instances. Then, we only need to
specify ``experiments.py @INSTANCE@`` as experiment arguments.


Below, we list all @-variables and where they can be used.

- ``@BASE_DIR@``: path of the directory containing the ``experiments.yml``
- ``@COMPILE_DIR_FOR:<build_name>@``: :ref:`compilation directory <BuildDirectories>` of ``<build_name>`` in the same revision
- ``@EXTRA_ARGS@``: extra arguments of all variants and the instance of an experiment
- ``@INSTANCE@``: path of a :ref:`local <LocalInstances>`/:ref:`remote <RemoteInstances>` instance, i.e. ``/instance_directory/<instance_name>``
- ``@INSTANCE_DIR@``: path of the :ref:`InstanceDirectory`
- ``@INSTANCE_FILENAME@``: filename of the instance
- ``@INSTANCE:<ext>@``: path of a :ref:`MultipleExtensions` instance with extension ``<ext>``, i.e. ``/instance_directory/<instance_name>.<ext>``
- ``@INSTANCE:<idx>@``: path of an :ref:`ArbitraryInputFiles` instance with index ``<idx>`` in the ``files`` key, i.e. ``/instance_directory/files[<idx>]``
- ``@OUTPUT@``: path to the output file of an experiment
- ``@OUTPUT:<ext>@``: path to the output file with extension ``<ext>`` of an experiment
- ``@OUTPUT_SUBDIR@``: output subdirectory of the experiment where the output and status files are stored, i.e. ``/path_to_experiments_yml/output/``
- ``@PARALLELISM@``: number of available CPUs
- ``@PREFIX_DIR_FOR:<build_name>@``: :ref:`installation directory <BuildDirectories>` of ``<build_name>`` in the same revision
- ``@REPETITION@``: repetition number of this experiment
- ``@SOURCE_DIR_FOR:<build_name>@``: :ref:`source directory <BuildDirectories>` of ``<build_name>`` in the same revision
- ``@THIS_CLONE_DIR@``: Deprecated for ``@THIS_SOURCE_DIR@``
- ``@THIS_COMPILE_DIR@``: :ref:`compilation directory <BuildDirectories>` of this build
- ``@THIS_PREFIX_DIR@``: :ref:`installation directory <BuildDirectories>` of this build
- ``@THIS_SOURCE_DIR@``: :ref:`source directory <BuildDirectories>` of this build
- ``@VARIANT_VALUE:<axis_name>@``: variant value of the :ref:`dynamic variant <DynamicVariants>` axis ``<axis_name>``


Builds
------

.. _AtVariablesBuildsCompile:

compile
^^^^^^^

The following @-variables can be used in the ``compile`` key:

- ``@BASE_DIR@``
- ``@COMPILE_DIR_FOR:<build_name>@``
- ``@INSTANCE_DIR@``
- ``@PARALLELISM@``
- ``@PREFIX_DIR_FOR:<build_name>@``
- ``@SOURCE_DIR_FOR:<build_name>@``
- ``@THIS_CLONE_DIR@`` (deprecated for ``@THIS_SOURCE_DIR@``)
- ``@THIS_COMPILE_DIR@``
- ``@THIS_PREFIX_DIR@``
- ``@THIS_SOURCE_DIR@``


configure
^^^^^^^^^

Same as for the :ref:`AtVariablesBuildsCompile` key.

environ
^^^^^^^

The values of the ``environ`` key will be substituted and the @-variables are the same as for
the :ref:`AtVariablesBuildsCompile` key.

extra_paths
^^^^^^^^^^^

Same as for the :ref:`AtVariablesBuildsCompile` key `without` the ``@PARALLELISM@`` variable.

install
^^^^^^^

Same as for the :ref:`AtVariablesBuildsCompile` key.

regenerate
^^^^^^^^^^

Same as for the :ref:`AtVariablesBuildsCompile` key.

workdir
^^^^^^^

Same as for the :ref:`AtVariablesBuildsCompile` key.


Experiments
-----------

.. _AtVariablesExperimentsArgs:

args
^^^^

The following @-variables can be used in the ``args`` key:

- ``@BASE_DIR@``
- ``@COMPILE_DIR_FOR:<build_name>@`` (``<build>`` has to be in ``used_builds`` or be required by a build in it)
- ``@EXTRA_ARGS@``
- ``@INSTANCE@``
- ``@INSTANCE_DIR@``
- ``@INSTANCE:<ext>@``
- ``@INSTANCE:<idx>@``
- ``@OUTPUT@``
- ``@OUTPUT:<ext>@``
- ``@OUTPUT_SUBDIR@``
- ``@PREFIX_DIR_FOR:<build_name>@`` (``<build_name>`` has to be in ``used_builds`` or be required by a build in it)
- ``@REPETITION@``
- ``@SOURCE_DIR_FOR:<build_name>@`` (``<build_name>`` has to be in ``used_builds`` or be required by a build in it)
- ``@VARIANT_VALUE:<axis_name>@``

environ
^^^^^^^

The values of the ``environ`` key will be substituted and the @-variables are the same as for
the :ref:`AtVariablesExperimentsArgs` key.

num_nodes
^^^^^^^^^

Same as for the :ref:`AtVariablesExperimentsArgs` key `without` the ``@EXTRA_ARGS@`` variable.

num_threads
^^^^^^^^^^^

Same as for the :ref:`AtVariablesExperimentsArgs` key `without` the ``@EXTRA_ARGS@`` variable.

procs_per_node
^^^^^^^^^^^^^^

Same as for the :ref:`AtVariablesExperimentsArgs` key `without` the ``@EXTRA_ARGS@`` variable.


workdir
^^^^^^^

Same as for the :ref:`AtVariablesExperimentsArgs` key `without` the ``@EXTRA_ARGS@`` variable.


Instances
---------

.. _AtVariablesInstanceArgs:

args
^^^^

The following @-variables can be used in the ``args`` key:


- ``@BASE_DIR@``
- ``@INSTANCE_DIR@``
- ``@INSTANCE@``
- ``@INSTANCE:<ext>@``
- ``@INSTANCE:<idx>@``

environ
^^^^^^^

The values of the ``environ`` key will be substituted and the @-variables are the same as for
the :ref:`AtVariablesInstanceArgs` key.

extra_args
^^^^^^^^^^

Same as for the :ref:`experiments args <AtVariablesExperimentsArgs>` key `without` the ``@EXTRA_ARGS@`` variable.

generator
^^^^^^^^^

args
~~~~

The following @-variables can be used in the ``args`` key of the ``generator`` key:

- ``@INSTANCE_FILENAME@``

url
^^^

The following @-variables can be used in the ``url`` key:

- ``@INSTANCE_FILENAME@``

workdir
^^^^^^^

Same as for the :ref:`AtVariablesInstanceArgs` key.


Variants
--------

environ
^^^^^^^

Same as for the :ref:`experiments args <AtVariablesExperimentsArgs>` key `without` the ``@EXTRA_ARGS@`` variable.

extra_args
^^^^^^^^^^

Same as for the :ref:`experiments args <AtVariablesExperimentsArgs>` key `without` the ``@EXTRA_ARGS@`` variable.

num_nodes
^^^^^^^^^

Same as for the :ref:`experiments args <AtVariablesExperimentsArgs>` key `without` the ``@EXTRA_ARGS@`` variable.

num_threads
^^^^^^^^^^^

Same as for the :ref:`experiments args <AtVariablesExperimentsArgs>` key `without` the ``@EXTRA_ARGS@`` variable.

procs_per_node
^^^^^^^^^^^^^^

Same as for the :ref:`experiments args <AtVariablesExperimentsArgs>` key `without` the ``@EXTRA_ARGS@`` variable.

