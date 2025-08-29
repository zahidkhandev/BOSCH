# A closure is a function that captures and remembers variables from the scope where it was created, even if that scope no longer exists.

def greet(msg):
    def inner_function(name):
        return name+" "+ msg 
    return inner_function
# Create closure
closure = greet("Welcome to Python class  ")
print(closure("Doss"))  

def outer_function(x):
    def inner_function(y):
        return x + y  # inner function uses 'x' from outer scope
    return inner_function
# Create closure
closure = outer_function(10)
print(closure(5))   # 15
print(closure(20))  # 30

