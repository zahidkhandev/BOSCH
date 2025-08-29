numbers = [10, 20, 30]   # list is an iterable
# Convert iterable -> iterator
it = iter(numbers)       # iterator created
print(next(it))  # 10
print(next(it))


numbers = [10, 20, 30]   # list is an iterable
# Convert iterable -> iterator
it = iter(numbers)       # iterator created
print(next(it))  # 10
print(next(it))


def even_numbers(limit):
    for i in range(2, limit+1, 2):
        yield i
 
for num in even_numbers(10):
    print(num)  # 2 4 6 8 10