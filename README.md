# simexpal: Simplifying Experimental Algorithmics

simexpal is a collection of tools to manage, launch, monitor and evaluate algorithmic experiments
(e.g. performance benchmarks).
The goal of this toolbox is to automatize various repetitive tasks that occur whenever such experiments
need to be executed. simexpal consists of both a command line (CLI) utility and a Python package.
While the CLI utility can be used to perform many common tasks with minimal configuration,
the Python package can be employed when more extensive customization is necessary.

**Features.** simexpal assists users with the following operations
- Manage instances: **Download instances** from external sources, **collect information** about instances.
- Manage runs: **Launch** runs and **monitor** their progress, **detect failed runs** and **restart** them, **collect results** of runs.

<!-- Write about reproducibility issues -->

## Installation

## Getting started

**Step 1: experiments.yml** Create a YAML file to describe your algorithmic experiments.

```yaml
instances:
  - repo: local
    items:
      - random_500.list
      - partially_sorted_500.list

experiments:
  - name: insertion-sort
    args: ['./demo.py', '--algo=insertion_sort', '@INSTANCE@']
  - name: bubble-sort
    args: ['./demo.py', '--algo=bubble_sort', '@INSTANCE@']
    output: stdout
```


