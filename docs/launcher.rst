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
    TODO: Add section on ForkLauncher, Slurm, SGE

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

- ``launchers``: list of dictionaries, which contain launchers

key.

.. _QueueLauncher:

Queue Launcher
~~~~~~~~~~~~~~

To define a queue launcher we need to add a list entry to the ``launchers`` key, which contains a
dictionary with the

- ``name``: name of the launcher
- ``default``: boolean (``true``/``false``) - whether this is the default launcher or not
- ``scheduler``: type of the launcher

key.

.. code-block:: YAML
   :linenos:
   :caption: How to specify a queue launcher in the launchers.yml file.

    launchers:
        - name: local-queue
          default: true
          scheduler: queue

In this way we created a queue launcher with the name ``local-queue``. We also set it to be the default
launcher.

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

Assume you have a ``launchers.yml`` file set up as in the :ref:`QueueLauncher` section, then
``simex experiments launch --launcher local-queue`` will select the launcher named ``local-queue`` from
the ``launchers.yml`` file to run experiments.

