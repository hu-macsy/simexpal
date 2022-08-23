.. _Launcher:

Launcher
=========

On this page we describe the different launchers for experiments. It is possible to use the local
machine or batch schedulers like `Slurm <https://slurm.schedmd.com/overview.html>`_ or
`Oracle Grid Engine <https://docs.oracle.com/cd/E19680-01/html/821-1541/docinfo.html#scrolltoc>`_
(formerly SGE) to run experiments. The launchers can be selected by adding further arguments to
the ``simex experiments launch`` command or by setting up a ``launchers.yml`` file. The structure
of this file will also be explained on this page.

In the following sections, we consider the
`sorting expample <https://github.com/hu-macsy/simexpal/tree/master/examples/sorting>`_ from the
:ref:`QuickStart` guide.

..
    TODO: Add section on SGE

Fork Launcher
-------------

Simexpal uses the fork launcher if no further configurations are made. The fork launcher launches
experiments on the local machine. In contrast to the :ref:`QueueLauncher`, the fork launcher launches
the experiments immediately in the current terminal and blocks until completion of the experiments.

Launching Experiments
^^^^^^^^^^^^^^^^^^^^^

To launch experiments through the fork launcher we can simply use the ``simex experiments launch``
command (if no launcher configurations were made), :ref:`set up a launchers.yml file <launchers_yml>`
or add the ``--launch-through=fork`` argument to the ``simex experiments launch`` command:

.. code-block:: bash

    $ simex experiments launch   # no launcher configurations were made beforehand

and

.. code-block:: bash

    $ simex experiments launch --launch-through=fork

will output

.. code-block:: bash

    Launching run bubble-sort/uniform-n1000-s1[0] on local machine
    Launching run bubble-sort/uniform-n1000-s2[0] on local machine
    Launching run bubble-sort/uniform-n1000-s3[0] on local machine
    Launching run insertion-sort/uniform-n1000-s1[0] on local machine
    Launching run insertion-sort/uniform-n1000-s2[0] on local machine
    Launching run insertion-sort/uniform-n1000-s3[0] on local machine

.. _QueueLauncher:

Queue Launcher
--------------

The queue launcher is mainly useful in scenarios where no sophisticated batch scheduler (e.g.
`Slurm <https://slurm.schedmd.com/overview.html>`_) is available, especially when launching
experiments on a remote machine over ``ssh``. In this case it does not require an active connection.
As the name suggests, the queue launcher puts the jobs in a queue and executes them sequentially.
It is possible to start a queue launcher as a daemon or interactively in a terminal. You can launch
experiments and monitor/stop/kill the launcher.

Starting the Launcher
^^^^^^^^^^^^^^^^^^^^^

As Daemon
~~~~~~~~~

To start the queue launcher as a daemon you need to have the
`systemd <https://www.freedesktop.org/wiki/Software/systemd/>`_ service manager installed. Then, use
``simex queue daemon`` to start the launcher:

.. code-block:: bash

    $ simex queue daemon
    Running as unit run-rdc0128bd4cd343e393681898359e5c69.service. # systemd output

Terminal
~~~~~~~~

You can start the queue launcher in a terminal so that it is possible to directly see internal
states of the launcher. You will then work from another terminal window in order to send commands to
the launcher. To start the launcher, use ``simex queue interactive``:

.. code-block:: bash

    $ simex queue interactive
    Serving on /home/username/.extl.sock  # internal message of the queue launcher

Troubleshooting
~~~~~~~~~~~~~~~

If the daemon was not closed properly via the ``stop`` or ``kill`` command, a UNIX socket remains on the
file system. In this case you need to add the ``--force`` argument to the ``simex queue interactive`` or
``simex queue daemon`` command to start the launcher. Alternatively, you can delete the socket manually.
The default path for the socket is ``~/.extl.sock``.

Launching Experiments
^^^^^^^^^^^^^^^^^^^^^

To launch experiments through the queue launcher we need to :ref:`set up a launchers.yml file <launchers_yml>`
or add the ``--launch-through=queue`` argument to the ``simex experiments launch`` command:

