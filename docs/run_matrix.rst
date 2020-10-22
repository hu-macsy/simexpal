.. _RunMatrix:

Run Matrix
==========

You might want to take a look at the following pages before exploring the run matrix:

- :ref:`QuickStart`
- :ref:`AtVariables`
- :ref:`Instances`
- :ref:`Builds`
- :ref:`Revisions`
- :ref:`Experiments`
- :ref:`Variants`

Simexpal will build every possible combination of :ref:`experiment <Experiments>`,
:ref:`instance <Instances>`, :ref:`variant <Variants>` and :ref:`revision <Revisions>`.
There are cases where this is not desired. For example, you might only want to run certain
instance/variant combinations. On this page we describe how to use the ``matrix`` key in the
``experiments.yml`` file and will mainly use the
`C++ example <https://github.com/hu-macsy/simexpal/tree/master/examples/sorting_cpp>`_ from
the :ref:`QuickStart` guide in order to do so.

Include Experiments
-------------------

Currently the ``matrix`` key works by specifying all the experiment combinations that you want
to include. Therefore, we will specify the

- ``include``: list of dictionaries, which specify included experiment combinations

key.

Each entry of ``include`` can contain the following keys:

- ``experiments``: list of included experiment names
- ``instsets``: list of included instance set names
- ``axes``: list of included axis names
- ``variants``: list of included variant names
- ``revisions``: list of included revision names

Simexpal will then build the cross product of each experiment, instance set, variant and revision
for each entry in ``include``. Omitting a key in ``include`` will select all possible elements of
the respective key, e.g., omitting ``revisions`` is equivalent to specifying the ``revisions`` key
with all possible revisions.

The ``matrix`` key of

.. code-block:: YAML
    :linenos:

    matrix:
      include:
        - experiments: [quick-sort]
          variants: [ba-insert, bs32]
          revisions: [main]
        - experiments: [quick-sort]
          variants: [ba-bubble]
          revisions: [main]

(The full ``experiments.yml`` can be found `here <https://github.com/hu-macsy/simexpal/tree/master/examples/sorting_cpp>`_ .)

results in the following experiments (using ``simex experiments list`` to display them):

.. code-block:: bash

    Experiment                                    Instance                     Status
    ----------                                    --------                     ------
    quick-sort ~ ba-bubble, bs32 @ main           uniform-n1000-s1             [0] not submitted
    quick-sort ~ ba-bubble, bs32 @ main           uniform-n1000-s2             [0] not submitted
    quick-sort ~ ba-bubble, bs64 @ main           uniform-n1000-s1             [0] not submitted
    quick-sort ~ ba-bubble, bs64 @ main           uniform-n1000-s2             [0] not submitted
    quick-sort ~ ba-insert, bs32 @ main           uniform-n1000-s1             [0] not submitted
    quick-sort ~ ba-insert, bs32 @ main           uniform-n1000-s2             [0] not submitted

.. note::
    If the ``axes`` key is omitted and the ``variants`` key does not contain any variant of an axis, then
    every variant of this axis will be selected. If this is not intended you need to specify the ``axes``
    key with the names of the desired axes.

If we wanted the second entry of the ``include`` key in the ``experiments.yml`` above, to only include
the variant ``ba-bubble`` (without any other variants of other axes), we would need to specify the
``axes`` key like this:

.. code-block:: YAML
    :linenos:

    matrix:
      include:
        - experiments: [quick-sort]
          variants: [ba-insert, bs32]
          revisions: [main]
        - experiments: [quick-sort]
          axes: [block-algo]
          variants: [ba-bubble]
          revisions: [main]

In this way  we obtain the experiments:

.. code-block:: bash

    Experiment                                    Instance                     Status
    ----------                                    --------                     ------
    quick-sort ~ ba-bubble @ main                 uniform-n1000-s1             [0] not submitted
    quick-sort ~ ba-bubble @ main                 uniform-n1000-s2             [0] not submitted
    quick-sort ~ ba-insert, bs32 @ main           uniform-n1000-s1             [0] not submitted
    quick-sort ~ ba-insert, bs32 @ main           uniform-n1000-s2             [0] not submitted

Repetitions
-----------

.. note::
   Repetitions specified in the run matrix will override the values of ``repeat`` specified in the
   ``experiments`` stanza.

Similarly to :ref:`repeating experiments <ExperimentsRepeat>` we can repeat all experiment combinations
of an ``include`` entry by specifying

- ``repetitions``: integer - number of times all combinations of an ``include`` entry are repeated.

To repeat experiments twice, we can define the key as follows:

.. code-block:: YAML
    :linenos:
    :caption: How to specify repetitions in the matrix key of an experiments.yml file.

    matrix:
      include:
        - experiments: [...]
          variants: [...]
          ...
          repetitions: 2

The default value of ``repetitions`` is ``1``.

More Examples
-------------

Experiments with Different Instance Types
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

When you are dealing with experiments that have different instance types, e.g. :ref:`MultipleExtensions`
Instances and :ref:`LocalInstances`, you need to use :ref:`InstanceSets` and the ``instsets`` key
appropriately. This means:

First, you have to assign your instances with different types to separate instance sets. For example, you
can assign your multiple extension instances to the instance set ``multiple_extension_set`` and your local
instances to ``local_instance_set``. Assuming you have defined two experiments ``multiple_ext_experiment``
and ``local_experiment`` that take multiple extension and local instances as input respectively, you can
specify your run matrix as follows:

.. code-block:: YAML
    :linenos:
    :caption: How to specify experiments with different instance types in the run matrix of the experiments.yml file.

    matrix:
      include:
        - experiments: [multiple_ext_experiment]
          instsets: [multiple_extension_set]
          ...
        - experiments: [local_experiment]
          instsets: [local_instance_set]
          ...

In this way, we can assure that the right instance paths are passed to each experiment.
