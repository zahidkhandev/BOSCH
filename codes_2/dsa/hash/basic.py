my_hash_set = [None,'Jones',None,'Lisa',None,'Bob',None,'Siri','Pete',None]
def hash_function(value):
    sum_of_chars = 0
    for char in value:
        print(ord(char))
        sum_of_chars += ord(char)
 
    return sum_of_chars % 10
def contains(name):
    index = hash_function(name)
    print(index)
    return my_hash_set[index] == name
 
print("'Siri' is in the Hash Set:",contains('Siri'))