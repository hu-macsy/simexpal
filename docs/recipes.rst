Recipes
========

.. highlight:: none

Automated Builds of Python Packages
-----------------------------------

Python packages are often installed using ``pip3`` (or ``pip``)
and use a different directory layout than native programs.
In particular, they do not make use of directories like ``bin/``,
``lib/`` or ``include/``. To still support automated builds of
Python packages, simexpal offers the ``exports_python`` property
for builds. This property takes a directory name (relative to
``@THIS_PREFIX_DIR@``) and exports
this name via the ``PYTHONPATH`` environment variable such that
the Python interpreter is able to load packages from this directory.
It can be used in conjunction with the ``--target`` option of ``pip3``
to locally install Python packages during automated builds.

.. code-block:: YAML

	builds:
	  - name: some_python_package
	    exports_python: 'python-packages/'
	    # [...]
	    install:
	      - args: ['pip3', 'install', '--target=@THIS_PREFIX_DIR@/python-packages', '@THIS_SOURCE_DIR@']

Note that on Debian-based Linux distributions, you need to pass ``--system`` to ``pip3``
to override the default of ``--user`` (which does not work with ``--target``).

