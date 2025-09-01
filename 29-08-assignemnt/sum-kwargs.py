def add(*args):
    tot=0
    for i in args:
        tot=tot+i 
    print("total  = " , tot)
add(2,3)    
add(3,4,5,6)
add(2,3,4)

def sum_kwargs(**kwargs):
    return sum(kwargs.values())

result = sum_kwargs(a=2,b=3,c=4)

print("Sum:", result)

