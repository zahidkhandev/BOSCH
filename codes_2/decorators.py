def decorator(func):
    def wrapper():
        print("******************************")
        func()
        print("********************************")
    return wrapper
 
@decorator
def greet():
    print("Hello, World!")
greet()