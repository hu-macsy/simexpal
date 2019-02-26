The "experiments.yml" reference
===============================

Simexpal needs an "experiments.yml" file to execute the experiments.
In this page we describe how to write the "experiments.yml" file it to automatically
execute your experiments on the desired instances.
The "experiments.yml" is a YAML file that contains a dictionary with two keys:

- instances: lists all the instances that will be used for the experiments.
- instdir: path to the directory that stores all the instances.
- experiments: lists all the experiments that will be executed on each instance.

Instances
---------
Because instances can be managed automatically if they are taken from public repositories,
the value associated to this key is a list of dictionaries with two keys:

- repo: the source repository of the instances. Use "local" if dealing with local instances.
- items: a list of instances.

An example of how to list a local set of instances is:

.. literalinclude:: ./experiments.yml.example
   :linenos:
   :lines: 1-7
   :language: yaml
   :caption: How to list instances in the experiments.yml file.

Experiments
-----------
This entry is a list of experiments that will be executed on all the instances.
Each experiment includes three keys:

- name: a unique identifier of the experiment.
- args: list of command-line arguments to run the code of the experiment.
- output: where the result of the experiments should be saved.

In the example below we show how to run two experiments (insertion-sort and bubble-sort)
on our instances.
demo.py is the code that executes our experiment and accepts two arguments:
the sorting algorithm and the path of the instance.
The resulting data will be outputted to the standard output.

.. literalinclude:: ./experiments.yml.example
   :linenos:
   :lines: 8-
   :language: yaml
   :caption: How to list experiments in the experiments.yml file.
