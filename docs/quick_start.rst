.. _QuickStart:

Quick Start
===========

.. highlight:: none

Installation
------------

Simexpal requires Python 3 and can be installed via pip3:

.. code-block:: bash

   $ pip3 install simexpal

.. _sortingExample:

Quick Example
-------------

The simexpal repository contains a small example that you can try out to quickly get to know
the tool. In this example, we compare different (inefficient) sorting algorithms
on multiple inputs.

.. note::
    While this constitutes a toy example, more complex examples
    can be handled using the same workflow. Indeed, simexpal has successfully been
    used to manage benchmarks that are published in algorithmic research papers.

..
    TODO: Add page about papers, link to it.

1.  Install simexpal as detailed above.

2.  Clone the simexpal repository and navigate to the ``examples/sorting/`` directory:

    .. code-block:: bash

        $ git clone https://github.com/hu-macsy/simexpal.git
        $ cd simexpal/examples/sorting/

    This directory contains an ``experiments.yml`` file that stores the configuration
    of all instances and experiments and some scripts:
    ``generate.py`` is used to generate random instances,
    the ``sort.py`` executes all algorithms and ``eval.py`` is a script that uses
    simexpal's Python interface to evaluate benchmarking results.

3.  Generate some instances for the benchmark:

    .. code-block:: bash

        # List the instances declared in experiments.yml.
        # Note that missing instances will appear in red.
        $ simex instances

    ::

        uniform-n1000-s1
        uniform-n1000-s2
        uniform-n1000-s3

    .. code-block:: bash

        $ simex instances install # Generate missing instance files.

    In the ``experiments.yml`` the instances are declared as part of the
    ``instances`` stanza. This stanza also declares how to invoke the
    generator script ``generate.py``.

4.  Launch the algorithms on all instances:

    .. code-block:: bash

        $ simex experiments # List experiment configurations from experiments.yml.

    ::

        Experiment                           Instance                            Status
        ----------                           --------                            ------
        bubble-sort                          uniform-n1000-s1                    [0]
        bubble-sort                          uniform-n1000-s2                    [0]
        bubble-sort                          uniform-n1000-s3                    [0]
        insertion-sort                       uniform-n1000-s1                    [0]
        insertion-sort                       uniform-n1000-s2                    [0]
        insertion-sort                       uniform-n1000-s3                    [0]

    .. code-block:: bash

        $ simex experiments launch # Launch all configurations locally.

    .. code-block:: bash

        $ simex experiments # Review the status of the experiments.

    ::

        Experiment                           Instance                            Status
        ----------                           --------                            ------
        bubble-sort                          uniform-n1000-s1                    [0] finished
        bubble-sort                          uniform-n1000-s2                    [0] finished
        bubble-sort                          uniform-n1000-s3                    [0] finished
        insertion-sort                       uniform-n1000-s1                    [0] finished
        insertion-sort                       uniform-n1000-s2                    [0] finished
        insertion-sort                       uniform-n1000-s3                    [0] finished

    In the ``experiments.yml`` file, all experiment configurations
    (including the invocation of ``sort.py``) are declared
    as part of the ``experiments`` stanza.

5.  Evaluate the results:

    .. code-block:: bash

        # Here, we use the popular pandas package to aggregate the results.
        # Make sure that pandas is installed on your machine (pip3 install pandas).
        $ ./eval.py

    ::

        experiment      comparisons          swaps      time
        bubble-sort        499500.0  253437.333333  0.091776
        insertion-sort     241891.0  257609.000000  0.039501

    ``eval.py`` is a simple 25 line script that uses the simexpal Python interface
    (i.e., the functions ``collect_successful_results()`` and ``open_output_file()``)
    to gather all results. It uses ``pandas`` to aggregate statistics over all experiments.

.. tip::
    Simexpal supports autocomplete via `argcomplete <https://pypi.org/project/argcomplete/>`.
    To enable autocomplete, install ``argcomplete`` and enable global completion:

    .. code-block:: bash

      $ pip install argcomplete
      $ activate-global-python-argcomplete

Running Experiments
-------------------

As a simple example, we compare Insertion Sort and Bubble Sort on a set of instances
(such an example is available in the  within `examples
<https://github.com/hu-macsy/simexpal/tree/master/examples>`_).
To this purpose, we created a new `sorting
<https://github.com/hu-macsy/simexpal/tree/master/examples/sorting>`_
directory, and wrote a short Python script
`sort.py
<https://github.com/hu-macsy/simexpal/blob/master/examples/sorting/sort.py>`_
where we implemented the two algorithms.
``sort.py`` accepts two arguments: the algorithm name (i.e. insertion-sort or bubble-sort)
and the path to the instance.
Then, you generated a bunch of instances and placed them in a directory called "instances"
within "project" (in this example we just deal with a single instance
`random_500.list
<https://github.com/hu-macsy/simexpal/blob/master/examples/sorting/instances/random_500.list>`_).
Now we can run a sorting algorithm on a specific instance with:
::

   python3 sort.py --algo=insertion-sort ./instances/random_500.list

