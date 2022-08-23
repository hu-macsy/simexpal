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

There are two types of variants:

1. static variants
2. dynamic variants

Static variants have to be specified individually and thus allow for more customization e.g.
:ref:`setting different environment variables <VariantsSettingEnvironmentVariables>` for each individual
variant. In cases where such customization is not necessary, dynamic variations can be used. By using
:ref:`AtVariables` and syntactic sugar, dynamic variations also simplify writing the ``experiments.yml``.

.. _StaticVariants:

Static Variants
^^^^^^^^^^^^^^^

To specify static variants we will use the following keys:

- ``axis``: name of the variant axis
- ``items``: list of dictionaries, which specify variants belonging to the same axis.

For the variants in the ``items`` list we have to specify the

- ``name``: name of the variant
- ``extra_args``: list of variant arguments

keys.

.. code-block:: YAML
   :linenos:
   :caption: How to specify static variants in the experiments.yml file.

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

.. _DynamicVariants:

Dynamic Variants
^^^^^^^^^^^^^^^^

Dynamic variants work similar to :ref:`static variants <StaticVariants>`. Some differences are the syntax, automatic
assignment of variant names of the form ``<axis_name>:<variant_value>`` to the variants and the introduction
of the :ref:`@-variable <AtVariables>` ``@VARIANT_VALUE:<axis_name>@``.

.. _RangeVariants:

``range`` Variants
~~~~~~~~~~~~~~~~~~

In cases where the values of variants are integers with regular step sizes, we can use ``range``
variants. In order to do so, we will use the

- ``axis``:  name of the variant axis
- ``range``: list with start and stop element
- ``steps``: step size
- ``extra_args``: list of variant arguments

keys.

The ``range`` and ``steps`` keys will generate values ``i`` equivalent to a
``for(int i = start; i <= stop; i += steps)`` loop in C.

The ``experiments.yml`` file in the :ref:`static variants <StaticVariants>` example can then be written in the
following way:

.. code-block:: YAML
   :linenos:
   :caption: How to specify range variants in the experiments.yml file.

    variants:
      - axis: 'block-algo'
        items:
          - name: 'ba-insert'
            extra_args: ['insertion_sort']
          - name: 'ba-bubble'
            extra_args: ['bubble_sort']
      - axis: 'block-size'
        range: [32,64]
        steps: 32
        extra_args: ['@VARIANT_VALUE:block-size@']

The only differences to the :ref:`static variants <StaticVariants>` example is that we created the variant axis
``block-size`` with variants named ``block-size:32`` and ``block-size:64``. Also, we need to specify the
``@VARIANT_VALUE:<axis_name>@`` :ref:`@-variable <AtVariables>` in the ``extra_args`` key to access the values of
the variants.

``enum`` Variants
~~~~~~~~~~~~~~~~~

``enum`` variants can be seen as a generalization of :ref:`range variants <RangeVariants>`. With ``enum``
variants, we can specify arbitrary values explicitly. In order to so, we will use the

- ``axis``:  name of the variant axis
- ``enum``: list of variant values
- ``extra_args``: list of variant arguments

keys.

The ``experiments.yml`` file in the :ref:`range variants <RangeVariants>` example can then be written in the
following way:

.. code-block:: YAML
   :linenos:
   :caption: How to specify enum variants in the experiments.yml file.

    variants:
      - axis: 'block-algo'
        enum: ['insertion_sort', 'bubble_sort']
        extra_args: ['@VARIANT_VALUE:block-algo@']
      - axis: 'block-size'
        range: [32,64]
        steps: 32
        extra_args: ['@VARIANT_VALUE:block-size@']

The only differences to the :ref:`range variants <RangeVariants>` example is that we created the variant axis
``block-algo`` with variants named ``block-algo:insertion_sort`` and ``block-algo:bubble_sort``.

.. _VariantsSettingEnvironmentVariables:

