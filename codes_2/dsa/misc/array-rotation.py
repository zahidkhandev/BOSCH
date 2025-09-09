arr = list(map(int, input("Enter the array of elements: ").split()))

d = int(input("Enter the dimension of rotation: "))

n = len(arr)

def leftRotation(arr, d):
    for i in range (d):
        first = arr[0]

        for j in range (n-1):
            arr [j] = arr[j+1]
        
        arr[n-1] = first
    return arr

def rightRotation(arr, d):
    for i in range (d):
        last = arr[-1]

        for j in range (n - 1, 0, -1):
            arr [j] = arr[j-1]
        
        arr[0] = last
    return arr

arr_copy = arr[:] 
print(leftRotation(arr, d))
print(rightRotation(arr_copy, d))