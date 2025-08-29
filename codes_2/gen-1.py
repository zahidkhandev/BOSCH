import sys
squares_list = [x*x for x in range(1000000)]
squares_gen =  (x*x for x in range(1000000))
print("List size:", sys.getsizeof(squares_list))     # Large (e.g., ~8 MB+)
print("Generator size:", sys.getsizeof(squares_gen)) # Tiny (e.g., ~200 bytes)


#Generator Expression (like list comprehension, but lazy)
squares = (x*x for x in range(5))  # generator expression
print(next(squares))
print("Welcome to  Generator class")
print(next(squares))
