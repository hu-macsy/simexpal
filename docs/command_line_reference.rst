.. _CommandLineReference:

Command-line Reference
======================

Simexpal instructions are written as:
::

   simex <instruction> [action] [selection option] [args...]

In the following, we list all simexpal instructions and their arguments.

archive
-------
Archives all the experimental data into a ``data.tar.gz`` file within the same directory
where the ``experiments.yml`` file is located.

experiments
-----------
Responsible to check, execute and remove experiments.
It supports the following actions:

:info: displays all related instances, instance sets, variant axes and variants of experiments
   on the command-line.
:list: lists all the experiments.
   Executed experiments are shown in green, failed ones are shown in red, running ones in
   yellow, and the non executed ones in the default command-line color. With the argument
   ``--detailed`` it will show every single run. With ``--compact`` all runs with the same
   experiment will be grouped together. The ``--full`` option forces simexpal to display the
   full experiment name.
:launch: launches all the non executed experiments.
:purge: deletes the experimental data. To confirm this action it needs the ``-f`` argument.
:print: displays all experimental output, including error outputs, on the command-line.

All the above actions can be applied to a subset of experiments according to a `selection option`,
which can be specified as an additional argument. Supported selection options are:

:``--all``: selects all the experiments.
:``--axes [axes...]``: selects all experiments with the variant axes from the space separated list of axes.
:``--run <r>``: selects the single run given as ``<experiment_display_name>/<instance>``, where
    ``<experiment_display_name>`` is the name of the experiment as displayed on the command-line and
    ``<instance>`` is the instance name as displayed on the command-line.
:``--experiment <e>``: selects the experiment named ``e``.
:``--failed``: selects all the failed experiments.
:``--instance <i>``: selects all experiments with the instance named ``i``.
:``--instset <i>``: selects all experiments with the instance set named ``i``.
:``--unfinished``: selects all the unfinished experiments.
:``--revision <i>``: selects all experiments with the revision named ``r``.
:``--variants [variants...]``: selects all experiments with the variants from the space separated list of variants.

instances
---------
Checks and eventually downloads the instances for the experiments.
It supports the following actions:

:list: lists all the instances found in the experiments.yml file.
   Available instances are shown in green, unavailable instances in red.
:install: downloads all the missing instances if they are taken from a public repository.
   With the argument ``--overwrite`` it will also download the available instances and
   overwrite them.
:process: caches information about instances.
:run-transform: manually runs a transformation on instance files.

