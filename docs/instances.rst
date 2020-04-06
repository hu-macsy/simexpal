.. _Instances:

Instances
=========

On this page we describe how to specify instances in the ``experiments.yml`` file. You can
list local instances that consist of one file or several files. More over simexpal can download
remote instances from the `KONECT <http://konect.cc>`_ and `SNAP <https://snap.stanford.edu/data/>`_
repository. It is also possible to assign instances to instance sets that enable a more efficient
usage of the :ref:`command line interface <CommandLineReference>` and are useful when defining
the run matrix.

Instance Directory
------------------

The instance directory is the directory that stores all the instances. The path can be set via
the ``instdir`` key:

.. code-block:: YAML
   :linenos:
   :caption: How to set the instance directory in the experiments.yml file.

    instdir: "<path_to_instance_directory>"

If ``instdir`` is not set, it will default to ``<path_to_experiments.yml_directory>/instances``.
The instance directory will be created if it does not exist already.

.. _LocalInstances:

Local Instances
---------------

To add local instances to the ``instances`` key, we add a list of dictionaries with two keys
to its value:

- ``repo``: source of the instances
- ``items``: a list of instances.

An example of how to list a local set of instances is:

.. literalinclude:: ./experiments.yml.example
   :linenos:
   :lines: 1-7
   :language: yaml
   :caption: How to list local instances in the experiments.yml file.

..
    TODO: Add section on instance generators

Remote Instances
----------------

It is possible to let simexpal download instances from the `KONECT <http://konect.cc>`_
and `SNAP <https://snap.stanford.edu/data/>`_ repository.

To list instances from the SNAP repository, set the value of ``repo`` to ``snap`` and put
the file names without the ``.txt.gz`` extension in the ``items`` list.

For instances from the KONECT repository, set the value of ``repo`` to ``konect`` and put
the internal names of the KONECT instances in the ``items`` list.

.. code-block:: YAML
   :linenos:
   :caption: How to list instances from the SNAP and KONECT repository in the experiments.yml file.

    instdir: "<path_to_instance_directory>"
    instances:
      - repo: snap
        items:
          - facebook_combined
          - wiki-Vote
      - repo: konect
        items:
          - dolphins
          - ucidata-zachary

After listing the instances use

.. code-block:: bash

   $ simex instances install

to download the instances into the instance directory.

Multiple Input Files
--------------------

Until now we only considered experiments with one input file, which might not always be the case.
Below we distinguish two cases:

1. The input filenames only differ in the extension, e.g. ``foo.graph`` and ``foo.xyz``.
2. The input filenames are arbitrary.

Multiple Extensions
^^^^^^^^^^^^^^^^^^^

Listing instances with multiple extensions is similar to listing :ref:`LocalInstances`. The
difference is that we will add the following key:

- ``extensions``: list of extensions that the instance has

.. code-block:: YAML
   :linenos:
   :caption: How to list instances with multiple extensions in the experiments.yml file.

    instdir: "<path_to_instance_directory>"
    instances:
      - repo: local
        extensions:
          - graph
          - xyz
        items:
          - foo
          - bar

The ``experiments.yml`` file above will create the instance ``foo`` which contains the files
``foo.graph`` and ``foo.xyz`` and the instance ``bar`` which contains the files
``bar.graph`` and ``bar.xyz``.

Arbitrary Input Files
^^^^^^^^^^^^^^^^^^^^^

To get an instance with arbitrary input files we will put a list of dictionaries as value for
the ``items`` key. The dictionaries contain two keys:

- ``name``: name of the instance
- ``files``: list of files the instance consists of

.. code-block:: YAML
   :linenos:
   :caption: How to list instances with arbitrary input files in the experiments.yml file.

    instdir: "<path_to_instance_directory>"
    instances:
      - repo: local
        items:
          - name: foo
            files:
              - file1
              - file2
          - name: bar
            files:
              - file3
              - file4

The ``experiments.yml`` file above will create the instance ``foo`` which contains the files
``file1`` and ``file2`` and the instance ``bar`` which contains the files
``file3`` and ``file4``.

Instance Sets
-------------

It is possible to assign instances to instance sets. This is useful when trying to run experiments
that have common instances. Assume you want to run an experiment on the two instances ``instance1``
and ``instance2`` and a different experiment on ``instance2`` and ``instance3``. To do this, you can
use the following key:

- ``set``: list of sets the instance belongs to

.. code-block:: YAML
   :linenos:
   :caption: How to assign instances to instance sets in the experiments.yml file.

    instdir: "<path_to_instance_directory>"
    instances:
      - repo: local
        set: [set1]
        items:
          - instance1
      - repo: local
        set: [set1, set2]
        items:
          - instance2
      - repo: local
        set: [set2]
        items:
          - instance3

In this way we have created the instance set ``set1``, which contains ``instance1`` and ``instance2``
and ``set2``, which contains ``instance2`` and ``instance3``.

Instance sets will also be useful when using the :ref:`command line interface <CommandLineReference>` of
simexpal and when defining the run matrix.