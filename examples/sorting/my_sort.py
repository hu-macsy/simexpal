#!/usr/bin/env python3

import argparse
import sys
from time import time
import yaml

import my_sorting_algorithms

def write_result(algo, sorted_array, n_comparisons, n_swaps, t):
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

def run_experiment(algo, instance, blockalgorithm, blocksize):
	n_comparisons: int = 0
	n_swaps: int = 0
	array = read_list(instance)
	t = 0
	sorted_array = []
	if algo == 'bubble-sort':
		t = -time()
		sorted_array, n_comparisons, n_swaps = my_sorting_algorithms.bubble_sort(array)
		t += time()
	elif algo == 'insertion-sort':
		t = -time()
		sorted_array, n_comparisons, n_swaps = my_sorting_algorithms.insertion_sort(array)
		t += time()
	elif algo == 'merge-sort':
		t = -time()

		chosen_blockalgorithm = my_sorting_algorithms.bubble_sort if blockalgorithm == 'bubble-sort' else my_sorting_algorithms.insertion_sort
		sorted_array, n_comparisons, n_swaps = my_sorting_algorithms.merge_sort(array, blocksize, chosen_blockalgorithm)

		t += time()

	else:
		print("Unknown algorithm: ", algo, file=sys.stderr)
		sys.exit(1)

	write_result(algo, sorted_array, n_comparisons, n_swaps, t)

def do_main():
	parser = argparse.ArgumentParser()
	parser.add_argument('--algo', type=str, choices=['bubble-sort', 'insertion-sort', 'merge-sort'])
	parser.add_argument('--block_algorithm', type=str, choices=['bubble-sort', 'insertion-sort'], default='bubble-sort')
	parser.add_argument('--block_size', type=int, default=50)
	parser.add_argument('instance', type=str)

	args = parser.parse_args()
	run_experiment(args.algo, args.instance, args.block_algorithm, args.block_size)

do_main()
