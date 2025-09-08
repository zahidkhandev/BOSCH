from collections import Counter

f = open("file.txt", "r")
read_file  = f.read()
words_list = read_file.split(" ")


def count_word_frequency(input_list):
    frequency = Counter(input_list)
    return frequency

word_freq = count_word_frequency(words_list)
print(word_freq)