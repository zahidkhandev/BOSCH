def rotateLeft(arr, d):
    n = len(arr)
    for i in range (d):
        first = arr[0]

        for j in range (n-1):
            arr [j] = arr[j+1]
        
        arr[n-1] = first
    return arr


input_arr = list(map(int, input("Enter an array: ").split()))
distance = int(input("Enter a integer d to shift left: "))
print("Left rotation:" , rotateLeft(input_arr, distance))