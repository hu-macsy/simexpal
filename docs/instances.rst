.. _Instances:

Instances
=========

You might want to take a look at the following pages before exploring instances:

- :ref:`QuickStart`
- :ref:`AtVariables`

On this page we describe how to specify instances in the ``experiments.yml`` file. You can
list local instances that consist of zero or more files. More over simexpal can download
remote instances from the `SNAP <https://snap.stanford.edu/data/>`_ repository, Git repositories
and arbitrary URLs. It is also possible to assign instances to instance sets that enable a more
efficient usage of the :ref:`command line interface <CommandLineReference>` and are useful when
defining the run matrix.

.. _InstanceDirectory:

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

.. _RemoteInstances:

Remote Instances
----------------

It is possible to let simexpal download instances from `SNAP <https://snap.stanford.edu/data/>`_,
a URL and a Git repository. In the sections below, we will see how to list the different
kinds of remote instances in the ``experiments.yml``.

After listing the instances we need to use

.. code-block:: bash

   $ simex instances install

to download the instances into the instance directory.

.. note::
    1st December 2020: It is no longer possible to automatically download `KONECT <http://konect.cc>`_
    instances as the website is no longer publicly available. It is still possible to list them and
    execute supported actions, e.g, transforming the instances to edgelist format via
    ``simex instances run-transform --transform='to_edgelist'`` if you already have them saved locally.

.. _SNAPInstances:

Instances From SNAP
^^^^^^^^^^^^^^^^^^^

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

Instances From a URL
^^^^^^^^^^^^^^^^^^^^

To list instances from a URL, we use the following keys:

- ``method``: download method
- ``url``: URL of the instance

We set the value of the ``method`` key to ``'url'`` and specify the URL of the instance in the
``url`` key.

.. code-block:: YAML
   :linenos:
   :caption: How to list instances from a URL in the experiments.yml file.

   instdir: "<path_to_instance_directory>"
   instances:
     - method: url
       url: 'https://raw.githubusercontent.com/hu-macsy/simexpal/master/simexpal/schemes/@INSTANCE_FILENAME@'
       items:
         - 'experiments.json'
         - 'launchers.json'

The :ref:`@-variable <AtVariables>` ``@INSTANCE_FILENAME@`` in the URL (from the example above) resolves to
the elements in the ``items`` key. Thus, we have listed the two instances ``experiments.json`` and
``launchers.json``, which come from
`<https://raw.githubusercontent.com/hu-macsy/simexpal/master/simexpal/schemes/experiments.json>`_ and
`<https://raw.githubusercontent.com/hu-macsy/simexpal/master/simexpal/schemes/launchers.json>`_ respectively.

Automatic Unpacking of Archives
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When dealing with instances from a URL, you might encounter archives. Simexpal can automatically unpack archives
by specifying the archive format in the

- ``format``: archive format of the instance

key. Supported formats are formats supported by
`shutil.unpack_archive() <https://docs.python.org/3.6/library/shutil.html#archiving-operations>`_ and also gzip'ed files,
i.e.:

- ``zip``: ZIP file (if the `zlib <https://docs.python.org/3.6/library/zlib.html#module-zlib>`_ module is available)
- ``tar``: uncompressed tar file
- ``gztar``: gzip’ed tar-file (if the `zlib <https://docs.python.org/3.6/library/zlib.html#module-zlib>`_ module is available)
- ``bztar``: bzip2’ed tar-file (if the `bz2 <https://docs.python.org/3.6/library/bz2.html#module-bz2>`_ module is available)
- ``xztar``: xz’ed tar-file (if the `lzma <https://docs.python.org/3.6/library/lzma.html#module-lzma>`_ module is available)
- ``gz``: gzip'ed file.

.. code-block:: YAML
   :linenos:
   :caption: How to automatically unpack instances from a URL in the experiments.yml file.

   instdir: "<path_to_instance_directory>"
   instances:
     - method: url
       url: https://snap.stanford.edu/data/@INSTANCE_FILENAME@.txt.gz
       items:
         - 'facebook_combined'
         - 'wiki-Vote'
       format: gz

.. note::
   This only serves as an example. Downloading instances from the `SNAP repository <https://snap.stanford.edu/data/>`_
   should be done as mentioned :ref:`above <SNAPInstances>`.

In the ``experiments.yml`` above we specified two instances ``facebook_combined`` and ``wiki-Vote``, which both come
from the `SNAP repository <https://snap.stanford.edu/data/>`_. As visible in the URL, the instances are gzip archives.
By setting ``format: gz`` we make sure that the appropriate unpacker is used.


Instances From Git
^^^^^^^^^^^^^^^^^^

To list instances from a Git repository, we use the following keys:

- ``method``: download method
- ``git``: link to the Git repository
- ``repo_name``: name of the directory to clone into
- ``commit``: SHA-1 hash
- ``git_subdir``: subdirectory of the instance in the Git repository


