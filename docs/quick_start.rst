.. _QuickStart:

Quick Start
===========

.. highlight:: none

The following will introduce you to the most fundamental mechanics of simexpal.
The quick start guide will explain simexpal installation, as well as the
features: instance and input parameter management, launch experiments, monitor
experiments, and evaluate experiments using the output data. Thereafter, we will
have a closer look at the different phases of experiments set up using simexpal
including running experiments, evaluating results, managing instances,
parameterize algorithms, builds and revisions, the run matrix, and launchers and
support for batch schedulers.

Installation
------------

simexpal requires Python 3.

Either you install it via pip3 using:

.. code-block:: bash

   $ pip3 install simexpal

Or you install it using the latest commit of our default branch from GitHub. Of
course, you can also choose to install a specific version (using our tags) or
branch. 

.. code-block:: bash

   $ git clone https://github.com/hu-macsy/simexpal.git
   $ cd simexpal
   $ pip3 install -e .

.. _sortingExample:

Minimal Example and Fundamentals
-------------

The simexpal repository contains a small example which can be used to quickly
get to know the tool. For this section, we compare different sorting algorithms
using multiple instances as input.

1.  Install simexpal as detailed above.

2.  Clone the simexpal repository and navigate to the ``examples/sorting/`` directory:

    .. code-block:: bash

        $ git clone https://github.com/hu-macsy/simexpal.git
        $ cd simexpal/examples/sorting/

    This directory contains an ``experiments.yml`` file which describes the
    configuration of all instances and experiments. In this case each instance
    will be generated using the ``generate.py`` script. Each experiment calls
    ``my_sort.py`` implementing the experiment given the parameters. ``eval.py`` is
    a script that uses simexpal's Python interface to evaluate the experiment
    results.

3.  Generate some instances for the benchmark. First, we list all instances:

    .. code-block:: bash

        # List the instances declared in experiments.yml.
        # Note that missing instances will appear in red.
        $ simex instances

    Output:

    ::

        Instance short name          Instance sets                                               
        -------------------          -------------
        uniform-n1000-s1
        uniform-n1000-s2
        uniform-n1000-s3

    Then, install all instances:

    .. code-block:: bash

        # Generate missing instance files.
        $ simex instances install 

    Output:

    :: 

      Generating instance 'uniform-n1000-s1'
      Generating instance 'uniform-n1000-s2'
      Generating instance 'uniform-n1000-s3'

    In the ``experiments.yml`` the instances are declared as part of the
    ``instances`` stanza. This stanza also declares how to invoke the generator
    script ``generate.py``.

4.  Launch the algorithms on all instances:

    List experiment configurations from experiments.yml.

    .. code-block:: bash

        $ simex e 

    Output:

    ::

        Experiment                           Instance                            Status
        ----------                           --------                            ------
        bubble-sort                          uniform-n1000-s1                    [0]
        bubble-sort                          uniform-n1000-s2                    [0]
        bubble-sort                          uniform-n1000-s3                    [0]
        insertion-sort                       uniform-n1000-s1                    [0]
        insertion-sort                       uniform-n1000-s2                    [0]
        insertion-sort                       uniform-n1000-s3                    [0]
        6 experiments in total

    Launch all experiments using process forks.

    .. code-block:: bash

        $ simex e launch --launch-through=fork

    Output:

    ::

        Launching run bubble-sort/uniform-n1000-s1[0] on local machine
        Launching run bubble-sort/uniform-n1000-s2[0] on local machine
        Launching run bubble-sort/uniform-n1000-s3[0] on local machine
        Launching run insertion-sort/uniform-n1000-s1[0] on local machine
        Launching run insertion-sort/uniform-n1000-s2[0] on local machine
        Launching run insertion-sort/uniform-n1000-s3[0] on local machine

    View the status of the experiments.

    .. code-block:: bash

        $ simex e list

    Output:

    ::

        Experiment                                    Instance                            Status
        ----------                                    --------                            ------
        bubble-sort                                   uniform-n1000-s1                    [0] finished
        bubble-sort                                   uniform-n1000-s2                    [0] finished
        bubble-sort                                   uniform-n1000-s3                    [0] finished
        insertion-sort                                uniform-n1000-s1                    [0] finished
        insertion-sort                                uniform-n1000-s2                    [0] finished
        insertion-sort                                uniform-n1000-s3                    [0] finished
        6 experiments in total

