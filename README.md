<p align="center">
  <img width="60%" src="docs/logo/logo.png" alt="simexpal - Simplifying Experimental Algorithmics"><br>
  <a href="https://github.com/hu-macsy/simexpal/actions"><img src="https://github.com/hu-macsy/simexpal/actions/workflows/ci.yml/badge.svg"></a>
  <a href="https://badge.fury.io/py/simexpal"><img src="https://badge.fury.io/py/simexpal.svg"></a>
</p>

# What is SimexPal? 

_SimexPal_ is a python based tool to setup, manage, launch, monitor, and
evaluate algorithmic experiments. _SimexPal_ is mainly developed by the MACSy
(Modelling and Analysis of Complex Systems) group where graph data is at the
heart of most projects. Therefore, the tool provides some special functionality
for graph algorithm experiments. However, this does not limit _SimexPal_ to be
only used for graph algorithm experiments, but is a tool that can be used for
almost all algorithmic experiments. 

Since algorithmic experiments require several tasks in a specific order, the
goal of this tool is to clearly describe and automatize these ordered steps.
Firstly, _SimexPal_ allows to make quick changes to the experiment setup, and
secondly it allows to describe experiments that are easy to repeat. When
describing the necessary steps, even users with no knowledge of _SimexPal_
should be able to quickly setup and execute the described experiments which
allows to reproduce and therefore verify experimental results.

_SimexPal_ consists of both a command line interface (CLI) utility and a python
package. While the CLI  can be used to perform many common tasks with minimal
configuration, the Python package can be employed when more extensive
customization is necessary.

## SimexPal Feature Set Summary

The following is a non-exhaustive list of the functionality provided by
SimexPal:

- resolve external resources such as git repositories
- describe and setup build processes
- describe experiments
- define parameters and parameter permutations
- manage _instances_ / data sets
- run and monitor experiments
- evaluate experiments

## Why should I use SimexPal?

Whether you're a student, an algorithm enthusiast, or a researcher, providing
experiments that can easily be reproduced will support the validity of your
findings. Self written scripts often bind experiments to a narrow set of soft-
and hardware. If not well documented, such scripts may be a source of error, or
the experiments may not be reproduced as intended.

Even though _SimexPal_ may not yet be the perfect algorithmic experiment
management software for all purposes, our goal was to abstract algorithmic
experiments from their hard- and software requirements as well as to provide a
clearly structured and well documented experiment setup. _SimexPal_ will allow
you to share your experiments with third parties, and the third parties to
validate your experimental results and findings with only a minimal description
on how to build and run the experiments.

Ultimately, _SimexPal_ represents an algorithmic experiment management tool with
which one can clearly define their experiment setup and execution, and therefore
majorly contributing to the goal of reproducible experiments.  

# Documentation

Please visit our [readthedocs](https://simexpal.readthedocs.io) document for a
detailed documentation of the _SimexPal_ features.

Our documentation also includes a [quick start
guide](https://simexpal.readthedocs.io/en/latest/quick_start.html) for a quick
and easy step-by-step guide to install and use _SimexPal_.

