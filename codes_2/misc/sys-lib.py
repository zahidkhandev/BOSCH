import sys
 
def reverseArray(A):
 
    # Reverse the list and return it
 
    return A[::-1]
 
  
input = sys.stdin.read
data = input().split()
N = int(data[0])  # Read the number of integers
print(data)
A = list(map(int, data[1:]))  # Read the space-separated integers into a list
reversed_array = reverseArray(A) # Reverse the array
print(reversed_array)
print(' '.join(map(str, reversed_array))) 