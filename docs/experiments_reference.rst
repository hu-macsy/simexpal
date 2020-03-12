The "experiments.yml" reference
===============================

Simexpal needs an "experiments.yml" file to to automatically execute your experiments
on the desired instances. In this page we describe the structure of the "experiments.yml"
file. The "experiments.yml" is a YAML file that contains a dictionary with several keys:

- instances: list of all the instances that will be used for the experiments.
- instdir: path to the directory that stores all the instances.
- experiments: list of all the experiments that will be executed on the instances.

There are also further keys that allow for customization of the experiments and to
automatically build the binaries the experiments run from:

- builds: list of Git builds, which also include build instructions.
- revisions: list of Git revisions of builds.
- variants: list of additional input parameters for experiments.
- matrix: specifies which combinations of experiments, instances, variants and revisions are run.



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