5.  Evaluate the results:

    To evaluate the experiment results, we call the ``eval.py`` script which
    uses the pandas package to aggregate the results. Please make sure that the
    Python package pandas is installed on your machine, or install it via ``pip3
    install pandas``. The script also uses the simexpal Python interface (i.e.,
    the functions ``collect_successful_results()`` and ``open_output_file()``)
    to gather all results.

    .. code-block:: bash

        $ python3 eval.py

    Output:

    ::

                        comparisons          swaps      time
        experiment                                          
        bubble-sort        499500.0  253437.333333  0.053750
        insertion-sort     241891.0  257609.000000  0.027219

.. tip::
    Simexpal supports autocomplete via `argcomplete <https://pypi.org/project/argcomplete/>`_.
    To enable autocomplete, install ``argcomplete`` and enable global completion:

    .. code-block:: bash
      
      $ pip3 install argcomplete
      $ activate-global-python-argcomplete

Running Experiments
-------------------

Let us now take a closer look at running experiments. As an example, we compare
the sorting algorithms *insertion sort* and *bubble sort* using a set of
instances. Please find the resources in our `example folder
<https://github.com/hu-macsy/simexpal/tree/master/examples>`_. 

If you look at the `sorting directory
<https://github.com/hu-macsy/simexpal/tree/master/examples/sorting>`_ in our
examples, you will find `my_sort.py
<https://github.com/hu-macsy/simexpal/blob/master/examples/sorting/my_sort.py>`_
including an implementation of the two algorithms *insertion sort* and *bubble
sort*. 

``my_sort.py`` expects two arguments: 

1. The algorithm name (i.e. *insertion-sort* or *bubble-sort*). 
2. The path to the instance. 

In the above example, we generated a bunch of instances which were written to
the *instances* folder at root level where the ``experiments.yml`` file is
present. 

For this example, we generate a new instance using the ``generate.py`` script.
First, we navigate to the ``sorting`` folder:

.. code-block:: bash

  $ cd examples/sorting

Thereafter, we generate a new instance file which contains 500 randomly
generated integers in list form with one integer per line:

.. code-block:: bash

  $ python3 generate.py -o ./instances/random-500 500

Now we can run *insertion-sort* on the newly generate instance: 

.. code-block:: bash

   python3 my_sort.py --algo=insertion-sort ./instances/random-500

Output:

::

  ...
  - 9949624
  - 9984385
  - 9984385
  swaps: 65114
  time: 0.006702899932861328

Let us continue with configuring simexpal to automatize the experimental pipeline.

Consider the ``experiments.yml`` `file
<https://github.com/hu-macsy/simexpal/blob/master/examples/sorting/experiments.yml>`_
in the root directory. It represents the simexpal configuration read in to run
the experiments on the desired instances. The file is structured as below:

.. literalinclude:: ../examples/sorting/experiments.yml
   :linenos:
   :language: yaml
   :caption: Example of an experiments.yml simexpal configuration file.

The structure of the configuration file will get more attention later on. At
this point, our ``sorting`` directory looks like this: 

::

  sorting
  ├── my_sort.py
  ├── experiments.yml
  └── instances
      └── random_500.list

To add the instance to be used in our experiments, we must add a local file with
it's name *random-500* (no extension) to our instances stanza:

