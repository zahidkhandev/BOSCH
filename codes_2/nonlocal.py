
#In order to call the variable that is not local to the local function we use the identifer nonlocal
def outer():
    x = 10
    def inner():
        nonlocal x 
        x=x+1
        print("Inner x:", x)
    inner()
outer()

