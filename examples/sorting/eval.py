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
df = pandas.DataFrame(cfg.collect_successful_results(parse))
print(df.groupby('experiment').agg('mean'))
