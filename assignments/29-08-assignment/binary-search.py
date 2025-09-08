def binary_search_recursive(arr, target, low, high):
    if low > high:
        return -1

    mid = low + (high - low) // 2

    if arr[mid] == target:
        return mid
    elif arr[mid] < target:
        return binary_search_recursive(arr, target, mid + 1, high)
    else:
        return binary_search_recursive(arr, target, low, mid - 1)

def binary_search(arr, target):
    return binary_search_recursive(arr, target, 0, len(arr) - 1)

list = [1,2, 22, 44, 12, 6, 7, 3, 4, 5]
list.sort()
element = 22

print(binary_search(list, element))