To keep the example simple, we assume that instances are lists of integers.

We can now start to configure simexpal to automatize the experimental pipeline.
First, we need to create a new `experiments.yml
<https://github.com/hu-macsy/simexpal/blob/master/examples/sorting/experiments.yml>`_
file within the ``sorting`` directory.
This is a configuration file that is read by simexpal to run the experiments on the
desired instances and it is structured as below:

.. literalinclude:: ../examples/sorting/experiments.yml
   :linenos:
   :language: yaml
   :caption: Example of experiments.yml file

The structure of this file will be better explained later in the guide.
At this point, our ``sorting`` directory looks like this:
::

   sorting
   ├── sort.py
   ├── experiments.yml
   └── instances
       └── random_500.list

After having completed this steps, we can start using simexpal to run our experiments.
A complete list of experiments and their status can be seen by:

.. code-block:: bash

   $ simex experiments list

The color of each line represents the status of the experiment:

- Green: finished
- Yellow: running
- Red: failed
- Default: not executed

Experiments can be launched with:

.. code-block:: bash

   $ simex experiments launch

This instruction will launch the non executed experiments on the local machine.

Evaluating Results
------------------

After experiments have been run, simexpal can assist with locating and collecting output data.
To do this, simexpal can be imported as a Python package. As simexpal is output format
and algorithm agnostic,
you need to provide functionality to parse output files and evaluate results.
Parsing output files can usually be greatly simplified by using standardized
formats and appropriate libraries.

The example below (i.e., ``eval.py`` from ``examples/sorting/``)
demonstrates this concept. It uses the simexpal Python package
to obtain all output files and meta data about them. In particular,
it uses the functions ``collect_successful_results()`` and
``open_output_file()`` for this purpose.
A user-supplied parsing function is employed to parse the output files.

.. literalinclude:: ../examples/sorting/eval.py
   :linenos:
   :lines: 7-24
   :language: python

Managing Instances
------------------
Before launching the experiments, make sure that all your instances are available.
Instances can be checked with:

.. code-block:: bash

   $ simex instances list

Unavailable instances will be shown in red, otherwise they will be shown in green.
If instances are taken from a public repository, they can be downloaded automatically.
We configured the YAML file below to use instances from `SNAP <https://snap.stanford.edu/data/>`_.

.. literalinclude:: ../examples/download_instances/experiments.yml
   :linenos:
   :language: yaml
   :caption: experiments.yml with instances from public repositories.

All the listed instances can be downloaded within the ``./graphs`` directory with:

.. code-block:: bash

   $ simex instances install

.. _parametersAndVariants:

Dealing with Parameters and Variants of an Algorithm
----------------------------------------------------

When benchmarking algorithms, it is often useful to compare different
variants or parameter configurations of the same algorithm.
simexpal can manage those variants without requiring you to duplicate
the ``experiments`` stanza multiple times.

As an example, imagine that you want to benchmark the running time of
merge sort using different minimum block sizes, as well as
its running time depending on different algorithms for minimal blocks.

..
    TODO: This example is implemented in directory TODO of the simexpal repository.

Those variants can be handled by simexpal using the following stanzas:

.. code-block:: YAML

    experiments:
      - name: 'merge-sort'
        stdout: out
        args: ['python3', 'sort.py', '--algo=insertion-sort', '@EXTRA_ARGS@', '@INSTANCE@']

    variants:
      - axis: 'block-size'
        items:
          - name: 'bbs1'
            extra_args: ['--base-block-size=1']
          - name: 'bbs10'
            extra_args: ['--base-block-size=10']
          - name: 'bbs50'
            extra_args: ['--base-block-size=50']
      - axis: 'block-algo'
        items:
          - name: 'bba-insertion'
            extra_args: ['--base-block-algorithm=insertion-sort']
          - name: 'bba-selection'
            extra_args: ['--base-block-algorithm=selection-sort']

simexpal will duplicate the experiment for each possible combination
of variants. Such a combination will consist of exactly one variant
for every ``axis`` property.


Automated Builds and Revision Support
-------------------------------------

To make sure that experiments are always run from exactly the same binaries,
it is possible to let simexpal pull your programs from some VCS
(as of version 0.1, only Git is supported) and build them automatically.

Automated builds are controlled by the ``builds`` and ``revisions`` stanzas
in ``experiments.yml``.

In the remainder of this section, we will reconsider the sorting example from the
:ref:`sortingExample` section. Instead of using a Python implementation of the algorithms,
we assume a `C++ implementation <https://github.com/hu-macsy/simexpal/tree/master/examples/sorting_cpp>`_ and use
simexpal's automated build support to compile it. In this example, simexpal will invoke a CMake build system to
build the program; however, simexpal is independent of the particular build system in use.


