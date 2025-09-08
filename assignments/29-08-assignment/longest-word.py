def find_longest_word(sentence):
    words = sentence.split()  
    if not words:
        return ""
    longest_word = max(words, key=len)
    return longest_word

sentence = "test sentence to try it out"
longest_word = find_longest_word(sentence)
print(f"Longest word: '{longest_word}'")