#!/usr/bin/env python3

from time import time
import argparse
import argparse
import os
import random
import sys
import yaml

script_dir = os.path.dirname( __file__ )
my_sort_dir = os.path.join( script_dir, '..', 'sorting', )
sys.path.append( my_sort_dir )

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

def run_experiment(algo, array):
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
	else:
		print("Unknown algorithm: ", algo, file=sys.stderr)
		sys.exit(1)

	write_result(algo, sorted_array, n_comparisons, n_swaps, t)

def do_main():
	parser = argparse.ArgumentParser()
	parser.add_argument('--seed', type=int, help="seed for random generator")
	parser.add_argument('n', type=int, help="number of integers to generate")
	parser.add_argument('--algo', type=str, choices=['bubble-sort', 'insertion-sort'])

	args = parser.parse_args()

	numbers = []
	random.seed(args.seed)
	for i in range(args.n):
		numbers.append(random.randint(1, 10e6))

	args = parser.parse_args()
	run_experiment(args.algo, numbers)

do_main()