We set the value of the ``method`` key to ``'git'`` and specify the Git URL of the instance in the
``git`` key. The ``repo_name`` states the local directory name of the Git repository. When installing
the instance, the Git repository will be stored in ``<instance_dir>/<repo_name>``. The ``commit`` value
specifies the version of the instance given as SHA-1 hash. It is also possible to specify other revision
parameters, e.g. ref names. For reproducibility reasons the former variant is recommended. If the instance
is not located in the root directory of the Git repository, we will need to specify the subdirectory of
the instance in ``git_subdir``.

.. code-block:: YAML
   :linenos:
   :caption: How to list instances from a Git repository in the experiments.yml file.

   instdir: "<path_to_instance_directory>"
   instances:
     - method: git
       git: 'https://github.com/hu-macsy/simexpal'
       repo_name: 'foo'
       commit: 'master'
       items:
         - 'setup.py'
         - 'pytest.ini'
     - method: git
       git: 'https://github.com/hu-macsy/simexpal'
       repo_name: 'foo'
       commit: 'd5e598f292b90cd7ef2e77d7a478ec52d42279df'
       git_subdir: 'simexpal/schemes/'
       items:
         - 'experiments.json'
         - 'launchers.json'

In the example above we clone the simexpal repository into ``<instance_dir>/foo``. Then ``setup.py`` and
``pytest.ini`` of the current ``master`` branch and ``simexpal/schemes/experiments.json`` and
``simexpal/schemes/launchers.json`` of the specified commit ``d5e598f292b90cd7ef2e77d7a478ec52d42279df``
will be downloaded into the instance directory.

Multiple Input Files
--------------------

Until now we only considered experiments with one input file, which might not always be the case.
Below we distinguish two cases:

1. The input filenames only differ in the extension, e.g. ``foo.graph`` and ``foo.xyz``.
2. The input filenames are arbitrary.

.. _MultipleExtensions:

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

.. _ArbitraryInputFiles:

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

Fileless Instances
------------------

There are cases where instances are not defined by a file but rather by some input parameters, e.g.
algorithms that generate their data themselves and only need input parameters like ``--seed 10``.
Specifying fileless instances works similar to specifying :ref:`ArbitraryInputFiles`. The difference is,
that we set ``files: []`` to indicate that we are dealing with a fileless instance and use the

- ``extra_args``:  list of extra arguments

key to specify our extra arguments.

.. code-block:: YAML
   :linenos:
   :caption: How to list fileless instances in the experiments.yml file.

    instances:
      - repo: local
        items:
          - name: foo
            files: []
            extra_args: ['--seed', '10']

.. _InstanceExtraArguments:

Extra Arguments
---------------

We can set extra arguments for instance blocks and individual instances, which can be appended to the
experiment arguments when the respective instance is used. In order to specify such instances, we use the

- ``extra_args``: list of extra arguments

key.

.. note::
   It is possible to have instances with common extra arguments and additional individual extra arguments
   by adding the ``extra_args`` key to the respective places (see below).

In order to specify common extra arguments for instance blocks, we simply add the ``extra_args`` key to them.

.. code-block:: YAML
   :linenos:
   :caption: How to list instances with common extra arguments in the experiments.yml file.

    instdir: "<path_to_instance_directory>"
    instances:
      - repo: local
        extra_args: ['some','extra_args']
        ...
        items:
          - instance1
          - instance2
      - repo: local
        extra_args: ['some','extra_args']
        ...
        items:
          - instance3
          - instance4

In order to specify individual extra arguments for :ref:`LocalInstances`, :ref:`RemoteInstances` and
:ref:`MultipleExtensions` we need to change the ``items`` key from a list of instances to a list of
dictionaries containing the

- ``name``: name of the instance `and`
- ``extra_args``

key, e.g.,

.. code-block:: YAML
   :linenos:
   :caption: How to list local/remote/multiple extension instances with individual
             extra arguments in the experiments.yml file.

   instances:
     - repo: local # local instances with extra arguments
       items:
         - name: inst1
           extra_args: ['some','extra_args']
         - name: inst2
           extra_args: ['some','extra_args']
     - repo: snap # remote instances with extra arguments
       items:
         - name: facebook_combined
           extra_args: ['some', 'extra_args']
         - name: wiki-Vote
           extra_args: ['some', 'extra_args']
     - repo: local # multiple extension instances with extra args
       items:
         - name: inst3
           extra_args: ['some', 'extra_args']
         - name: inst4
           extra_args: ['some', 'extra_args']
       extensions: [ext1, ext2]

For :ref:`ArbitraryInputFiles` we only need to add the ``extra_args`` key
to the dictionaries of the instances, e.g,

.. code-block:: YAML
   :linenos:
   :caption: How to list arbitrary input file instances with individual extra arguments
             in the experiments.yml file.

    instances:
     - repo: local
       items:
         - name: inst3
           files: [file1, file2]
           extra_args: ['some', 'extra', 'argument']
         - name: inst4
           files: [file1, file2]
           extra_args: ['some', 'extra', 'argument']

.. _InstanceSets:

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
simexpal and when defining the :ref:`RunMatrix`.

Next
----

To set up your automated builds, visit the :ref:`Builds` page. If you do not plan on using
automated builds, you can visit the :ref:`Experiments` page to set up your experiments.