.. code-block:: bash

    $ simex experiments launch --launch-through=queue
    Submitting run bubble-sort/uniform-n1000-s1[0] on to local queue launcher
    Submitting run bubble-sort/uniform-n1000-s2[0] on to local queue launcher
    Submitting run bubble-sort/uniform-n1000-s3[0] on to local queue launcher
    Submitting run insertion-sort/uniform-n1000-s1[0] to local queue launcher
    Submitting run insertion-sort/uniform-n1000-s2[0] to local queue launcher
    Submitting run insertion-sort/uniform-n1000-s3[0] to local queue launcher

Show the Status
^^^^^^^^^^^^^^^

It is possible to query the launcher for the current run, pending runs and the number of completed runs.
To do that, you can use ``simex queue show``:

.. code-block:: bash

    $ simex queue show
    Currently running:   bubble-sort/uniform-n1000-s3[0]
    Pending runs:        insertion-sort/uniform-n1000-s1[0]
                         insertion-sort/uniform-n1000-s2[0]
                         insertion-sort/uniform-n1000-s3[0]
    Completed runs:      2

Terminate
^^^^^^^^^

The launcher can be terminated by using the ``stop`` or ``kill`` command. The differences of those
commands are stated below.

- ``simex queue stop``: terminate the launcher after finishing all pending jobs
- ``simex queue kill``: terminate the launcher immediately

Slurm Launcher
--------------

`Slurm <https://slurm.schedmd.com/overview.html>`_ is a cluster management and job scheduling system,
which simexpal can use to submit experiments.

Launching Experiments
^^^^^^^^^^^^^^^^^^^^^

To launch experiments through the Slurm launcher we need to :ref:`set up a launchers.yml file <launchers_yml>`.
Alternatively, we can add the ``--launch-through=slurm`` and ``--queue=<queue>`` (where ``<queue>`` is the name
of the partition to use) argument to the ``simex experiments launch`` command. If ``--queue`` is omitted, the
default slurm partition will be used:

.. code-block:: bash

   $ simex e launch --launch-through=slurm
   Submitting run bubble-sort/uniform-n1000-s1[0] to default slurm partition
   Submitting run bubble-sort/uniform-n1000-s2[0] to default slurm partition
   Submitting run bubble-sort/uniform-n1000-s3[0] to default slurm partition
   Submitted batch job 287454

   Submitting run insertion-sort/uniform-n1000-s1[0] to default slurm partition
   Submitting run insertion-sort/uniform-n1000-s2[0] to default slurm partition
   Submitting run insertion-sort/uniform-n1000-s3[0] to default slurm partition
   Submitted batch job 287455

Show the Status
^^^^^^^^^^^^^^^

The status of experiments can be listed via the ``simex experiments`` (or short: ``simex e``)
command. When encountering experiments that are currently submitted to or started by Slurm,
simexpal will additionally query Slurm using its ``squeue`` command to verify the status. If
the ``squeue`` command outputs an unexpected status, simexpal will return the ``broken`` status.

.. code-block:: bash

   $ simex e
   Experiment                              Instance                            Status
   ----------                              --------                            ------
   bubble-sort                             uniform-n1000-s1                    [0] started
   bubble-sort                             uniform-n1000-s2                    [0] started
   bubble-sort                             uniform-n1000-s3                    [0] started
   insertion-sort                          uniform-n1000-s1                    [0] submitted
   insertion-sort                          uniform-n1000-s2                    [0] submitted
   insertion-sort                          uniform-n1000-s3                    [0] submitted

Terminate
^^^^^^^^^

It is possible to terminate experiments that are already submitted to or started by Slurm. To
do so, we can use ``simex experiments kill`` (internally ``scancel`` will be used). To confirm
the termination of experiments, we need to add the ``-f`` argument to the command.

.. code-block:: bash

   $ simex experiments kill -f
   Killing run bubble-sort/uniform-n1000-s1[0] with Slurm jobid 287454_0
   Killing run bubble-sort/uniform-n1000-s2[0] with Slurm jobid 287454_1
   Killing run bubble-sort/uniform-n1000-s3[0] with Slurm jobid 287454_2
   Killing run insertion-sort/uniform-n1000-s1[0] with Slurm jobid 287455_0
   Killing run insertion-sort/uniform-n1000-s2[0] with Slurm jobid 287455_1
   Killing run insertion-sort/uniform-n1000-s3[0] with Slurm jobid 287455_2

