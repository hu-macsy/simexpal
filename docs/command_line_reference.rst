Command-line Reference
======================

Simexpal instructions are written as:
::

   simex <instruction> [action] [selection option] [*args]

In the following, we list all simexpal instructions and their arguments.

instances
---------
Checks and eventually downloads the instances for the experiments.
It supports the following actions:

:list: lists all the instances found in the experiments.yml file.
   Available instances are shown in green, unavailable instances in red.
:install: downloads all the missing instances if they are taken from a public repository.
   With the argument ``--overwrite`` it will also download the available instances and
   overwrite them.
:process: ``TODO``
:run-transform: ``TODO``

experiment
----------
Responsible to check, execute and remove experiments.
It supports the following actions:

:list: lists all the experiments.
   Executed experiments are shown in green, failed ones are shown in red, running ones in
   yellow, and the non executed ones in the default command-line color.
:launch: launches all the non executed experiments.
:purge: removes the experimental data according to the `selection option`.
   ``--all`` removes all experiments, ``--todo`` removes all failed experiments, ``--todo``
   removes all completed experiments, ``--experiment <name>`` removes the experiment named
   `name`.
   To actually delete experimental data, this instruction needs a further option ``-f``.
   Otherwise it will just perform a dry run.

builds
------
TODO

archive
-------
Archives all the experimental data into a ``data.tar.gz`` file within the same directory
where the ``experiments.yml`` file is located.
