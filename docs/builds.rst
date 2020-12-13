.. _Builds:

Builds
======

You might want to take a look at the following pages before exploring automated builds:

- :ref:`QuickStart`
- :ref:`AtVariables`

To ensure reproducibility of experiments, it is possible to let simexpal pull programs from a VCS (currently
only Git is supported) and build them automatically. To achieve this, we need to specify a ``builds`` and
``revisions`` stanza in the ``experiments.yml``.

On this page we will explain the ``builds`` key and mainly use the
`C++ example <https://github.com/hu-macsy/simexpal/tree/master/examples/sorting_cpp>`_ from the
:ref:`QuickStart` guide in order to do so. For example, we will explain how to specify a Git repository or
a local build that does not come from a VCS, enable the automated build support and the directories involved
in the build process. Furthermore we will present additional options such as pulling Git submodules and setting
additional environment variables for the build process.

You can find information regarding the ``revisions`` key on the :ref:`Revisions` page.

.. _SpecifyingGitRepository:

Specifying a Git Repository
---------------------------

To state our git repository, we use the keys

- ``name``: (arbitrary) name of the build
- ``git``: link to the Git repository

as follows:

.. code-block:: YAML
   :linenos:
   :caption: How to specify a Git repository in the experiments.yml file.

    builds:
      - name: simexpal
        git: https://github.com/hu-macsy/simexpal

.. _PullingGitSubmodules:

Pulling Git Submodules
----------------------

If your program contains Git submodules you need to set the

- ``recursive-clone``: boolean (``true``/``false``) - whether to pull git submodules recursively or not

key to ``true`` in order for simexpal to pull the respective files.

.. code-block:: YAML
   :linenos:
   :caption: How to let simexpal pull Git submodules.

    builds:
      - name: networkit
        git: https://github.com/networkit/networkit
        recursive-clone: true

If ``recursive-clone`` is not set, it will default to ``false``.

Specifying Builds Without Version Control
-----------------------------------------

Specifying builds without version control works similar to :ref:`SpecifyingGitRepository`. The differences are

- we omit the ``git`` key *and*
- store the local build files in ``./develop/<build_name>@<revision_name>``.

**As of now local builds are only supported for** :ref:`DevRevisions` **as we can not guarantee reproducibility
without some kind of identifier, e.g, a commit hash.**

All the options below also apply for local builds (we just need to omit the ``git`` key, where applicable).

Automated Builds
----------------

To enable automated build support, we can specify the following keys:

- ``regenerate``: list of dictionaries containing regeneration parameters
- ``configure``: list of dictionaries containing configuration parameters
- ``compile``: list of dictionaries containing compilation parameters
- ``install``: list of dictionaries containing installation parameters


.. code-block:: YAML
   :linenos:
   :caption: How to specify configuration, compilation and installation parameters in the experiments.yml file.

   builds:
     - name: simexpal
       git: 'https://github.com/hu-macsy/simexpal'
       configure:
         - args:
             - 'cmake'
             - '-DCMAKE_INSTALL_PREFIX=@THIS_PREFIX_DIR@'
             - '@THIS_CLONE_DIR@/examples/sorting_cpp/'
       compile:
         - args:
             - 'make'
             - '-j@PARALLELISM@'
       install:
         - args:
             - 'make'
             - 'install'

The order of the build steps is as follows:

1. the specified :ref:`revision <Revisions>` of the build (and possibly its submodules) will be pulled
2. regeneration
3. configuration
4. compilation
5. installation

The purpose of the `regeneration` step is to prepare the source directory before the build starts, e.g., by
downloading additional dependencies or subprojects.

During the `configuration` step we can configure our project, e.g, by running ``cmake`` or using a
``./configure`` script.

Analogously for the `compilation` and `installation` step we can compile and install our project during
those steps, e.g, by running ``make`` and ``make install``.

To specify the build parameters, we will use the ``args`` key and set the value to a list of arguments. Arguments
are stated separately, e.g., ``make install`` becomes a list containing ``make`` and ``install``. In the example
above, we used CMake as build system; however, simexpal is independent of the particular build system in use.

