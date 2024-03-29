.. _CommandLineReference:

Command-line Reference
======================

simexpal instructions are written as:

::

   simex <instruction> [action] [selection option] [args...]

In the following, we list all simexpal instructions and their arguments.

archive
-------
Archives all the experimental data into a ``data.tar.gz`` file within the same directory
where the ``experiments.yml`` file is located.

.. _cli_builds:

builds
------

Used to download Git repositories and install executables. It supports the
following actions:

:make: downloads a Git repository and executes all build commands.
:purge: deletes all related build files. To confirm this action it needs the ``-f`` argument.
:remake: rebuilds a build from scratch.

All the above actions can be applied to a subset of builds according to the ``--revisions`` and
positional ``builds`` argument. Not specifying an argument will select all respective elements, e.g.,
not specifying the ``--revisions`` argument will lead to the selection of every revision.

develop
-------

Used to download Git repositories and install executables. It also allows you to
redo arbitrary build steps after changing local Git files to take over the local
changes.

The ``develop`` action can be applied to a subset of builds according to the ``--revisions`` and
positional ``builds`` argument (analogously to how it works for the :ref:`simex builds <cli_builds>`
command above).

It further supports the following additional arguments:

:--checkout:      Deletes the local Git repository and clones it.
:--compile:       Compiles the build.
:--configure:     Configures the build.
:--delete-source: Deletes the source directory when purging.
:--install:       Installs the build files.
:--purge:         Deletes all related build files.
:--recheckout:    Deletes the cloned git repository, reclones, regenerates,
                  reconfigures, recompiles, and reinstalls it.
:--recompile:     Recompiles and reinstall the build.
:--reconfigure:   Reconfigures the build.
:--regenerate:    Regenerates the build.
:--reinstall:     Reinstalls the build.
:--reregenerate:  Regenerates, reconfigures, recompiles, and reinstalls the build.

The ``--checkout``, ``--recheckout`` and ``--purge`` arguments further require the ``-f`` argument to confirm
their actions.

experiments
-----------

Used to check, execute and remove experiments. The experiments command accepts
the following actions flags:

:info:   Displays all related instances, instance sets, variant axes and variants
         of experiments on the command line.

:list:   Lists all the experiments. Executed experiments are shown in green,
         failed ones are shown in red, running ones in yellow, and the non
         executed ones in the default command line color. With the argument
         ``--detailed`` it will show every single run. With ``--compact``, all
         runs with the same experiment will be grouped together. The ``--full``
         option forces simexpal to display the full experiment name.

:launch: Launches all the non executed experiments.

:print:  Displays all experimental output, including error outputs, on the command line.

:purge:  Deletes the experimental data. To confirm this action it needs the ``-f`` argument.

:kill:   Terminates jobs submitted to or started by the scheduler. To confirm
         this action it needs the ``-f`` argument.

All the above actions can be applied to a subset of experiments according to a `selection option`,
which can be specified as an additional argument. Supported selection options are:

:--all:                    Selects all the experiments.
:--axes [axes...]:         Selects all experiments with the variant axes from
                           the space separated list of *axes*.
:--run <r>:                Selects the single run *r* given as
                           ``<experiment_display_name>/<instance>``, where
                           ``<experiment_display_name>`` is the name of the
                           experiment as displayed on the command line and
                           ``<instance>`` is the instance name as displayed on
                           the command line.
:--experiment <e>:         Selects the experiment named *e*.
:--failed:                 Selects all the failed experiments.
:--instance <i>:           Selects all experiments with the instance named *i*.
:--instset <i>:            Selects all experiments with the instance set named *i*.
:--unfinished:             Selects all the unfinished experiments.
:--revision <r>:           Selects all experiments with the revision named *r*.
:--variants [variants...]: Selects all experiments with the variants from the
                           space separated list of variants.

instances
---------

The instance command can check the availability of instances, and install
instances. It supports the following flags:

:install:         Installs missing instances. This can also trigger a download if an
                  instance resource is configured accordingly. With the argument
                  ``--overwrite``, this command will reinstall all instances and
                  overwrite existing ones.

:list:            Lists all defined instances. Available instances are shown in green,
                  unavailable instances in red.

:process:         This command will read in all available instances, read the
                  count of vertices and edges per file and print it to a file
                  with the same name as the instance with extension `.info`.
                  This command is therefore specific for graph files.

:run-transform:   Manually runs the defined transformation on instance files.

queue
-----

Triggers actions or prints information concerning the configured experiment
launcher and its queue.

:daemon:       Prints info on the running daemon.

:stop:         Stops the elements in the queue from being processed.

:interactive:  Provides an interactive shell with the queue.

:kill:         Kills the queue process.

:show:         Prints the queued experiments using the queue daemon.