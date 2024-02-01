#!/usr/bin/env python3

def insertion_sort(array):
	n_comparisons = 0
	n_swaps = 0

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
		
	return (array, n_comparisons, n_swaps)

def bubble_sort(array):
	n_comparisons = 0
	n_swaps = 0

	for i in range(len(array)):
		for j in reversed(range(i + 1, len(array))):
			n_comparisons += 1
			if array[j] < array[j - 1]:
				n_swaps += 1
				array[j], array[j - 1] = array[j - 1], array[j]
				
	return (array, n_comparisons, n_swaps)

def merge_sort(array, min_block_size, min_block_sort_algorithm):
    n_comparisons = 0
    n_swaps = 0

    n_comparisons += 1
    if len(array) <= min_block_size:
        return min_block_sort_algorithm(array)

    n_comparisons += 1
    if len(array) == 0:
        return array

    pivot_element = len(array) // 2
    left_array = array[:pivot_element]
    right_array = array[pivot_element:]

    left_array, left_comparisons, left_swaps = merge_sort(left_array, min_block_size, min_block_sort_algorithm)
    right_array, right_comparisons, right_swaps = merge_sort(right_array, min_block_size, min_block_sort_algorithm)

    n_comparisons = n_comparisons + left_comparisons + right_comparisons
    n_swaps = n_swaps + left_swaps + right_swaps

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

    larger_array, index = (left_array, i) if i < len(left_array) else (right_array, j)

    while index < len(larger_array):
        array[k] = larger_array[index]
        index = index + 1
        k = k + 1

    return (array, n_comparisons, n_swaps)