Setting Environment Variables
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

It is possible to set environment variables for each build step. To achieve this, we can use the

- ``environ``: dictionary of (environment variable, value)-pairs

key as follows:

.. code-block:: YAML
   :linenos:
   :caption: How to specify environment variables for the configuration step in the experiments.yml file.

   builds:
     - name: simexpal
       git: 'https://github.com/hu-macsy/simexpal'
       configure:
         - args:
             - 'cmake'
             - '-DCMAKE_INSTALL_PREFIX=@THIS_PREFIX_DIR@'
             - '@THIS_CLONE_DIR@/examples/sorting_cpp/'
           environ:
               'CXX': '/path/to/g++'
               'CC': '/path/to/gcc'
       compile:
         ...
       install:
         ...

Specifying environment variables for other steps works analogously to specifying environment variables for the
configuration step (as seen above). If an environment variable already exists, then the given path will be
preprended to it.

Setting the Working Directory
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The default working directories (see :ref:`BuildDirectories`) for each build step are the same for
:ref:`normal revisions<NormalRevisions>` and :ref:`develop revisions<DevRevisions>` and are as follows:

+---------------+-----------------------------+
| Step          |  Default Working Directory  |
+===============+=============================+
| regeneration  |  clone directory            |
+---------------+-----------------------------+
| configuration |  compilation directory      |
+---------------+-----------------------------+
| compilation   |  compilation directory      |
+---------------+-----------------------------+
| installation  |  installation directory     |
+---------------+-----------------------------+

We can change the working directories by adding the

- ``workdir``: path of the working directory

key to the respective dictionaries of the build steps.

.. code-block:: YAML
   :linenos:
   :caption: How to specify the working directory for the configuration step in the experiments.yml file.

   builds:
     - name: simexpal
       git: 'https://github.com/hu-macsy/simexpal'
       configure:
         - args:
             - 'cmake'
             - '-DCMAKE_INSTALL_PREFIX=@THIS_PREFIX_DIR@'
             - '@THIS_CLONE_DIR@/examples/sorting_cpp/'
           workdir: '/arbitrary/directory/path'
       compile:
         ...
       install:
         ...

Specifying the working directory for other steps works analogously to specifying the working directory for the
configuration step (as seen above).

Extra Paths
-----------

For many UNIX packages it is standard to install the executable in the ``@THIS_PREFIX_DIR@/bin`` directory.
This is why simexpal only checks those directories by default when looking for an executable. However, this
assumption might not always be correct, for example, when using a custom build system. To cover those cases,
we specify the

- ``extra_paths``: list of extra paths, which simexpal should check when running an experiment that uses this build

key.

.. code-block:: YAML
   :linenos:
   :caption: How to specify extra paths of builds in the experiments.yml file.

   builds:
     - name: build1
       ...
       extra_paths: ['/path/to/executable']

When running an experiment that uses this build, simexpal will prepend the paths given in ``extra_paths`` to
the ``PATH`` environment variable.

.. _DependentBuilds:

Dependent Builds
----------------

There are cases where a build is dependent on other builds e.g. it needs the path to certain builds which are built
before. For this case we use the

- ``requires``: list of required builds

key, which contains a list of builds that need to be built before the
current build. In this way we make sure that simexpal builds the required builds beforehand.

.. code-block:: YAML
   :linenos:
   :caption: How to specify dependent builds in the experiments.yml file.

   builds:
     - name: build1
       ...
       requires:
         - build2
         - build3
       ...
     - name: build2
       ...
     - name: build3
       ...

.. _BuildDirectories:

Build Directories
-----------------

Depending on the kind of the :ref:`revision <Revisions>` used for the builds, simexpal uses different directories. In
the following subsections we will cover the directories for :ref:`normal revisions<NormalRevisions>` and
:ref:`develop revisions<DevRevisions>`.

.. _BuildDirectoriesNormalBuilds:

Build Directories for Normal Builds
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
A :ref:`normal revision<NormalRevisions>` in simexpal uses the ``/builds`` directory, which contains the four
subdirectories

- repository directory,
- clone directory,
- compilation directory and
- installation/prefix directory,

