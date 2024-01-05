.. _Revisions:

Revisions
=========

You might want to take a look at the following pages before exploring revisions:

- :ref:`QuickStart`
- :ref:`AtVariables`
- :ref:`Builds`

Simexpal supports two kinds of revisions: "normal" (static) revisions and develop (dynamic) revisions. If you have
a finished project and only want to run experiments, normal revisions will suffice. If your project is not finished
yet and needs refinement depending on factors like runtime or experiment outputs, you can use develop revisions.

Revisions contain builds and their desired versions. The versions can be specified in the following ways:

- SHA-1 hash of a tagged commit (recommended)
- SHA-1 hash of a top commit
- branch name (resolves to top commit of the branch)

For reproducibility reasons we recommend specifying the SHA-1 hash of a tagged commit.

.. _NormalRevisions:

"Normal" Revisions
------------------

To specify a normal revisions, we use the ``revisions`` key and set the value to a list of dictionaries containing
the keys

- ``name``: name of the revision
- ``build_version``: dictionary of (build, SHA-1 hash/branch)-pairs

.. code-block:: YAML
   :linenos:
   :caption: How to specify normal revisions in the experiments.yml.

   revisions:
     - name: main
       build_version:
         'simexpal': 'd8d421e3c2eaa32311a6c678b15e9e22ea0d8eac'   # SHA-1 hash of a tagged commit
     - name: secondary
       build_version:
         'simexpal': 'master'

In the example above we created the revisions ``main`` and ``secondary``, which both contain the build ``simexpal``.
The ``main`` revision contains a tagged version of simexpal, whereas the ``secondary`` revision contains the latest
commit of the ``master`` branch.
If our revision had more than one build, we would simply add new lines of ``'<build_name>': '<SHA-1 hash>'`` below the
``'simexpal': '...'`` line.

.. _DevRevisions:

Develop Revisions
-----------------

Specifying develop revisions works similarly to specifying :ref:`normal revisions<NormalRevisions>`. The differences
are:

- we add another key ``develop`` and set its value to ``true`` *and*
- we leave the values of the ``build_version`` dict as empty string ``''``.

Values specified for the ``build_version`` key will be ignored for develop
revisions. Instead, the latest commit of the default branch will be checked out
after cloning the repository.

.. code-block:: YAML
   :linenos:
   :caption: How to specify a develop revision in the experiments.yml.

   revisions:
     - name: main
       develop: true
       build_version:
         'simexpal': ''

.. note::
   It is possible to have normal and develop revisions at the same time.
   Use the regular git commands within the cloned repositories used as 
   develop revisions to switch branches or checkout to another commit.

Next
----

Now that you have set up your automated builds, you can visit the :ref:`Experiments` page to define
your experiments.
