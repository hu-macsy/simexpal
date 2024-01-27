#!/usr/bin/env python3

import argparse
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

def merge_sort(array, min_block_size, min_block_sort_algorithm):
	global n_comparisons
	global n_swaps

	n_comparisons += 1
	if len(array) <= min_block_size:
		return min_block_sort_algorithm(array)

	n_comparisons += 1
	if len(array) == 0:
		return array

	pivot_element = len(array) // 2
	left_array = array[:pivot_element]
	right_array = array[pivot_element:]

	left_array = merge_sort(left_array, min_block_size, min_block_sort_algorithm)
	right_array = merge_sort(right_array, min_block_size, min_block_sort_algorithm)

	k = 0
	i = 0
	j = 0
	while i < len(left_array) and j < len(right_array):
		if left_array[i] < right_array[j]:
			array[k] = left_array[i]
			i = i + 1
		else:
			array[k] = right_array[j]
			j = j + 1
		k = k + 1

	if i < len(left_array):
		while i < len(left_array):
			array[k] = left_array[i]
			i = i + 1
			k = k + 1
	else:
		while j < len(right_array):
			array[k] = right_array[j]
			j = j + 1
			k = k + 1

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

def run_experiment(algo, instance, blockalgorithm, blocksize):
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
	elif algo == 'merge-sort':
		t = -time()

		if (blockalgorithm == 'bubble-sort'):
			sorted_array = merge_sort(array, blocksize, bubble_sort)
		else:
			sorted_array = merge_sort(array, blocksize, insertion_sort)

		t += time()

	else:
		print("Unknown algorithm: ", algo, file=sys.stderr)
		sys.exit(1)

	write_result(algo, sorted_array, t)

def do_main():
	parser = argparse.ArgumentParser()
	parser.add_argument('--algo', type=str, choices=['bubble-sort', 'insertion-sort', 'merge-sort'])
	parser.add_argument('--block_algorithm', type=str, choices=['bubble-sort', 'insertion-sort'], default='bubble-sort')
	parser.add_argument('--block_size', type=int, default=50)
	parser.add_argument('instance', type=str)

	args = parser.parse_args()
	run_experiment(args.algo, args.instance, args.block_algorithm, args.block_size)

do_main()
