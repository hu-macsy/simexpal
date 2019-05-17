Usage Guide
===========

.. highlight:: none

Installation
------------

Simexpal requires Python 3 and can be installed via pip3:

.. code-block:: bash

   $ pip3 install simexpal

Quick Example
-------------

The simexpal repository contains a small example that you can try out to quickly get to know the tool.

1.  Install simexpal as detailed above.

2.  Clone the simexpal repository and navigate to the `examples/sorting/` directory:

    .. code-block:: bash

        $ git clone https://github.com/hu-macsy/simexpal.git
        $ cd simexpal/examples/sorting/

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

TODO: Example

Managing Instances
------------------
Before launching the experiments, make sure that all your instances are available.
Instances can be checked with:

.. code-block:: bash

   $ simex instances list

Unavailable instances will be shown in red, otherwise they will be shown in green.
If instances are taken from a public repository, they can be downloaded automatically.
We configured the YAML file below to use instances from `Konect <http://konect.cc/networks/>`_
and `SNAP <https://snap.stanford.edu/data/>`_.

.. literalinclude:: ../examples/download_instances/experiments.yml
   :linenos:
   :language: yaml
   :caption: experiments.yml with instances from public repositories.

All the listed instances can be downloaded within the "./graphs" directory with:

.. code-block:: bash

   $ simex instances install

Dealing with Parameters and Variants of an Algorithm
----------------------------------------------------

When benchmarking algorithms, it is often useful to compare different
variants or parameter configurations of the same algorithm.
simexpal can manage those variants without requiring you to duplicate
the ``experiments`` stanza multiple times.

As an example, imagine that you want to benchmark the running time of
merge sort using different minimum block sizes, as well as
its running time depending on different algorithms for minimal blocks.
This example is implemented in directory TODO of the simexpal repository.

Those variants can be handled by simexpal using the following stanzas:

.. code-block:: YAML

    experiments:
      - name: 'merge-sort'
        output: stdout
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

In the remainder of this section, we will reconsider the sorting example from
TODO. Instead of using a Python implementation of the algorithms,
we will work with a C implementation and use simexpal's automated build support to compile it.
In the simexpal repository, sample C code for the problem can be found
in `TODO`. In this example, simexpal will invoke a CMake build system to build the program;
however, simexpal is independent of the particular build system in use.

To enable automated builds, we need to add ``builds`` and ``revisions``
stanzas to ``experiments.yml``. In our example, these look like:

.. code-block:: YAML

	builds:
	  - name: networkit
		git: 'https://github.com/hu-macsy/simexpal.git'
		configure:
		  - args:
			  - 'cmake'
			  - '-DCMAKE_INSTALL_PREFIX=@THIS_PREFIX_DIR@'
			  - '-DCMAKE_BUILD_TYPE=RelWithDebInfo'
			  - '@THIS_CLONE_DIR@/TODO'
		compile:
		  - args: ['make', '-j@PARALLELISM@']
		install:
		  - args: ['make', 'install']

After ``experiments.yml`` has been adopted, we can run the automated build
using

.. code-block:: bash

	$ simex builds make

Once the build process is finished, the experiments can be started as usual.

.. TODO: Give example: how to pull code from this repo, build it and run it.

Run Matrix
----------

TODO

