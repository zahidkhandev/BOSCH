from collections import Counter

def count_element_frequency(input_list):
    frequency = Counter(input_list)
    return frequency

my_list = [1, 2, 2, 3, 1, 4, 2, 5, 3, 1]
element_frequencies = list(count_element_frequency(my_list))
print(element_frequencies)