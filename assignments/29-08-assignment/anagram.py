def anagram(s1, s2):
    return sorted(s1.lower()) == sorted(s2.lower())

string1 = "Listen"
string2 = "Silent"
if anagram(string1, string2):
    print("The strings are anagrams.")
else:
    print("The strings are not anagrams.")