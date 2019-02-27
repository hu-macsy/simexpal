Usage Guide
===========

Installation
------------

Simexpal requires Python 3 and can be installed via pip3:
::

   pip3 install simexpal

Running Experiments
-------------------

Imagine that you want to compare insertion sort and bubble sort on a set of instances.
To this purpose, you create a new "project" directory write a short Python script
demo.py where you implemented the two algorithms and save it into "project".
demo.py accepts two arguments: the algorithm name (i.e. insertion-sort or bubble-sort)
and the path to the instance.
Then, you generated a bunch of instances and placed them in a directory called "instances"
within "project" (in this example we just deal with a single instance named "random_500.list").
Now you can run a sorting algorithm on a specific instance with:
::

   python3 demo.py --algo=insertion-sort ./instances/random_500.list

To keep the example simple, we assume that instances are lists of integers.

You can now start to configure simexpal to automatize your experimental pipeline.
First, you need to create a new "experiments.yml" file within the "project" directory.
This is a configuration file that is read by simexpal to run the experiments on the
desired instances and it is structured as below:

.. literalinclude:: ./example/experiments.yml
   :linenos:
   :language: yaml
   :caption: Example of experiments.yml file

The structure of this file will be better explained later in the guide.
At this point, your "project" directory looks like this:
::

   project
   ├── sort.py
   ├── experiments.yml
   └── instances
       └── random_500.list

After having completed this steps, you can start using simexpal to run your experiments.
A complete list of experiments and their status can be seen by:
::

   simex experiments list

The color of each line represents the status of the experiment:

- Green: finished
- Yellow: running
- Red: failed
- Default: not executed

Experiments can be launched with:
::

   simex experiments launch

This instruction will launch the non executed experiments on the local machine.

Evaluating Results
------------------

TODO

Managing Instances
------------------
Before launching the experiments, make sure that all your instances are available.
Instances can be checked with:
::

   simex instances list

Unavailable instances will be shown in red, otherwise they will be shown in green.
If instances are taken from a public repository, they can be downloaded automatically.
We configured the YAML file below to use instances from `Konect <http://konect.cc/networks/>`_
and `SNAP <https://snap.stanford.edu/data/>`_.

.. literalinclude:: ./graph_example/experiments.yml
   :linenos:
   :language: yaml
   :caption: experiments.yml with instances from public repositories.

All the listed instances can be downloaded within the "./graphs" directory with:
::

   simex instances install

Dealing with Parameters and Variants of an Algorithm
----------------------------------------------------

TODO

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

	simex builds make

Once the build process is finished, the experiments can be started as usual.

.. TODO: Give example: how to pull code from this repo, build it and run it.

Run Matrix
----------

TODO