To enable automated builds, we need to add ``builds`` and ``revisions``
stanzas to ``experiments.yml``. In our example, these look like:

.. code-block:: YAML

    builds:
      - name: simexpal
        git: 'https://github.com/hu-macsy/simexpal'
        configure:
          - args:
            - 'cmake'
            - '-DCMAKE_INSTALL_PREFIX=@THIS_PREFIX_DIR@'
            - '@THIS_CLONE_DIR@/examples/sorting_cpp/'
        compile:
          - args:
            - 'make'
            - '-j@PARALLELISM@'
        install:
          - args:
            - 'make'
            - 'install'

    revisions:
      - name: main
        build_version:
          'simexpal': 'd8d421e3c2eaa32311a6c678b15e9e22ea0d8eac'      # specify the SHA-1 hash of a tagged commit (recommended)
                                                                      # it is also possible to checkout the top commit
                                                                      # of a branch by specifying the SHA-1 hash or
                                                                      # branch name (not recommended for reproducibility reasons)

Next, we have to assign the builds to their respective experiments:

.. code-block:: YAML

    experiments:
      - name: quick-sort
        use_builds: [simexpal]  # specify which builds get used for this experiment
        args: ['quicksort', '@INSTANCE@', '@EXTRA_ARGS@']
        stdout: out

Simexpal resolves the ``@INSTANCE@`` variable to the instance paths and the ``@EXTRA_ARGS@``
to the extra arguments of the variants (that we define below) during runtime.

After ``experiments.yml`` has been adopted, we can run the automated build
using

.. code-block:: bash

    $ simex builds make

Once the build process is finished, the experiments can be started as usual.


Run Matrix
----------

In the :ref:`parametersAndVariants` section we saw how we can use simexpal to specify
variants of experiments. For the following example we will consider this ``variants`` stanza:

.. code-block:: YAML

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

simexpal will build every possible combination of experiment, instance,
variant and revision. There are cases where this is not desired. For example, you might only want
to run certain instance/variant combinations.

Assume you want to run Quicksort with Insertionsort as base block algorithm and ``32`` as
minimal block size. Additionally you want to run Quicksort with Bubblesort as base block
algorithm and use both ``32`` and ``64`` as minimal block sizes.

To achieve this, we need to add a ``matrix`` stanza to ``experiments.yml``.
In our example, this looks like:

.. code-block:: YAML

    matrix:
      include:
        - experiments: [quick-sort]
          variants: [ba-insert, bs32]
          revisions: [main]
        - experiments: [quick-sort]
          variants: [ba-bubble]     # We could explicitly specify [ba-bubble, bs32, bs64]. In this case it is not
                                    # necessary as bs32 and bs64 are all the possible values for the block-size axis
          revisions: [main]

(The full ``experiments.yml`` can be found `here <https://github.com/hu-macsy/simexpal/tree/master/examples/sorting_cpp>`_ .)

Using ``simex experiments list`` we can confirm that we got our desired experiments:

.. code-block:: bash

    Experiment                                    Instance                     Status
    ----------                                    --------                     ------
    quick-sort ~ ba-bubble, bs32 @ main           uniform-n1000-s1             [0] not submitted
    quick-sort ~ ba-bubble, bs32 @ main           uniform-n1000-s2             [0] not submitted
    quick-sort ~ ba-bubble, bs64 @ main           uniform-n1000-s1             [0] not submitted
    quick-sort ~ ba-bubble, bs64 @ main           uniform-n1000-s2             [0] not submitted
    quick-sort ~ ba-insert, bs32 @ main           uniform-n1000-s1             [0] not submitted
    quick-sort ~ ba-insert, bs32 @ main           uniform-n1000-s2             [0] not submitted

Launchers / Support for Batch Schedulers
----------------------------------------

To submit experiments to a batch scheduler, simexpal allows you to define "launchers".
A launcher specifies where and how simexpal should submit experiments. If no launcher
(not even a default launcher or ``--launch-through``) is specified,
simexpal launches experiments on the local machine.

Launchers are defined in a file ``~/.simexpal/launchers.yml``. For example,
to submit jobs to the Slurm partition ``fat-nodes``, a launcher configuration
could look like this:

.. code-block:: YAML

    launchers:
      - name: local-cluster
        default: true
        scheduler: slurm
        queue: fat-nodes

When launching experiments using ``simex experiments launch``, you can specify
the ``--launcher`` option (e.g., ``simex experiments launch --launcher local-cluster``)
to select a certain launcher. Note that the ``default: true`` attribute
of a launcher overrides the default behavior of launching on the local machine
(hence, there can only be one launcher with ``default: true``).