Setting Environment Variables
-----------------------------

.. note::
   Environment variables specified in variants will override the values of environment variables
   specified in the ``experiments`` stanza (if the same variable occurs).

Setting environment variables for variants works similar to
:ref:`setting environment variables for experiments <ExperimentsSettingEnvironmentVariables>`.
For static variants we set the

- ``environ``: dictionary of (environment variable, value)-pairs

key for each item in the ``items`` key. For dynamic variants we set the ``environ`` key on the same
level as the ``axis`` key. For example you can specify environment variables as follows:

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
     - axis: block-algo
       enum: ...
       ...
       environ:
         foo1: 'bar'
     - axis: block-size
       range: ...
       steps: ...
       ...
       environ:
         foo2: 'baz'

With dynamic variants it is also possible to use the :ref:`@-variable <AtVariables>` ``@VARIANT_VALUE:<axis_name>@``
as value for the environment variables.

.. note::
   Dynamic variants of the same ``axis`` will share the environment variables set by ``environ``.


Slurm: ``--ntasks-per-node``, ``-c``, ``-N``
--------------------------------------------

.. note::
   Supported Slurm arguments specified in variants will override the values of supported Slurm
   arguments specified in the ``experiments`` stanza (if the same slurm argument occurs).

The :ref:`supported Slurm arguments in experiments <ExperimentsSupportedSlurmArgs>` are also
supported for variants. For static variants we set the

- ``procs_per_node``: number of tasks to invoke on each node (slurm: ``--ntasks-per-node=n``)
- ``num_threads``: number of cpus required per task (slurm: ``-c``, ``--cpus-per-task=ncpus``)
- ``num_nodes``: number of nodes on which to run (N = min[-max]) (slurm: ``-N``, ``--nodes=N``)

keys for each item in the ``items`` key.


.. _StaticSlurmVariants:
.. code-block:: YAML
   :linenos:
   :caption: How to specify supported Slurm parameters for static variants in the experiments.yml file.

   variants:
     - axis: num_cores
       items:
         - name: c24
           num_nodes: 1
           procs_per_node: 24
           num_threads: 2
           extra_args: []           # empty extra_args as we only want to benchmark with
                                    # different node/cpu settings
         - name: c48
           num_nodes: 2
           procs_per_node: 24
           num_threads: 2
           extra_args: []

When launching your experiments with slurm, the variant ``c24`` will append
``-N 1 --ntasks-per-node 24 -c 2`` to the sbatch command. Analogously for the experiment with
the variant ``c48``.

For dynamic variants we set ``procs_per_node``, ``num_threads`` and ``num_nodes`` on the same
level as the ``axis`` key:

.. code-block:: YAML
   :linenos:
   :caption: How to specify supported Slurm parameters for dynamic variants in the experiments.yml file.

   variants:
     - axis: 'block-size'
       range: [32,64]
       steps: 32
       extra_args: ['@VARIANT_VALUE:block-size@']
       num_nodes: 1
       procs_per_node: 24
       num_threads: 2

.. note::
   Dynamic variants of the same ``axis`` will share the values set by ``procs_per_node``, ``num_threads``
   and ``num_nodes``.

Also, the :ref:`@-variable <AtVariables>` ``@VARIANT_VALUE:<axis_name>@`` can be specified as value of
these keys. E.g. the following is equivalent to the :ref:`static case above <StaticSlurmVariants>`:

.. code-block:: YAML
   :linenos:
   :caption: How to specify supported Slurm parameters as dynamic variants in the experiments.yml file.

   variants:
   - axis: 'num-cores'
     range: [1,2]
     steps: 1
     num_nodes: '@VARIANT_VALUE:num-cores@'
     procs_per_node: 24
     num_threads: 2


Next
----

Now that you have entirely set up your experiments, you can modify the experiment combinations
that you want to run. Visit the :ref:`RunMatrix` page for a detailed explanation.
