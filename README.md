<p align="center">
  <img width="60%" src="docs/logo/logo.png" alt="simexpal - Simplifying Experimental Algorithmics"><br>
  <a href="https://github.com/hu-macsy/simexpal/actions"><img src="https://github.com/hu-macsy/simexpal/actions/workflows/ci.yml/badge.svg"></a>
  <a href="https://badge.fury.io/py/simexpal"><img src="https://badge.fury.io/py/simexpal.svg"></a>
</p>

## What is SimexPal? 

`simexpal` is a python based tool to setup, manage, launch, monitor, and
evaluate algorithmic experiments. `simexpal` is mainly developed by the MACSy
(Modelling and Analysis of Complex Systems) group where graph data is at the
heart of most projects. Therefore, the tool provides some special functionality
for graph algorithm experiments. However, this does not limit `simexpal` to be
only used for graph algorithm experiments, but is a tool that can be used for
almost all algorithmic experiments. 

Since algorithmic experiments require several tasks in a specific order, the
goal of this tool is to clearly describe and automatize these ordered steps.
Firstly, `simexpal` allows to make quick changes to the experiment setup, and
secondly it allows to describe experiments that are easy to repeat. When
describing the necessary steps, even users with no knowledge of `simexpal`
should be able to quickly setup and execute the described experiments which
allows to reproduce and therefore verify experimental results.

`simexpal` consists of both a command line interface (CLI) utility and a python
package. While the CLI  can be used to perform many common tasks with minimal
configuration, the Python package can be employed when more extensive
customization is necessary.



**Features.** simexpal assists users with the following operations
- Manage instances: **Download instances** from external sources, **collect information** about instances.
- Manage runs: **Launch** runs and **monitor** their progress, **detect failed runs** and **restart** them, **collect results** of runs.

<!-- Write about reproducibility issues -->

## Documentation

Please refer to the [quick start guide](https://simexpal.readthedocs.io/en/latest/quick_start.html) for further information about
how to install and use simexpal.