.. code-block:: yaml  

  instances:
    - generator:
        args: ['./generate.py', '--seed=1', '1000']
      items:
        - uniform-n1000-s1
    - generator:
        args: ['./generate.py', '--seed=2', '1000']
      items:
        - uniform-n1000-s2
    - generator:
        args: ['./generate.py', '--seed=3', '1000']
      items:
        - uniform-n1000-s3
    - repo: local
      items:
        - random-500

  experiments:
    - name: insertion-sort
      args: ['./my_sort.py', '--algo=insertion-sort', '@INSTANCE@']
      stdout: out
    - name: bubble-sort
      args: ['./my_sort.py', '--algo=bubble-sort', '@INSTANCE@']
      stdout: out

After having completed this step, we can start using simexpal to run our
experiments including the new instance. The @-Variable ``@INSTANCE@`` will be
use for all instances. A complete list of experiments and their status can be
seen by:

.. code-block:: bash

   $ simex e list

The color of each line represents the status of the experiment:

.. role:: green
.. role:: yellow
.. role:: red

.. raw:: html

    <style> .red {color:red} </style>
    <style> .yellow {color:yellow} </style>
    <style> .green {color:green} </style>

- green :green:`🮆` represents *finished*
- yellow :yellow:`🮆` represents *running*
- red :red:`🮆` represents *failed*
- and the default color represents *not executed*

Experiments can be launched with:

.. code-block:: bash

   $ simex e launch --launch-through=fork

This instruction will launch the non-executed experiments on the local machine.
After all experiments have ben run, all experiment entries should be finished:

.. code-block:: bash

   $ simex e list

Output:

::

  Experiment                                    Instance                            Status
  ----------                                    --------                            ------
  bubble-sort                                   random-500                          [0] finished
  bubble-sort                                   uniform-n1000-s1                    [0] finished
  bubble-sort                                   uniform-n1000-s2                    [0] finished
  bubble-sort                                   uniform-n1000-s3                    [0] finished
  insertion-sort                                random-500                          [0] finished
  insertion-sort                                uniform-n1000-s1                    [0] finished
  insertion-sort                                uniform-n1000-s2                    [0] finished
  insertion-sort                                uniform-n1000-s3                    [0] finished
  8 experiments in total

Evaluating Results
------------------

After the experiments have been run, simexpal can assist with locating and
collecting output data. For this purpose, simexpal can be imported as a Python
package. As simexpal is output format and algorithm agnostic, you need to
provide functionality to parse output files and evaluate results. Parsing output
files can usually be greatly simplified by using standardized formats and
appropriate libraries.

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

Run this Python script to evaluate the experiments:

.. code-block:: bash

  $ python3 eval.py

Output:

::

                  comparisons      swaps      time
  experiment                                      
  bubble-sort        405812.5  205647.25  0.043447
  insertion-sort     196834.5  208978.00  0.021463

Managing Instances
------------------

Before launching the experiments, we need to make sure that all our instances
are available. Instances can be checked with:

.. code-block:: bash

  $ simex instances list

An example output:

::

  Instance short name                      Instance sets                                               
  -------------------                      -------------                                               
  random-500                                                                                           
  uniform-n1000-s1                                                                                     
  uniform-n1000-s2                                                                                    
  uniform-n1000-s3 

Unavailable instances will be shown in red, available instances will be shown in
green. 

If instances are taken from a public repository, they can be downloaded
automatically. We configured the `YAML file
<https://github.com/hu-macsy/simexpal/blob/master/examples/download_instances/experiments.yml>`_
under ``examples/download_instances`` below to use instances from `SNAP
<https://snap.stanford.edu/data/>`_.

.. literalinclude:: ../examples/download_instances/experiments.yml
   :linenos:
   :language: yaml
   :caption: experiments.yml with instances from public repositories.

Please navigate to the subfolder ``examples/download_instances`` and list all
instances:

.. code-block:: bash

  $ simex instances list

Output:

:: 

  Instance short name                      Instance sets                                               
  -------------------                      -------------                                               
  cit-HepTh                                                                                            
  facebook_combined  

The listed instances are shown as not available. To download them, use the
following command:

.. code-block:: bash

   $ simex instances install

Output:

