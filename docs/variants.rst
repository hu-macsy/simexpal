.. _Variants:

Variants
========

You might want to take a look at the following pages before exploring variants:

- :ref:`QuickStart`
- :ref:`AtVariables`
- :ref:`Builds`
- :ref:`Revisions`
- :ref:`Experiments`

When benchmarking algorithms, it is often useful to compare different variants or parameter
configurations of the same algorithm. Simexpal can manage those variants without requiring
you to duplicate the ``experiments`` stanza multiple times.

Specifying Variants
-------------------

To specify variants we will use the following keys:

- ``axis``: name of the variant axis
- ``items``: list of dictionaries, which specify variants belonging to the same axis.

For the variants in the ``items`` list we have to specify the

- ``name``: name of the variant
- ``extra_args``: list of variant arguments

keys.

.. code-block:: YAML
   :linenos:
   :caption: How to specify variants in the experiments.yml file.

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

In this way we created the two variant axes ``block-algo`` and ``block-size``. The former
axis has the variants ``ba-insert`` and ``ba-bubble`` and the latter has the variants
``bs32`` and ``bs64``. If the ``extra_args`` contain more than one argument, e.g., a keyword
argument ``--block-algo ba-insert``, then the arguments are stated separately in a list, i.e.
``['--block-algo', 'ba-insert']``.

Experiments will then be created from the cross product of the variants of each axis, i.e,
``(ba-insert, bs32)``, ``(ba-insert, bs64)``, ``(ba-bubble, bs32)`` and ``(ba-bubble, bs32)``
for the ``experiments.yml`` above.

.. note::
   The elements in each cross product will be sorted lexicographically. This plays a role when
   the ``extra_args`` contain positional arguments as they are resolved in the order of the
   elements in a cross product.

Later we will see how to choose only certain combinations of variants (:ref:`RunMatrix`).

Setting Environment Variables
-----------------------------

.. note::
   Environment variables specified in variants will override the values of environment variables
   specified in the ``experiments`` stanza (if the same variable occurs).

Setting environment variables for variants works similar to
:ref:`setting environment variables for experiments <ExperimentsSettingEnvironmentVariables>`.
The difference is that we set the

- ``environ``: dictionary of (environment variable, value)-pairs

key for each item in the ``items`` key. For example you can specify the
``OMP_NUM_THREADS`` environment variable as follows:

.. code-block:: YAML
   :linenos:
   :caption: How to specify environment variables for variants in the experiments.yml file.

   variants:
     - axis: num_threads
       items:
         - name: ONT2
           ...
           environ:
             OMP_NUM_THREADS: 2

         - name: ONT4
           ...
           environ:
             OMP_NUM_THREADS: 4

Slurm: ``--ntasks-per-node``, ``-c``, ``-N``
--------------------------------------------

.. note::
   Supported Slurm arguments specified in variants will override the values of supported Slurm
   arguments specified in the ``experiments`` stanza (if the same slurm argument occurs).

The :ref:`supported Slurm arguments in experiments <ExperimentsSupportedSlurmArgs>` are also
supported for variants. Here, we can specify the

- ``procs_per_node``: number of tasks to invoke on each node (slurm: ``--ntasks-per-node=n``)
- ``num_threads``: number of cpus required per task (slurm: ``-c``, ``--cpus-per-task=ncpus``)
- ``num_nodes``: number of nodes on which to run (N = min[-max]) (slurm: ``-N``, ``--nodes=N``)

keys for each item in the ``items`` key.

.. code-block:: YAML
   :linenos:
   :caption: How to specify supported Slurm parameters for variants in the experiments.yml file.

   variants:
     - axis: num_cores
       items:
         - name: c24
           num_nodes: 1
           procs_per_node: 24
           num_threads: 2
           extra_args: []           # empty extra_args as we only want to benchmark with
                                    # different node/cpu settings; do NOT omit this key
         - name: c48
           num_nodes: 2
           procs_per_node: 24
           num_threads: 2
           extra_args: []

When launching your experiments with slurm, the variant ``c24`` will append
``-N 1 --ntasks-per-node 24 -c 2`` to the sbatch command. Analogously for the experiment with
the variant ``c48``.

Next
----

Now that you have entirely set up your experiments, you can modify the experiment combinations
that you want to run. Visit the :ref:`RunMatrix` page for a detailed explanation.
