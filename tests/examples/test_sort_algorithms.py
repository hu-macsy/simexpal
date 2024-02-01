#!/usr/bin/env python3

import pytest
import random
import sys
import os

script_dir = os.path.dirname( __file__ )
my_sort_dir = os.path.join( script_dir, '..', '..', 'examples', 'sorting' )
sys.path.append( my_sort_dir )

import my_sorting_algorithms

random.seed(42)
array_size: int = 100
max_int: int = 9999

@pytest.fixture
def random_array():
    return [random.randint(1, max_int) for _ in range(array_size)]

def test_insertion_sort(random_array):
    our_sorted_array, num_comparisons, num_swaps = my_sorting_algorithms.insertion_sort(random_array)

    assert our_sorted_array == sorted(random_array)
    assert num_comparisons > 0
    assert num_swaps > 0

def test_bubble_sort(random_array):
    our_sorted_array, num_comparisons, num_swaps = my_sorting_algorithms.bubble_sort(random_array)

    assert our_sorted_array == sorted(random_array)
    assert num_comparisons > 0
    assert num_swaps > 0

def test_merge_sort(random_array):
    min_blocksize: int = 10
    block_algorithm = my_sorting_algorithms.bubble_sort
    our_sorted_array, num_comparisons, num_swaps = my_sorting_algorithms.merge_sort(random_array, min_blocksize, block_algorithm)

    assert our_sorted_array == sorted(random_array)
    assert num_comparisons > 0
    assert num_swaps > 0