:: 
  
  Downloading instance 'cit-HepTh' from snap repository
  [==================================================]100% (1.26MB/1.26MB)
  Downloading instance 'facebook_combined' from snap repository
  [==================================================]100% (0.21MB/0.21MB)

Now when repeating the ``simex instances list`` command, you'll see that all
instances are available.

.. _parametersAndVariants:

Parameterize Algorithms
-----------------------

When benchmarking algorithms, it is often useful to compare different variants
or parameter configurations. simexpal can manage those variants without
requiring you to duplicate the ``experiments`` stanza multiple times.

As an example, imagine that you want to benchmark the running time of a *merge
sort* algorithm using different minimum block sizes and sorting algorithms for
these blocks. The ``my_sort.py`` script under ``examples/sorting`` provides an
implementation of *merge sort*.

The following extends the original ``experiments.yml`` file with additional
variants for *merge sort* after we defined our instances:

.. code-block:: YAML

    experiments:
      - name: 'merge-sort'
        stdout: out
        args: ['python3', 'my_sort.py', '--algo=merge-sort', '@EXTRA_ARGS@', '@INSTANCE@']

    variants:
      - axis: 'block-size'
        items:
          - name: 'bs2'
            extra_args: ['--block_size=2']
          - name: 'bs20'
            extra_args: ['--block_size=20']
          - name: 'bs200'
            extra_args: ['--block_size=200']
      - axis: 'block-algo'
        items:
          - name: 'bba-insertion'
            extra_args: ['--block_algorithm=insertion-sort']
          - name: 'bba-selection'
            extra_args: ['--block_algorithm=bubble-sort']

    matrix:
      include:
        - experiments: [insertion-sort, bubble-sort]
          axes: []
        - experiments: [merge-sort]
          axes: [block-size, block-algo]

First, we define the new experiment ``merge-sort`` adding the @-Variable
``@EXTRA_ARGS@``. This will allow simexpal to insert additional program
arguments. Second, we define ``variants`` as possible parameter groups for our
experiment. Finally, we must add groups of experiments where for
``insertion-sort`` and ``bubble-sort`` the axes remain empty - as we do not want
to parameterize these experiments. The experiment group with ``merge-sort`` will
be using the variant axes ``block-size`` and ``block-algo``. 

After successfully running all (remaining) experiments, listing the experiments
with:

.. code-block:: bash

  simex e list --full


prints:

::

  Experiment                        started    finished   failures             other
  ----------                        -------    --------   --------             -----
  bubble-sort                                  4/4                             
  insertion-sort                               4/4                             
  merge-sort ~ bba-insertion, bs2              4/4                             
  merge-sort ~ bba-insertion, bs20             4/4                             
  merge-sort ~ bba-insertion, bs200            4/4                             
  merge-sort ~ bba-selection, bs2              4/4                             
  merge-sort ~ bba-selection, bs20             4/4                             
  merge-sort ~ bba-selection, bs200            4/4                             
  32 experiments in total


Builds and Revisions
--------------------

To make sure that experiments always run using the same program binaries,
simexpal can manage internal projects as well as external Git repositories,
automatizing the build process.

Automated builds are controlled by the ``builds`` and ``revisions`` stanzas
in the ``experiments.yml``.

For the remainder of this section, we will will use the `C++ implementation
<https://github.com/hu-macsy/simexpal/tree/master/examples/sorting_cpp>`_ of the
sorting example. We will use simexpal to resolve the dependency and to configure
and compile the C++ project. 

simexpal will invoke CMake commands to build the program; these steps are merely
a list of shell input strings, thus you may use any build environment..

To enable automated builds, we need to add ``builds`` and ``revisions`` stanzas
to ``experiments.yml``. For experiments, to use the correct project, we must use
the ``simexpal`` build. 

.. literalinclude:: ../examples/sorting_cpp/experiments.yml
   :emphasize-lines: 1, 18, 39
   :linenos: 
   :language: yaml
   :caption: experiments.yml for the C++ example of sorting algorithms.

