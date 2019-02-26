Usage Guide
===========

Listing Experiments
-------------------
A complete list of experiments and their status can be seen by:
::

   simexpal experiments list

The color of each line represents the status of the experiment:

- Green: finished
- Yellow: running
- Red: failed
- Default: not executed

Running Experiments
-------------------
Experiments can be launched with:
::

   simexpal experiments launch

This instruction will launch the non executed experiments on the local machine.

Managing Instances
------------------
Before launching the experiments, make sure that all your instances are available.
Instances can be checked with:
::

   simexpal instances list

Unavailable instances will be shown in red, otherwise they will be shown in green.
If instances are taken from a public repository, they can be downloaded with:
::

   simexpal instances install

Automated Builds
----------------

Dealing with Revisions
----------------------