during the build process.

The `repository directory` contains some internal information related to the builds e.g. internal tags that are
used by simexpal to handle multiple :ref:`revisions <Revisions>` of programs. This directory should normally
not be of interest for a user.

The `clone directory` contains the actual program files from a checked out branch.

The `compilation directory` contains the compilation and internal simexpal files.

The `install/prefix directory` contains the installation (usually) and internal simexpal files.

Below you can find the shortened directory structure of our
`C++ example <https://github.com/hu-macsy/simexpal/tree/master/examples/sorting_cpp>`_ example. The
repository directory has ``<build_name>`` as prefix and ``.repo`` as suffix. The clone, compilation and
installation directory have ``<build_name>@<revision_name>`` as prefix and the first two have ``.clone``
and ``.compile`` as suffix respectively. The installation directory does not have any suffix. The internal
simexpal files have the suffix ``.simexpal``.

.. code-block:: bash
   :caption: Build directories for normal builds used by simexpal during the build process.

   /path/to/experiments.yml/directory
   ├── CMakeLists.txt
   ├── builds
   │   ├── simexpal.repo                        # repository directory
   │   │   ├── internal simexpal
   │   │   ├── ...
   │   │   └── files/directories
   │   ├── simexpal@main                        # installation/prefix directory
   │   │   ├── bin
   │   │   │   └── quicksort                    # our executable
   │   │   └── installed.simexpal               # internal simexpal file
   │   ├── simexpal@main.clone                  # clone directory
   │   │   ├── checkedout.simexpal              # internal simexpal file
   │   │   ├── regenerated.simexpal             # internal simexpal file
   │   │   ├── project
   │   │   ├── ...
   │   │   └── files/directories
   │   └── simexpal@main.compile                # compilation directory
   │       ├── configuration and compilation
   │       ├── ...
   │       ├── files/directories
   │       ├── compiled.simexpal                # internal simexpal file
   │       └── configured.simexpal              # internal simexpal file
   ├── experiments.yml
   └── quicksort.cpp

Build Directories for Develop Builds
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

A :ref:`develop revision<DevRevisions>` in simexpal uses the ``/dev-builds`` directory, which contains the two
subdirectories

- compilation directory and
- installation/prefix directory

and the ``/develop`` directory, which contains the

- clone directory,

during the build process:

The functions of the respective directories are as :ref:`before<BuildDirectoriesNormalBuilds>` (for local builds
the clone directory contains the local program files).

Below you can find the shortened directory structure of our
`C++ example <https://github.com/hu-macsy/simexpal/tree/master/examples/sorting_cpp>`_ example
(if ``recursive-clone`` was set to ``True``). The clone, compilation and installation directory have
``<build_name>@<revision_name>`` as prefix. Additionally, the compilation directory has ``.compile``
as suffix. The clone directory is located in the ``/develop`` directory, whereas the compilation and
installation directories are located in the ``/dev-builds`` directory. The internal simexpal files have
the suffix ``.simexpal``.

.. code-block:: bash
   :caption: Build directories for dev-builds used by simexpal during the build process.

   /path/to/experiments.yml/directory
   ├── CMakeLists.txt
   ├── dev-builds
   │   ├── simexpal@main                        # installation/prefix directory
   │   │   ├── bin
   │   │   │   └── quicksort                    # our executable
   │   │   └── installed.simexpal               # internal simexpal file
   │   └── simexpal@main.compile                # compilation directory
   │       ├── configuration and compilation
   │       ├── ...
   │       ├── files/directories
   │       ├── compiled.simexpal                # internal simexpal file
   │       └── configured.simexpal              # internal simexpal file
   ├── develop
   │   └── simexpal@main                        # clone directory
   │       ├── project
   │       ├── ...
   │       ├── files/directories
   │       ├── checkedout.simexpal              # internal simexpal file
   │       └── regenerated.simexpal             # internal simexpal file
   ├── experiments.yml
   └── quicksort.cpp

Next
----

To get a more detailed understanding of revisions and fully set up your builds, visit the :ref:`Revisions` page.
