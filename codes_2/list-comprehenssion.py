# Like List Comprehension, Python allows dictionary comprehensions. We can create dictionaries using simple expressions. A dictionary comprehension takes the form {key: value for (key, value) in iterable}
	
# Python code to demonstrate dictionary 
# comprehension
	
# Lists to represent keys and values
keys = ['a','b','c','d','e']
values = [1,2,3,4,5]  
	
# but this line shows dict comprehension here  
myDict = { k:v for (k,v) in zip(keys, values)}  
	
# We can use below too
# myDict = dict(zip(keys, values))  
	
print (myDict)



# fruits = ["apple", "banana", "cherry", "kiwi", "mango"]
# newlist = []
	 
# for x in fruits:
# 	 if "a" in x:
# 	   newlist.append(x)
	
# print(newlist) 

fruits = ["apple", "banana", "cherry", "kiwi", "mango"]
	
newlist = [x for x in fruits if "a" in x]
	
print(newlist) 
	
