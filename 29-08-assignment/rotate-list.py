def rotate_list(lst, k):
    n = len(lst)
    if n == 0:
        return lst
    
    k = k % n
    
    rotated_part = lst[n - k:]
    remaining_part = lst[:n - k]
    
    return rotated_part + remaining_part

my_list = [1, 2, 3, 4, 5, 6, 7]
k_positions = 3
rotated_my_list = rotate_list(my_list, k_positions)
print(rotated_my_list)

another_list = ['a', 'b', 'c', 'd']
k_positions_2 = 1
rotated_another_list = rotate_list(another_list, k_positions_2)
print(rotated_another_list)