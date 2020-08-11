#!/usr/bin/env python3

import simexpal
import pandas
import yaml

def parse(run, f):
	output = yaml.load(f, Loader=yaml.Loader)
	return {
		'experiment': run.experiment.name,
		'instance': run.instance.shortname,
		'comparisons': output['comparisons'],
		'swaps': output['swaps'],
		'time': output['time']
	}

cfg = simexpal.config_for_dir()
results = []
for successful_run in cfg.collect_successful_results():
	with successful_run.open_output_file() as f:
		results.append(parse(successful_run, f))

df = pandas.DataFrame(results)
print(df.groupby('experiment').agg('mean'))
