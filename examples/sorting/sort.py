#!/usr/bin/env python3

import argparse
import bisect
import sys
from time import time
import yaml

n_comparisons = 0
n_swaps = 0

def insertion_sort(array):
	global n_comparisons
	global n_swaps

	for i in range(1, len(array)):
		elem = array[i]
		for k in range(i):
			n_comparisons += 1
			if array[k] > elem:
				break
		for j in reversed(range(k + 1, i)):
			n_swaps += 1
			array[j + 1] = array[j]
		array[k] = elem
	return array

def bubble_sort(array):
	global n_comparisons
	global n_swaps

	for i in range(len(array)):
		for j in reversed(range(i + 1, len(array))):
			n_comparisons += 1
			if array[j] < array[j - 1]:
				n_swaps += 1
				array[j], array[j - 1] = array[j - 1], array[j]
	return array

def write_result(algo, sorted_array, t):
	result_dict = {
		'algo' : algo,
		'result' : sorted_array,
		'comparisons': n_comparisons,
		'swaps': n_swaps,
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
