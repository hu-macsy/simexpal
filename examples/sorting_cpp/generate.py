#!/usr/bin/env python3

import argparse
import random

parser = argparse.ArgumentParser()
parser.add_argument('-o', type=str, help="path of output file", default="/dev/stdout")
parser.add_argument('--seed', type=int, help="seed for random generator")
parser.add_argument('--range', type=int, help="range of integers", default=10e6)
parser.add_argument('n', type=int, help="number of integers to generate")

args = parser.parse_args()

numbers = []
random.seed(args.seed)
for i in range(args.n):
    numbers.append(random.randint(1, args.range))

with open(args.o, 'w') as f:
    for num in numbers:
        f.write(str(num)+'\n')
