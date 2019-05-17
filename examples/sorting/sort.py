#!/usr/bin/env python3

import argparse
import bisect
import sys
from time import time
import yaml

def insertion_sort(array):
	sorted_array = [array.pop(0)]
	while len(array) > 0:
		x = array.pop(0)
		j = bisect.bisect_left(sorted_array, x)
		sorted_array.insert(j, x)
	return sorted_array

def bubble_sort(array):
	for i in range(len(array)):
		for j in reversed(range(i + 1, len(array))):
			if array[j] < array[j - 1]:
				array[j], array[j - 1] = array[j - 1], array[j]
	return array

def write_result(algo, sorted_array, t):
	result_dict = {
			'algo' : algo,
			'result' : sorted_array,
			'time' : t
	}
	print(yaml.dump(result_dict, default_flow_style=False))

def read_list(instance):
	try:
		with open(instance, 'r') as f:
			l = [int(line.strip()) for line in f]
			return l
	except IOError as error:
		raise

def run_experiment(algo, instance):
	array = read_list(instance)
	t = 0
	sorted_array = []
	if algo == 'bubble-sort':
		t = -time()
		sorted_array = bubble_sort(array)
		t += time()
	elif algo == 'insertion-sort':
		t = -time()
		sorted_array = insertion_sort(array)
		t += time()
	else:
		print("Unknown algorithm: ", algo, file=sys.stderr)
		sys.exit(1)

	write_result(algo, sorted_array, t)

def do_main():
	parser = argparse.ArgumentParser()
	parser.add_argument('--algo', type=str, choices=['bubble-sort', 'insertion-sort'])
	parser.add_argument('instance', type=str)

	args = parser.parse_args()
	run_experiment(args.algo, args.instance)

do_main()
