import random

n = 5000 
numbers = []
for i in range(n):
    numbers.append(random.randint(1, 1e6))

with open('./random.list', 'w') as f:
    for num in numbers:
        f.write(str(num)+'\n')

