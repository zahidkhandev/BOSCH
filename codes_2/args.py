def add(*args):
    tot=0
    for i in args:
        tot=tot+i 
    print("total  = " , tot)
add(2,3)    
add(3,4,5,6)
add(2,3,4)

# **kwargs -->Keyword or key value  
# *kwargs --> variable no of arguments
 
def sum_kwargs(**kwargs):
    return sum(kwargs.values())
 
# Example usage
# result = sum_kwargs(a=10, b=20, c=30, d=40)
result = sum_kwargs(a=2,b=3,c=4)

print("Sum:", result)   # Output: Sum: 100

