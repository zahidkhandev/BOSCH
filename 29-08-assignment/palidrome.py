str = input("Enter a str to check palidrome: ")
rev_str = str[::-1]

if rev_str == str:
    print("Palidrome")
else:
    print("not a palindrome")