After navigating to ``examples/sorting_cpp``, we must first generate the
instances:

.. code-block:: bash

    $ simex instances install

Now we build the C++ project:

.. code-block:: bash

    $ simex builds make

Once the build process is finished, the experiments can be started as usual
using:

.. code-block:: bash

    $ simex e launch --launch-through=fork 


Run Matrix
----------

In the :ref:`parametersAndVariants` section we saw how we can use simexpal to
specify axes and variants of parameters. For the following example we will take
a look at the ``variants`` stanza of the `C++ Sorting Example
<https://github.com/hu-macsy/simexpal/tree/master/examples/sorting_cpp/experiments.yml>`_:

.. literalinclude:: ../examples/sorting_cpp/experiments.yml
   :emphasize-lines: 43
   :linenos: 
   :language: yaml
   :caption: experiments.yml for the C++ example of sorting algorithms.

simexpal will build every permutation of the experiment, instance, variant and
revision sets. However, there are cases where this is not desired. For example,
you might only want to run certain instance/variant combinations, not all.

Assume you want to run the *quick sort* algorithm with *insertion sort* as base
block algorithm and ``32`` as minimal block size. Additionally you want to run
*quick sort* with *bubble sort* as base block algorithm and use both ``32`` and
``64`` as minimal block sizes.

To achieve this, we need to add a ``matrix`` stanza to ``experiments.yml``. In
our example, this looks like:

.. code-block:: YAML

    matrix:
      include:
        - experiments: [quick-sort]
          variants: [ba-insert, bs32]
          revisions: [main]
        - experiments: [quick-sort]
          variants: [ba-bubble]    
          revisions: [main]

We could explicitly specify ``[ba-bubble, bs32, bs64]`` for the variants of
``quick-sort``. In this case however, it is not necessary as ``bs32`` and
``bs64`` are all the possible values for the ``block-size`` axis.

Using ``simex experiments list --full`` we can confirm that we got our desired
experiments:

.. code-block:: bash

    Experiment                          Instance                            Status
    ----------                          --------                            ------
    quick-sort ~ ba-bubble, bs32 @ main uniform-n1000-s1                    [0] not submitted
    quick-sort ~ ba-bubble, bs32 @ main uniform-n1000-s2                    [0] not submitted
    quick-sort ~ ba-bubble, bs32 @ main uniform-n1000-s3                    [0] not submitted
    quick-sort ~ ba-bubble, bs64 @ main uniform-n1000-s1                    [0] not submitted
    quick-sort ~ ba-bubble, bs64 @ main uniform-n1000-s2                    [0] not submitted
    quick-sort ~ ba-bubble, bs64 @ main uniform-n1000-s3                    [0] not submitted
    quick-sort ~ ba-insert, bs32 @ main uniform-n1000-s1                    [0] not submitted
    quick-sort ~ ba-insert, bs32 @ main uniform-n1000-s2                    [0] not submitted
    quick-sort ~ ba-insert, bs32 @ main uniform-n1000-s3                    [0] not submitted
    9 experiments in total


Launchers and Support for Batch Schedulers
----------------------------------------

To submit experiments to a batch scheduler, simexpal allows you to define
"launchers". A launcher specifies where and how simexpal should submit
experiments. If no launcher (not even a default launcher or
``--launch-through``) is specified, simexpal launches experiments on the local
machine.

Launchers must be defined in the ``launchers.yml`` file located under
``~/.simexpal/launchers.yml``. For example, to submit jobs to the Slurm
partition ``cluster9``, a launcher configuration could look like this:

.. code-block:: YAML

    launchers:
      - name: local-cluster
        default: true
        scheduler: slurm
        queue: cluster9

When launching experiments using ``simex experiments launch``, you can specify
the ``--launcher`` option (e.g., ``simex experiments launch --launcher
local-cluster``) to select a certain launcher. 

.. note::

    The ``default: true`` attribute of a launcher overrides the default behavior
    of launching on the local machine. Hence, there can only be one launcher
    with ``default: true``.