Troubleshooting
^^^^^^^^^^^^^^^

When encountering unexpected statuses, we can use ``simex experiments print`` to check the experiments
error output and manually check the error/output files of Slurm located in ``aux/_slurm/``. Each Slurm
job has a respective ``<job_id>-<array_id>.err`` and ``<job_id>-<array_id>.out`` file. If the job is not
part of a job array ``-<array_id>`` is omitted in the name.

.. _launchers_yml:

"launchers.yml" File
--------------------

The ``launchers.yml`` file contains a list of launchers. By setting up a ``launchers.yml`` file we can
omit additional arguments in the ``simex experiments launch`` command or select launchers, which are
defined in it. In the following sections, we will see how to setup and use our ``launchers.yml``. First,
we need to create the ``launchers.yml`` file in the ``~/.simexpal/`` folder:

.. code-block:: bash

    $ mkdir ~/.simexpal     # Create the ~/.simexpal/ folder if it does not exist already
    $ cd ~/.simexpal        # Navigate into ~/.simexpal/
    $ touch launchers.yml   # Create an empty launchers.yml file

Launchers
^^^^^^^^^

To specify launchers in the ``launchers.yml`` file we need to set the

- ``launchers``: list of dictionaries containing launchers

key. Each dictionary contains the

- ``name``: name of the launcher
- ``default``: boolean (``true``/``false``) - whether this is the default launcher or not
- ``scheduler``: type of the launcher

keys.

Fork Launcher
~~~~~~~~~~~~~

To define a fork launcher we need to add a list entry to the ``launchers`` key, which contains a
dictionary with the

- ``name``: name of the launcher
- ``default``: boolean (``true``/``false``) - whether this is the default launcher or not
- ``scheduler``: type of the launcher

key.

.. code-block:: YAML
   :linenos:
   :caption: How to specify a fork launcher in the launchers.yml file.

    launchers:
        - name: local-fork
          default: true
          scheduler: fork

In this way we created a fork launcher with the name ``local-fork``. We also set it to be the default
launcher.

.. _QueueLauncherYml:

Queue Launcher
~~~~~~~~~~~~~~

To define a queue launcher we need to set ``scheduler: queue``:

.. code-block:: YAML
   :linenos:
   :caption: How to specify a queue launcher in the launchers.yml file.

    launchers:
        - name: local-queue
          default: true
          scheduler: queue

In this way we created a queue launcher with the name ``local-queue``. We also set it to be the default
launcher.

Slurm Launcher
~~~~~~~~~~~~~~

To define a Slurm launcher we need to set ``scheduler: slurm``. Also, we can choose the partition
the experiments are run on by setting the

- ``queue``: name of the partition to use

key. If ``queue`` is not specified, Slurm will use the default partition.

.. code-block:: YAML
   :linenos:
   :caption: How to specify a Slurm launcher in the launchers.yml file.

    launchers:
        - name: local-cluster
          default: true
          scheduler: slurm
          queue: fat-nodes

In this way we created a Slurm launcher with the name ``local-cluster``. We also set it to be the default
launcher and use the partition ``fat-nodes``.

Command Line Interface
^^^^^^^^^^^^^^^^^^^^^^

Default Launcher
~~~~~~~~~~~~~~~~

When setting ``default: true`` for a launcher, ``simex experiments launch`` will run experiments
with this launcher.

.. warning::
    There can only be one launcher with ``default: true``. Having multiple launchers with ``default: true``
    will lead to a ``RuntimeError``.

Selecting the Launcher
~~~~~~~~~~~~~~~~~~~~~~

When launching experiments using ``simex experiments launch``, you can specify the ``--launcher`` option
to select a certain launcher defined in the ``launchers.yml`` file. For example:

Assume you have a ``launchers.yml`` file set up as in the :ref:`QueueLauncherYml` section, then
``simex experiments launch --launcher local-queue`` will select the launcher named ``local-queue`` from
the ``launchers.yml`` file to run experiments.

