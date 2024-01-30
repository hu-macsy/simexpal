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
    assert my_sorting_algorithms.insertion_sort(random_array)[0] == sorted(random_array)